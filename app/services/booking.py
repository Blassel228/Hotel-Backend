from app.models import Booking
from app.schemas.booking import CreateBooking, CreateBookingIn
from app.schemas.guest import GuestCreateIn, GuestCreate
from app.utils.unitofwork import UnitOfWork


class BookingService:
    async def create(self, booking: CreateBookingIn, guest: GuestCreateIn, unit_of_work: UnitOfWork, user_id: int) -> Booking:
        booking = CreateBooking(**booking.model_dump(), user_id=user_id)
        async with unit_of_work:
            created_booking = await unit_of_work.booking.create(booking)
            await unit_of_work.guest.create(GuestCreate(**guest.model_dump(), booking_id=created_booking.id))
        return created_booking