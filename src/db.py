import logging
from collections.abc import Generator
from contextlib import contextmanager

from fastapi import HTTPException
from sqlalchemy import MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from sqlmodel import Session

from config.config import settings

from src.json import json

DB_NAMING_CONVENTION = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()]
    ),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": ("fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s"),
    "pk": "pk__%(table_name)s",
}

logger = logging.getLogger(__name__)

metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

engine = create_engine(
    settings.DB_URL,
    echo=False,
    future=True,
    json_serializer=json.dumps,
    json_deserializer=json.loads,
    pool_size=32,
    pool_timeout=10,
    pool_recycle=60 * 2,
    max_overflow=5,
    pool_pre_ping=True,
)

session_maker = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=True,
)


def get_session() -> Generator[Session, None]:
    try:
        with session_maker() as session:
            try:
                yield session
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
    except SQLAlchemyError as e:
        logger.error(f"DB Error {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": 500,
                "msg": "Ошибка доступа к Базе данные",
                "detail": str(e),
            },
        ) from e


@contextmanager
def get_transactional_session() -> Generator[Session, None, None]:
    session = session_maker()
    try:
        session.begin()
        yield session
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction rollback due to error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": 500,
                "msg": "Ошибка транзакции с Базой данных",
                "detail": str(e),
            },
        ) from e
    finally:
        session.close()
