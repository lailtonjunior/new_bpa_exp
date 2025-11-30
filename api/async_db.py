from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import get_db_settings

_engine = None
_SessionLocal = None


def _get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        settings = get_db_settings()
        url = (
            f"postgresql+asyncpg://{settings['db_user']}:{settings['db_password']}"
            f"@{settings['db_host']}:{settings['db_port']}/{settings['db_name']}"
        )
        _engine = create_async_engine(url, future=True, echo=False)
        _SessionLocal = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
    return _engine, _SessionLocal


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    _, session_factory = _get_engine()
    async with session_factory() as session:
        yield session


async def dispose_engine():
    if _engine:
        await _engine.dispose()
