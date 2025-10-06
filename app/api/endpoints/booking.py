from fastapi import APIRouter

from app.api.dependencies import booking_service, UnitOfWorkDep, get_current_user

router = APIRouter()


@router.put("/cancel_booking/{id}")
async def update_to_cancel_status(id: str, unit_of_work: UnitOfWorkDep, service: booking_service):
    return await service.cancel_booking(unit_of_work=unit_of_work, id=id)


@router.get("/get_bookings_for_one_user")
async def get_bookings_for_one_user(
    current_user: get_current_user, unit_of_work: UnitOfWorkDep, service: booking_service
):
    return await service.get_bookings_for_one_user(user_id=current_user.id, unit_of_work=unit_of_work)


@router.get("/get_one/{booking_id}")
async def get_bookings_for_one_user(booking_id: str, unit_of_work: UnitOfWorkDep, service: booking_service):
    return await service.get_one(booking_id=booking_id, unit_of_work=unit_of_work)


@router.get("/get_bookings_for_rooms_not_rated_by_user")
async def get_bookings_for_rooms_not_rated_by_user(current_user: get_current_user, service: booking_service, unit_of_work: UnitOfWorkDep):
    return await service.get_bookings_for_rooms_not_rated_by_user(unit_of_work=unit_of_work, user_id=current_user.id)

