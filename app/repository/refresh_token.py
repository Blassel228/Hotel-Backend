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
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked == False, RefreshToken.used == False)
            .values(revoked=True, used=True)
        )
        await self.execute(stmt)

    async def consume_token(self, token_hash: str, expires_after: datetime) -> bool:
        result = await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
                RefreshToken.used.is_(False),
                RefreshToken.expires_at > expires_after,
            )
            .values(used=True, revoked=True)
        )
        return result.rowcount > 0
