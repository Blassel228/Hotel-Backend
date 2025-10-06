from sqlalchemy import Sequence, exists, select

from app.models import Booking, Rating
from app.repository.base import SQLAlchemyRepository


class BookingRepository(SQLAlchemyRepository):
    model = Booking

    join_load_list = [Booking.room]

    async def get_bookings_for_rooms_not_rated_by_user(self, user_id: str) -> Sequence[Booking]:
        """
        Get bookings of the given user for rooms that the user has NOT rated yet.
        """
        rating_exists = exists().where(
            Rating.user_id == user_id,
            Rating.room_id == self.model.room_id
        )

        statement = (
            select(self.model)
            .where(
                self.model.user_id == user_id,
                ~rating_exists
            )
            .distinct()
        )

        statement = self.add_loading_options(statement)
        return await self.execute(
            statement=statement,
            action=lambda result: result.unique().scalars().all()
        )