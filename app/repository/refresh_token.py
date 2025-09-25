from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, update

from app.models.refresh_token import RefreshToken
from app.repository.base import SQLAlchemyRepository


class RefreshTokenRepository(SQLAlchemyRepository):
    model = RefreshToken

    async def delete_expired(self, cutoff: datetime) -> None:
        stmt = delete(RefreshToken).where(RefreshToken.expires_at < cutoff)
        await self.execute(stmt)

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        stmt = update(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False,
            RefreshToken.used == False
        ).values(revoked=True, used=True)
        await self.execute(stmt)
