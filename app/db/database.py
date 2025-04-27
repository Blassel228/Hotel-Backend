from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core import settings

engine = create_async_engine(
    settings.db.url,
    future=True,
    echo=False,
    pool_recycle=settings.db.POOL_RECYCLE,
    pool_pre_ping=True,
    pool_size=settings.db.POOL_SIZE,
    max_overflow=settings.db.MAX_OVERFLOW,
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
