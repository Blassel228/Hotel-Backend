from app.utils.unitofwork import UnitOfWork


class PropertyService:
    async def get_all(self, unit_of_work: UnitOfWork):
        async with unit_of_work:
            return await unit_of_work.property.get_multi()
