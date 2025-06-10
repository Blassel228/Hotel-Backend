from app.utils.unitofwork import UnitOfWork


class RoomService:
    async def get_all(self, unit_of_work: UnitOfWork, offset: int = 0, limit: int = None):
        async with unit_of_work:
            return await unit_of_work.room.get_multi(offset=offset, limit=limit)
