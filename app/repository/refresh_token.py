from datetime import datetime

from sqlalchemy import delete, update

from app.models.refresh_token import RefreshToken
from app.repository.base import SQLAlchemyRepository


class RefreshTokenRepository(SQLAlchemyRepository):
    model = RefreshToken

    async def delete_expired(self, cutoff: datetime) -> None:
        stmt = delete(RefreshToken).where(RefreshToken.expires_at < cutoff)
        await self.execute(stmt)


    async def revoke_all_for_user_except(self, user_id: str, exclude_token_id: int):
        query = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.id != exclude_token_id,
                RefreshToken.revoked.is_(False)
            )
            .values(revoked=True, used=True)
        )
        await self.session.execute(query)


    async def revoke_all_for_user(self, user_id: str):
        query = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(revoked=True, used=True)
        )
        await self.session.execute(query)