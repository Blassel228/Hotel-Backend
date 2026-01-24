from app.core.exc.booking import PermissionDeniedException, BookingConflictException
from app.enums.booking_status import BookingStatus
from app.models import Booking
from app.schemas.booking import CreateBooking, CreateBookingIn, UpdateBooking
from app.utils.unitofwork import UnitOfWork


class BookingService:
    async def get_one(self, booking_id: str, unit_of_work: UnitOfWork):
        async with unit_of_work:
            return await unit_of_work.booking.get_one(id=booking_id)

    async def get_all(self, unit_of_work: UnitOfWork):
        async with unit_of_work:
            return await unit_of_work.booking.get_multi()

    async def update(self, booking_id: str, booking: UpdateBooking, unit_of_work: UnitOfWork):
        if booking.start_date.tzinfo is not None:
            booking.start_date = booking.start_date.replace(tzinfo=None)
        if booking.end_date.tzinfo is not None:
            booking.end_date = booking.end_date.replace(tzinfo=None)

        async with unit_of_work:
            await unit_of_work.booking.update(booking.model_dump(), id=booking_id)
            return await unit_of_work.booking.get_one(id=booking_id)

    async def delete(self, booking_id: str, unit_of_work: UnitOfWork):
        async with unit_of_work:
            return await unit_of_work.booking.delete(id=booking_id)

    async def cancel_booking(self, id: str, unit_of_work: UnitOfWork, current_user_id: int | None = None):
        async with unit_of_work:
            booking = await unit_of_work.booking.get_one(id=id)

            if current_user_id is not None and booking.user_id != current_user_id:
                raise PermissionDeniedException()

            if booking.status == BookingStatus.CANCELLED.value:
                raise BookingConflictException(action="cancelled", detail="Booking is already cancelled")
            if booking.status == BookingStatus.COMPLETED.value:
                raise BookingConflictException(action="cancelled", detail="Completed booking cannot be cancelled")

            await unit_of_work.booking.update({"status": BookingStatus.CANCELLED.value}, id=id)
            return await unit_of_work.booking.get_one(id=id)

    async def create_with_token(self, booking_in: CreateBookingIn, unit_of_work: UnitOfWork, user_id: int) -> Booking:
        async with unit_of_work:
            booking_data = CreateBooking(**booking_in.model_dump(), user_id=user_id)
            created_booking = await unit_of_work.booking.create(booking_data)
        return created_booking

    async def get_bookings_for_one_user(self, user_id: str, unit_of_work: UnitOfWork):
        async with unit_of_work:
            bookings = await unit_of_work.booking.get_multi(user_id=user_id)
        return bookings

    async def get_bookings_for_rooms_not_rated_by_user(self, user_id: str, unit_of_work: UnitOfWork):
        async with unit_of_work:
            return await unit_of_work.booking.get_bookings_for_rooms_not_rated_by_user(user_id=user_id)
