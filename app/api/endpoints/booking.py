from fastapi import APIRouter

from app.api.dependencies import booking_service, UnitOfWorkDep, get_current_user
from app.schemas.booking import UpdateBooking

router = APIRouter()


@router.get("/", summary="Get all bookings")
async def get_all(unit_of_work: UnitOfWorkDep, service: booking_service):
    return await service.get_all(unit_of_work=unit_of_work)


@router.get("/my", summary="Get all bookings for the current user")
async def get_user_bookings(current_user: get_current_user, unit_of_work: UnitOfWorkDep, service: booking_service):
    return await service.get_bookings_for_one_user(user_id=current_user.id, unit_of_work=unit_of_work)


@router.get("/unrated", summary="Get bookings for rooms not yet rated by the user")
async def get_unrated_bookings(current_user: get_current_user, service: booking_service, unit_of_work: UnitOfWorkDep):
    return await service.get_bookings_for_rooms_not_rated_by_user(unit_of_work=unit_of_work, user_id=current_user.id)


@router.get("/{booking_id}", summary="Get a booking by ID")
async def get_booking(booking_id: str, unit_of_work: UnitOfWorkDep, service: booking_service):
    return await service.get_one(booking_id=booking_id, unit_of_work=unit_of_work)


@router.put("/{booking_id}", summary="Update a booking")
async def update(booking_id: str, unit_of_work: UnitOfWorkDep, service: booking_service, booking: UpdateBooking):
    return await service.update(unit_of_work=unit_of_work, booking_id=booking_id, booking=booking)


@router.put("/{booking_id}/cancel", summary="Cancel a booking by ID")
async def cancel_booking(booking_id: str, unit_of_work: UnitOfWorkDep, service: booking_service):
    return await service.cancel_booking(unit_of_work=unit_of_work, id=booking_id)


@router.delete("/{booking_id}", summary="Delete a booking")
async def delete(booking_id: str, unit_of_work: UnitOfWorkDep, service: booking_service):
    return await service.delete(unit_of_work=unit_of_work, booking_id=booking_id)
