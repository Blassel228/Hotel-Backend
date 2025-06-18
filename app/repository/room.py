from typing import Sequence

from sqlalchemy import select
from app.models import Room
from app.repository.base import SQLAlchemyRepository


class RoomRepository(SQLAlchemyRepository):
    model = Room

    async def get_by_capacity(
            self,
            capacity: int
    ) -> Sequence[Room]:

        statement = (
            select(self.model)
            .where(self.model.capacity >= capacity)
        )
        return await self.execute(statement=statement, action=lambda result: result.scalars().all())

