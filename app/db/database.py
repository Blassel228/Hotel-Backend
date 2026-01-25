from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core import settings

engine = create_async_engine(
    settings.db.url,
    future=True,
    echo=False,
    pool_recycle=settings.db.POOL_RECYCLE,
    pool_pre_ping=True,
    poolclass=NullPool,
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
