from app.models import Booking
from app.repository.base import SQLAlchemyRepository


class BookingRepository(SQLAlchemyRepository):
    model = Booking
