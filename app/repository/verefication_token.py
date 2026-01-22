from app.models import VerificationToken
from app.repository.base import SQLAlchemyRepository


class VerificationTokenRepository(SQLAlchemyRepository):
    model = VerificationToken
