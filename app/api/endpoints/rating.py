from fastapi import APIRouter

from app.api.dependencies import UnitOfWorkDep, get_current_user, rating_service
from app.schemas.rating import RatingCreateIn

router = APIRouter()


@router.post("/")
async def create(
    rating: RatingCreateIn, unit_of_work: UnitOfWorkDep, current_user: get_current_user, service: rating_service
):
    return await service.create(rating=rating, unit_of_work=unit_of_work, user_id=current_user.id)


@router.get("/rooms/{room_id}/average", summary="Get average rating for a room")
async def get_room_average_rating(
    room_id: str,
    unit_of_work: UnitOfWorkDep,
    service: rating_service,
):
    return await service.get_average_rating(room_id=room_id, unit_of_work=unit_of_work)


@router.get("/average", summary="Get average ratings for all rooms")
async def get_all_average_ratings(
    unit_of_work: UnitOfWorkDep,
    service: rating_service,
):
    return await service.get_average_ratings(unit_of_work=unit_of_work)