from app.schemas.guest import GuestCreateIn
from app.utils.unitofwork import UnitOfWork


class GuestService:
    async def create(self, guest: GuestCreateIn, unit_of_work: UnitOfWork):
        async with unit_of_work:
            return await unit_of_work.booking.create(guest)
