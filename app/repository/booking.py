from sqlalchemy import Sequence, exists, select

from app.models import Booking, Review
from app.repository.base import SQLAlchemyRepository


class BookingRepository(SQLAlchemyRepository):
    model = Booking

    join_load_list = [Booking.room]

    async def get_bookings_for_rooms_not_rated_by_user(self, user_id: str) -> Sequence[Booking]:
        """
        Get bookings of the given user that do NOT have a review yet.
        """
        rating_exists = exists().where(Review.booking_id == Booking.id)

        statement = select(Booking).where(
            Booking.user_id == user_id,
            ~rating_exists
        ).distinct()

        statement = self.add_loading_options(statement)
        return await self.execute(statement=statement, action=lambda result: result.unique().scalars().all())