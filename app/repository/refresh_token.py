from app.models.RefreshToken import RefreshToken
from app.repository.base import SQLAlchemyRepository


class RefreshTokenRepository(SQLAlchemyRepository):
    model = RefreshToken
