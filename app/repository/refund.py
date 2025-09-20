from app.models import Refund
from app.repository.base import SQLAlchemyRepository


class RefundRepository(SQLAlchemyRepository):
    model = Refund
