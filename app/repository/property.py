from app.models import Property
from app.repository.base import SQLAlchemyRepository


class PropertyRepository(SQLAlchemyRepository):
    model = Property
