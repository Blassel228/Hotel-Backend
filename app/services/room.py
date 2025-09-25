from datetime import datetime
from typing import Sequence

from app.models import Room
from app.utils.unitofwork import UnitOfWork


class RoomService:
    async def get_one(self, unit_of_work: UnitOfWork, room_id: str):
        async with unit_of_work:
            return await unit_of_work.room.get_one(id=room_id)

    async def get_all(self, unit_of_work: UnitOfWork, offset: int = 0, limit: int = None) -> Sequence[Room]:
        async with unit_of_work:
            return await unit_of_work.room.get_multi(offset=offset, limit=limit)

    async def search(
        self,
        unit_of_work: UnitOfWork,
        start_date: datetime,
        end_date: datetime,
        capacity: int = 1,
    ) -> Sequence[Room]:
        result = []

        async with unit_of_work:
            rooms = await unit_of_work.room.get_by_capacity(capacity=capacity)

        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        for room in rooms:
            if not room.bookings:
                result.append(room)
            for booking in room.bookings:
                if (booking.start_date <= start_datetime <= booking.end_date) or (
                    booking.start_date <= end_datetime <= booking.end_date
                ):
                    continue
                else:
                    result.append(room)
                    print(result)
        return result
