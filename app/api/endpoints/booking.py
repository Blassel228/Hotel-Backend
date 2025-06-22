from fastapi import APIRouter

from app.api.dependencies import booking_service, UnitOfWorkDep, get_current_user
from app.schemas.booking import CreateBookingIn
from app.schemas.guest import GuestCreateIn

router = APIRouter()


@router.post("")
async def create(
    booking: CreateBookingIn, guest: GuestCreateIn, service: booking_service, unit_of_work: UnitOfWorkDep, current_user:get_current_user
):
    return await service.create(booking, guest, unit_of_work, current_user.id)
