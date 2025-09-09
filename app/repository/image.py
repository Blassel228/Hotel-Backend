from app.models import Image
from app.repository.base import SQLAlchemyRepository


class ImageRepository(SQLAlchemyRepository):
    model = Image
