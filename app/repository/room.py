from app.models import Room
from app.repository.base import SQLAlchemyRepository


class RoomRepository(SQLAlchemyRepository):
    model = Room
