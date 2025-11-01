from fastapi import APIRouter

from app.api.dependencies import user_service, UnitOfWorkDep, get_current_user
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter()


@router.post("/")
async def create(user: UserCreate, service: user_service, unit_of_work: UnitOfWorkDep):
    return await service.create(user, unit_of_work)


@router.put("/self-update")
async def self_update(
    user: UserUpdate,
    service: user_service,
    current_user: get_current_user,
    unit_of_work: UnitOfWorkDep,
):
    return await service.update(user=user, user_id=current_user.id, unit_of_work=unit_of_work)


@router.get("/")
async def get_multi(service: user_service, unit_of_work: UnitOfWorkDep):
    return await service.get_multi(unit_of_work)


@router.get("/{user_id}")
async def get_one(service: user_service, unit_of_work: UnitOfWorkDep, user_id: str):
    return await service.get_one(unit_of_work=unit_of_work, user_id=user_id)


@router.delete("/{user_id}")
async def delete(
    service: user_service,
    unit_of_work: UnitOfWorkDep,
    user_id: str,
):
    return await service.delete(unit_of_work=unit_of_work, user_id=user_id)


@router.put("/{user_id}")
async def update(user_id: str, service: user_service, unit_of_work: UnitOfWorkDep, user: UserUpdate):
    return await service.update(user_id=user_id, unit_of_work=unit_of_work, user=user)
