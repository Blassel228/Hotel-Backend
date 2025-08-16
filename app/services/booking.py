from app.models import Booking
from app.schemas.booking import CreateBooking, CreateBookingIn
from app.schemas.guest import GuestCreateIn, GuestCreate
from app.utils.unitofwork import UnitOfWork


class BookingService:
    async def create_with_token(
        self, booking_in: CreateBookingIn, guest_in: GuestCreateIn, unit_of_work: UnitOfWork, user_id: int
    ) -> Booking:
        async with unit_of_work:
            guest_data = GuestCreate(**guest_in.model_dump())
            created_guest = await unit_of_work.guest.create(guest_data)
            booking_data = CreateBooking(**booking_in.model_dump(), user_id=user_id, guest_id=created_guest.id)
            created_booking = await unit_of_work.booking.create(booking_data)
        return created_booking

    async def create_without_token(
        self, booking_in: CreateBookingIn, guest_in: GuestCreateIn, unit_of_work: UnitOfWork
    ):
        async with unit_of_work:
            guest_data = GuestCreate(**guest_in.model_dump())
            created_guest = await unit_of_work.guest.create(guest_data)
            booking_data = CreateBooking(**booking_in.model_dump(), guest_id=created_guest.id)
            created_booking = await unit_of_work.booking.create(booking_data)
        return created_booking
