from app.models.refresh_token import RefreshToken
from app.repository.base import SQLAlchemyRepository


class RefreshTokenRepository(SQLAlchemyRepository):
    model = RefreshToken
