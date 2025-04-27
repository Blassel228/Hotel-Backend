from app.models import User
from app.repository.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User
