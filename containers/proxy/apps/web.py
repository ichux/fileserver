import base64
import os
import re
import shutil
import tempfile
import urllib.parse
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path

import bcrypt
import jwt
from apps import SECRET_KEY, TOKEN_EXPIRY_MINUTES, UPLOAD_DIR, lifespan
from apps.models import User
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route


class XAccelRedirectResponse(Response):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers["X-Accel-Redirect"] = path

        # necessary
        del self.headers["content-type"]


def sanitize_filename(filename: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", Path(filename).name)


def basic_auth_required(func):
    """Decorator to require Basic Auth and verify credentials"""

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        auth = request.headers.get("Authorization")

        if not auth or not auth.startswith("Basic "):
            return Response(
                "Missing or invalid Basic Auth",
                status_code=401,
                headers={"WWW-Authenticate": "Basic"},
            )

        encoded_credentials = auth.replace("Basic ", "")
        try:
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            username, password = decoded_credentials.split(":", 1)
        except (Exception,):
            return Response("Invalid Basic Auth format", status_code=401)

        if not verify_user(request, username, password):
            return Response("Invalid credentials or user is disabled", status_code=403)

        return await func(request, *args, **kwargs)

    return wrapper


def verify_user(request, username, password):
    """Verify user credentials from the database."""
    user = request.state.session.query(User).filter(User.username == username).first()

    request.state.session.add(user)
    request.state.session.commit()

    if not user or not user.enabled:
        return False
    return bcrypt.checkpw(password.encode(), user.password_hash.encode())


async def get_file(request: Request):
    token = request.query_params.get("token")
    filepath = request.path_params["filepath"]

    if not token:
        return Response("Token is required", status_code=401)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # Decode the base64-encoded route from the token
        encoded_route = payload.get("route")
        if not encoded_route:
            return Response("Invalid token payload", status_code=403)

        try:
            decoded_filepath = urllib.parse.unquote(encoded_route)
        except (Exception,):
            return Response("Malformed token route encoding", status_code=403)

        # Validate the decoded filepath against the request's filepath
        if decoded_filepath != filepath:
            return Response(
                f"Invalid token for this route: {decoded_filepath} | {filepath}",
                status_code=403,
            )
    except jwt.ExpiredSignatureError:
        return Response("Token has expired", status_code=401)
    except jwt.PyJWTError:
        return Response("Invalid token", status_code=401)

    if not (UPLOAD_DIR / filepath).exists():
        return Response("Not found", status_code=404)
    return XAccelRedirectResponse(f"/offloads/{filepath}")


@basic_auth_required
async def generate_token(request: Request):
    """Endpoint to generate JWT after verifying Basic Auth"""
    filepath = request.query_params.get("filepath")
    if not filepath:
        return Response("Missing filepath parameter", status_code=400)

    return Response(
        jwt.encode(
            {
                "route": urllib.parse.quote(filepath),
                "exp": datetime.now(timezone.utc)
                + timedelta(minutes=TOKEN_EXPIRY_MINUTES),
            },
            SECRET_KEY,
            algorithm="HS256",
        ),
        status_code=200,
    )


@basic_auth_required
async def push_file(request: Request):
    form = await request.form()

    if "file" not in form:
        return Response("No file uploaded", status_code=400)

    file = form["file"]

    if sanitize_filename(file.filename) != file.filename:
        return Response("Invalid filename", status_code=400)

    # Create a temporary file on disk
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        while chunk := await file.read(8192):
            temp_file.write(chunk)

        temp_file_path = temp_file.name

    dest_path = UPLOAD_DIR / file.filename
    shutil.move(temp_file_path, dest_path)

    # Set the file permissions to -rw-rw-r-- (0o664)
    os.chmod(dest_path, 0o664)
    return Response("success", status_code=200)


app = Starlette(
    routes=[
        Route("/{filepath:path}", get_file),
        Route("/generate-token", generate_token, methods=["POST"]),
        Route("/upload", push_file, methods=["POST"]),
    ],
    lifespan=lifespan,
)
