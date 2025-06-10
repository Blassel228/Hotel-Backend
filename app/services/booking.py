from app.schemas.booking import CreateBooking, CreateBookingIn
from app.utils.unitofwork import UnitOfWork


class BookingService:
    async def create(self, booking: CreateBookingIn, unit_of_work: UnitOfWork, user_id: int):
        duration = (booking.end_date - booking.start_date).days
        async with unit_of_work:
            room = await unit_of_work.room.get_one(id=booking.room_id)
        price = room.price * duration
        booking = CreateBooking(**booking.model_dump(), status="completed", user_id=user_id, price=price)
        async with unit_of_work:
            return await unit_of_work.booking.create(booking)
