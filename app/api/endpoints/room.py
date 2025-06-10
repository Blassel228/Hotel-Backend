from fastapi import APIRouter

from app.api.dependencies import room_service, UnitOfWorkDep

router = APIRouter()


@router.get("")
async def get(service: room_service, unit_of_work: UnitOfWorkDep, offset: int = 0, limit: int = None):
    return await service.get_all(unit_of_work, offset, limit)
