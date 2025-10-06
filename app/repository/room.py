from typing import Sequence

from sqlalchemy import select, exists

from app.models import Room, Booking, Rating
from app.repository.base import SQLAlchemyRepository


class RoomRepository(SQLAlchemyRepository):
    model = Room

    async def get_by_capacity(self, capacity: int) -> Sequence[Room]:
        statement = select(self.model).where(self.model.capacity >= capacity)
        return await self.execute(statement=statement, action=lambda result: result.scalars().all())

    async def get_rooms_booked_not_rated_by_user(self, user_id: str) -> Sequence[Room]:
        """
        Get rooms that were booked by the given user but not yet rated by them.
        """
        rating_exists = exists().where(
            Rating.user_id == user_id,
            Rating.room_id == Room.id
        )

        statement = (
            select(Room)
            .join(Booking, Booking.room_id == Room.id)
            .where(
                Booking.user_id == user_id,
                ~rating_exists
            )
            .distinct()
        )

        statement = self.add_loading_options(statement)

        return await self.execute(
            statement=statement,
            action=lambda result: result.unique().scalars().all()
        )
