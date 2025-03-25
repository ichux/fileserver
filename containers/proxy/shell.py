import asyncio
import os

from apps import SessionLocal
from apps.web import app
from IPython import embed
from starlette.config import Config

config = Config()
config.file_values = {key: value for key, value in os.environ.items()}

embed(
    banner1="Fileserver Interactive Shell\n"
    "Available variables: app, config, asyncio, SessionLocal\n",
    user_ns={
        "app": app,
        "config": config,
        "asyncio": asyncio,
        "SessionLocal": SessionLocal,
    },
)


# In [1]: from apps.models import User
#
# In [2]: with SessionLocal() as session:
#    ...:     data = session.query(User).filter(User.username == 'username').first()
