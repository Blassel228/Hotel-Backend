import functools
from abc import ABC, abstractmethod
from typing import Any

from loguru import logger
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core import settings
from app.db.database import async_session
from app.repository import RefreshTokenRepository, RatingRepository
from app.repository import RefundRepository
from app.repository.booking import BookingRepository
from app.repository.guest import GuestRepository
from app.repository.image import ImageRepository
from app.repository.room import RoomRepository
from app.repository.user import UserRepository


class ABCUnitOfWork(ABC):
    session: AsyncSession

    user: UserRepository
    booking: BookingRepository
    room: RoomRepository
    guest: GuestRepository
    image: ImageRepository
    refund: RefundRepository
    refresh_token: RefreshTokenRepository
    rating: RatingRepository

    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, *args: Any) -> None:
        raise NotImplementedError


class UnitOfWork(ABCUnitOfWork):
    def __init__(self) -> None:
        self.session_maker = async_session

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self.session_maker()

        # Repository classes
        self.user = UserRepository(self.session)
        self.booking = BookingRepository(self.session)
        self.room = RoomRepository(self.session)
        self.guest = GuestRepository(self.session)
        self.image = ImageRepository(self.session)
        self.refund = RefundRepository(self.session)
        self.refresh_token = RefreshTokenRepository(self.session)
        self.rating = RatingRepository(self.session)

        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if exc:
            logger.exception("An error occurred while processing the request. Rolling back. Error: {exc}", exc=exc)
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()
        await logger.complete()

        if exc:
            raise exc


@functools.lru_cache
def get_sessionmaker_without_pool() -> async_sessionmaker:
    engine = create_async_engine(settings.db.url, poolclass=NullPool)
    return async_sessionmaker(bind=engine, autoflush=False)


class UnitOfWorkNoPool(UnitOfWork):
    def __init__(self) -> None:
        super().__init__()
        self.session_maker = get_sessionmaker_without_pool()
