import base64
from datetime import datetime
from typing import Sequence

from starlette.requests import Request

from app.models import Room
from app.schemas.room import RoomFilterParams, RoomUpdate, RoomCreate, RoomCreateIn, RoomUpdateIn
from app.utils.unitofwork import UnitOfWork


class RoomService:
    async def get_one(self, unit_of_work: UnitOfWork, room_id: str):
        async with unit_of_work:
            return await unit_of_work.room.get_one(id=room_id)

    async def get_all(self, unit_of_work: UnitOfWork, offset: int = 0, limit: int = None) -> Sequence[Room]:
        async with unit_of_work:
            return await unit_of_work.room.get_multi(offset=offset, limit=limit)

    async def create(self, unit_of_work: UnitOfWork, room: RoomCreateIn, image: bytes):
        image = base64.b64encode(image).decode("utf-8")
        room = RoomCreate(**room.model_dump(), image=image)
        async with unit_of_work:
            return await unit_of_work.room.create(room)

    async def get_with_filters(self, unit_of_work: UnitOfWork, filters: RoomFilterParams):
        filter_dict = {k: v for k, v in filters.__dict__.items() if v is not None}
        lowest_price = filter_dict.pop("lowest_price", 0)
        greatest_price = filter_dict.pop("greatest_price", None)
        async with unit_of_work:
            rooms = await unit_of_work.room.get_multi(**filter_dict)
        if lowest_price and greatest_price:
            rooms = [room for room in rooms if lowest_price < room.price < greatest_price]
        return rooms

    async def update(self, unit_of_work: UnitOfWork, room_id: str, room: RoomUpdateIn):
        room_data = room.model_dump(exclude_none=True)

        image_b64 = room_data.pop("image", None)

        if image_b64 is not None:
            room_data["image"] = image_b64

        room_update = RoomUpdate(**room_data)

        async with unit_of_work:
            return await unit_of_work.room.update(room_update.model_dump(exclude_none=True), id=room_id)

    async def delete(self, unit_of_work: UnitOfWork, room_id: str):
        async with unit_of_work:
            return await unit_of_work.room.delete(id=room_id)

    async def search(
        self,
        unit_of_work: UnitOfWork,
        start_date: datetime,
        end_date: datetime,
        capacity: int = 1,
    ) -> Sequence[Room]:
        async with unit_of_work:
            return await unit_of_work.room.get_available_in_period(
                start_date=start_date, end_date=end_date, capacity=capacity
            )

    async def get_rooms_booked_not_rated_by_user(self, unit_of_work: UnitOfWork, user_id: str):
        async with unit_of_work:
            return await unit_of_work.room.get_rooms_booked_not_rated_by_user(user_id=user_id)
