from datetime import datetime
from typing import Sequence

from sqlalchemy import select, and_, not_, exists

from app.enums.booking_status import BookingStatus
from app.models import Review
from app.models import Room, Booking
from app.repository.base import SQLAlchemyRepository


class RoomRepository(SQLAlchemyRepository):
    model = Room

    async def get_by_capacity(self, capacity: int) -> Sequence[Room]:
        statement = select(self.model).where(self.model.capacity >= capacity)
        return await self.execute(statement=statement, action=lambda result: result.scalars().all())

    async def get_rooms_booked_not_rated_by_user(self, user_id: str) -> Sequence[Room]:
        rating_exists = exists().where(Review.user_id == user_id, Review.room_id == Room.id)

        statement = (
            select(Room)
            .join(Booking, Booking.room_id == Room.id)
            .where(Booking.user_id == user_id, ~rating_exists)
            .distinct()
        )

        statement = self.add_loading_options(statement)

        return await self.execute(statement=statement, action=lambda result: result.unique().scalars().all())

    async def get_available_in_period(
        self,
        start_date: datetime,
        end_date: datetime,
        capacity: int = 1,
    ) -> Sequence[Room]:
        overlapping_booking = exists().where(
            and_(
                Booking.room_id == Room.id,
                Booking.status != BookingStatus.CANCELLED.value,
                Booking.start_date <= end_date,
                Booking.end_date >= start_date,
            )
        )

        statement = select(Room).where(Room.capacity >= capacity, not_(overlapping_booking))

        statement = self.add_loading_options(statement)

        result = await self.execute(statement=statement, action=lambda r: r.unique().scalars().all())
        return result
