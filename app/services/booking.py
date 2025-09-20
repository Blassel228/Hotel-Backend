from app.enums.booking_status import BookingStatus
from app.models import Booking
from app.schemas.booking import CreateBooking, CreateBookingIn
from app.schemas.guest import GuestCreateIn, GuestCreate
from app.utils.unitofwork import UnitOfWork


class BookingService:
    async def cancel_booking(self, id: str, unit_of_work: UnitOfWork):
        async with unit_of_work:
            await unit_of_work.booking.update({"status": BookingStatus.CANCELLED.value}, id=id)
            return await unit_of_work.booking.get_one(id=id)

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

    async def get_bookings_for_one_user(self, user_id: str, unit_of_work: UnitOfWork):
        async with unit_of_work:
            return await unit_of_work.booking.get_multi(user_id=user_id)
