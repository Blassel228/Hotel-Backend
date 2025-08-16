from fastapi import APIRouter

from app.api.dependencies import booking_service, UnitOfWorkDep, get_current_user
from app.schemas.booking import CreateBookingIn
from app.schemas.guest import GuestCreateIn

router = APIRouter()


@router.post("/create_booking_with_token")
async def create(
    booking_in: CreateBookingIn,
    guest_in: GuestCreateIn,
    service: booking_service,
    unit_of_work: UnitOfWorkDep,
    current_user: get_current_user,
):
    return await service.create_with_token(booking_in, guest_in, unit_of_work, current_user.id)

@router.post("/create_booking_without_token")
async def create_without_token(
    booking_in: CreateBookingIn,
    guest_in: GuestCreateIn,
    service: booking_service,
    unit_of_work: UnitOfWorkDep,
):
    return await service.create_without_token(booking_in, guest_in, unit_of_work)

