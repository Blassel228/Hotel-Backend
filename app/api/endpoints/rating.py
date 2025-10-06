from fastapi import APIRouter

from app.api.dependencies import UnitOfWorkDep, get_current_user, rating_service
from app.schemas.rating import RatingCreateIn

router = APIRouter()


@router.post("/")
async def create(
    rating: RatingCreateIn, unit_of_work: UnitOfWorkDep, current_user: get_current_user, service: rating_service
):
    return await service.create(rating=rating, unit_of_work=unit_of_work, user_id=current_user.id)


@router.get("/get_average_rating/room/{room_id}")
async def get_average_rating(room_id: str, unit_of_work: UnitOfWorkDep, service: rating_service):
    return await service.get_average_rating(room_id=room_id, unit_of_work=unit_of_work)


@router.get("/get_average_ratings")
async def get_average_rating(unit_of_work: UnitOfWorkDep, service: rating_service):
    return await service.get_average_ratings(unit_of_work=unit_of_work)
