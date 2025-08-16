from datetime import date

from fastapi import APIRouter

from app.api.dependencies import room_service, UnitOfWorkDep
from app.models import Room

router = APIRouter()


@router.get("")
async def get(service: room_service, unit_of_work: UnitOfWorkDep, offset: int = 0, limit: int = None):
    return await service.get_all(unit_of_work, offset, limit)


@router.get("/search/{start_date}/{end_date}/{capacity}")
async def search(unit_of_work: UnitOfWorkDep, start_date: date, end_date: date, capacity: int, service: room_service):
    return await service.search(unit_of_work=unit_of_work, start_date=start_date, end_date=end_date, capacity=capacity)
