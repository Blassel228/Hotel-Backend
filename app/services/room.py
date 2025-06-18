from typing import List, Sequence

from app.models import Room
from app.utils.unitofwork import UnitOfWork
from datetime import date


class RoomService:
    async def get_all(self, unit_of_work: UnitOfWork, offset: int = 0, limit: int = None) -> Sequence[Room]:
        async with unit_of_work:
            return await unit_of_work.room.get_multi(offset=offset, limit=limit)

    async def search(self, unit_of_work: UnitOfWork, start_date: date, end_date: date, capacity: int = 1, ) -> Sequence[Room]:
        result = []

        async with unit_of_work:
            rooms = await unit_of_work.room.get_by_capacity(capacity=capacity)

        for room in rooms:
            if not room.bookings:
                result.append(room)
            for booking in room.bookings:
                if ((booking.start_date <= start_date <= booking.end_date)
                        or (booking.start_date <= end_date<= booking.end_date)):
                    continue
                else:
                    result.append(room)
                    print(result)
        return result
