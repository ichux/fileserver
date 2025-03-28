import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, TypedDict

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from starlette.applications import Starlette

SECRET_KEY = os.getenv("SECRET_KEY")
TOKEN_EXPIRY_MINUTES = int(os.getenv("TOKEN_EXPIRY_MINUTES"))

UPLOAD_DIR = Path("~/offloads").expanduser()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


engine = create_engine(f"sqlite:///{UPLOAD_DIR / ".fs_auth.db"}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class EssentialStatus(TypedDict):
    session: Session


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[EssentialStatus]:
    with SessionLocal() as session:
        yield {"session": session}


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

Base = declarative_base(metadata=MetaData(naming_convention=naming_convention))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
