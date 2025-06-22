from app.models import Guest
from app.repository.base import SQLAlchemyRepository

class GuestRepository(SQLAlchemyRepository):
    model = Guest