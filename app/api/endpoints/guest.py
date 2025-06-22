from fastapi import APIRouter

from app.api.dependencies import guest_service, UnitOfWorkDep
from app.schemas.guest import GuestCreateIn

router = APIRouter()


@router.post("")
async def create(
    guest: GuestCreateIn, service: guest_service, unit_of_work: UnitOfWorkDep
):
    return await service.create(guest, unit_of_work)
