from fastapi import APIRouter

from app.api.dependencies import user_service, UnitOfWorkDep
from app.schemas.user import UserCreate

router = APIRouter()


@router.post("/")
async def create(user: UserCreate, service: user_service, unit_of_work: UnitOfWorkDep):
    return await service.create(user, unit_of_work)


@router.get("/")
async def get_multi(user: UserCreate, service: user_service, unit_of_work: UnitOfWorkDep):
    return await service.get_multi(user, unit_of_work)
