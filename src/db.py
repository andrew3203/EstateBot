import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import HTTPException
from sqlalchemy import MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

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


engine = AsyncEngine(
    create_engine(
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
)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=True,
)  # type: ignore


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()
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


@asynccontextmanager
async def get_transactional_session() -> AsyncGenerator[AsyncSession, None]:
    session = async_session_maker()
    try:
        session.begin()
        yield session
    except Exception as e:
        await session.rollback()
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
        await session.close()
