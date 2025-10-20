from app.enums import OrderDirection
from app.enums.rating_filters import RatingFilters
from app.schemas.review import ReviewCreate, ReviewCreateIn, ReviewAverageGet
from app.utils.unitofwork import UnitOfWork


class ReviewService:
    async def get_multi(
        self,
        room_id: str,
        unit_of_work: UnitOfWork,
        offset: int = 0,
        limit: int | None = None,
        sort: RatingFilters = RatingFilters.BEST,
    ):
        async with unit_of_work:
            match sort:
                case RatingFilters.BEST:
                    return await unit_of_work.review.get_by_room_id(
                        room_id=room_id,
                        offset=offset,
                        limit=limit,
                        order_by="stars",
                        order_direction=OrderDirection.DESC,
                    )

                case RatingFilters.WORST:
                    return await unit_of_work.review.get_by_room_id(
                        room_id=room_id,
                        offset=offset,
                        limit=limit,
                        order_by="stars",
                        order_direction=OrderDirection.ASC,
                    )

                case RatingFilters.RECENT:
                    return await unit_of_work.review.get_by_room_id(
                        room_id=room_id,
                        offset=offset,
                        limit=limit,
                        order_by="created_at",
                        order_direction=OrderDirection.DESC,
                    )

                case RatingFilters.OLDEST:
                    return await unit_of_work.review.get_by_room_id(
                        room_id=room_id,
                        offset=offset,
                        limit=limit,
                        order_by="created_at",
                        order_direction=OrderDirection.ASC,
                    )

    async def create(self, unit_of_work: UnitOfWork, rating: ReviewCreateIn, user_id: str):
        rating = ReviewCreate(**rating.model_dump(), user_id=user_id)
        async with unit_of_work:
            updated_rating = await unit_of_work.review.create(rating)
            average_rating = round(await unit_of_work.review.get_average_rating(room_id=rating.room_id), 1)
            await unit_of_work.room.update({"average_rating": average_rating}, id=rating.room_id)
            return updated_rating

    async def get_average_rating(self, unit_of_work: UnitOfWork, room_id: str):
        async with unit_of_work:
            stars = await unit_of_work.review.get_average_rating(room_id=room_id)
            return ReviewAverageGet(room_id=room_id, stars=stars)

    async def get_average_ratings(self, unit_of_work: UnitOfWork):
        async with unit_of_work:
            ratings = await unit_of_work.review.get_average_ratings()
            return [ReviewAverageGet(room_id=rating["room_id"], stars=rating["stars"]) for rating in ratings]

    async def get_count(self, room_id: str, unit_of_work: UnitOfWork):
        async with unit_of_work:
            return await unit_of_work.review.get_count(room_id=room_id)
