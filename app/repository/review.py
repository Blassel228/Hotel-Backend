from typing import Any

from sqlalchemy import select, func

from app.models.review import Review
from app.repository.base import SQLAlchemyRepository, PaginateRepositoryMixin


from app.enums import OrderDirection


class ReviewRepository(SQLAlchemyRepository[Review], PaginateRepositoryMixin[Review]):
    model = Review

    async def get_by_room_id(
        self,
        room_id: str,
        *,
        offset: int = 0,
        limit: int | None = None,
        order_by: str = "created_at",
        order_direction: OrderDirection = OrderDirection.DESC,
    ) -> list[Review]:
        """
        Get reviews for a specific room with pagination and sorting.
        """
        # Validate that the column exists
        if not hasattr(self.model, order_by):
            raise ValueError(f"Invalid sort column: {order_by}")

        column = getattr(self.model, order_by)

        # Build query
        statement = select(self.model).where(self.model.room_id == room_id).offset(offset)

        if limit is not None:
            statement = statement.limit(limit)

        if order_direction == OrderDirection.ASC:
            statement = statement.order_by(column.asc())
        else:
            statement = statement.order_by(column.desc())

        statement = self.add_loading_options(statement)
        result = await self.session.execute(statement)
        return list(result.unique().scalars().all())

    async def get_average_rating(self, room_id: str) -> float | None:
        stmt = select(func.avg(self.model.stars)).where(self.model.room_id == room_id)
        result = await self.session.execute(stmt)
        avg = result.scalar()
        return float(avg) if avg is not None else None

    async def get_average_ratings(self) -> list[dict[str, Any]]:
        stmt = select(self.model.room_id, func.avg(self.model.stars).label("stars")).group_by(self.model.room_id)
        result = await self.session.execute(stmt)
        return [{"room_id": row.room_id, "stars": float(row.stars)} for row in result]
