from app.schemas.rating import RatingCreate, RatingCreateIn, RatingAverageGet
from app.utils.unitofwork import UnitOfWork


class RatingService:
    async def create(self, unit_of_work: UnitOfWork, rating: RatingCreateIn, user_id: str):
        rating = RatingCreate(**rating.model_dump(), user_id=user_id)
        async with unit_of_work:
            updated_rating = await unit_of_work.rating.create(rating)
            average_rating = round(await unit_of_work.rating.get_average_rating(room_id=rating.room_id), 1)
            await unit_of_work.room.update({"average_rating": average_rating}, id=rating.room_id)
            return updated_rating

    async def get_average_rating(self, unit_of_work: UnitOfWork, room_id: str):
        async with unit_of_work:
            stars = await unit_of_work.rating.get_average_rating(room_id=room_id)
            return RatingAverageGet(room_id=room_id, stars=stars)

    async def get_average_ratings(self, unit_of_work: UnitOfWork):
        async with unit_of_work:
            ratings = await unit_of_work.rating.get_average_ratings()
            return [RatingAverageGet(room_id=rating["room_id"], stars=rating["stars"]) for rating in ratings]
