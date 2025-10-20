from fastapi import APIRouter

from app.api.dependencies import UnitOfWorkDep, get_current_user, review_service
from app.enums import OrderDirection
from app.enums.rating_filters import RatingFilters
from app.schemas.review import ReviewCreateIn

router = APIRouter()


@router.post("/")
async def create(
    rating: ReviewCreateIn, unit_of_work: UnitOfWorkDep, current_user: get_current_user, service: review_service
):
    return await service.create(rating=rating, unit_of_work=unit_of_work, user_id=current_user.id)


@router.get("/rooms/{room_id}")
async def get_multi(
    room_id: str,
    service: review_service,
    unit_of_work: UnitOfWorkDep,
    limit: int = 10,
    offset: int = 1,
    sort: RatingFilters = RatingFilters.BEST,
):
    return await service.get_multi(room_id=room_id, limit=limit, offset=offset, sort=sort, unit_of_work=unit_of_work)


@router.get("/count/rooms/{room_id}")
async def get_count(room_id: str, service: review_service, unit_of_work: UnitOfWorkDep):
    return await service.get_count(room_id=room_id, unit_of_work=unit_of_work)


@router.get("/rooms/{room_id}/average", summary="Get average rating for a room")
async def get_room_average_rating(
    room_id: str,
    unit_of_work: UnitOfWorkDep,
    service: review_service,
):
    return await service.get_average_rating(room_id=room_id, unit_of_work=unit_of_work)


@router.get("/average", summary="Get average ratings for all rooms")
async def get_all_average_ratings(
    unit_of_work: UnitOfWorkDep,
    service: review_service,
):
    return await service.get_average_ratings(unit_of_work=unit_of_work)
