from app.models.rating import Rating
from app.repository.base import SQLAlchemyRepository
from sqlalchemy import select, func


class RatingRepository(SQLAlchemyRepository):
    model = Rating

    async def get_average_rating(self, room_id):
        stmt = select(func.avg(self.model.stars).label("stars")).where(self.model.room_id == room_id)
        result = await self.execute(stmt)
        return result.scalar()

    async def get_average_ratings(self):
        stmt = select(self.model.room_id, func.avg(self.model.stars).label("stars")).group_by(self.model.room_id)
        return await self.execute(stmt, action=lambda result: result.mappings().all())
