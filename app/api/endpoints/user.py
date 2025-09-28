from fastapi import APIRouter

from app.api.dependencies import user_service, UnitOfWorkDep, get_current_user
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter()


@router.post("/")
async def create(user: UserCreate, service: user_service, unit_of_work: UnitOfWorkDep):
    return await service.create(user, unit_of_work)


@router.put("/")
async def update(
    user: UserUpdate,
    service: user_service,
    current_user: get_current_user,
    unit_of_work: UnitOfWorkDep,
):
    return await service.update(user, current_user.id, unit_of_work)


@router.get("/")
async def get_multi(service: user_service, unit_of_work: UnitOfWorkDep):
    return await service.get_multi(unit_of_work)
