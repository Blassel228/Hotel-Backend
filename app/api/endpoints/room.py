import json
from datetime import date
from typing import List

from fastapi import APIRouter, Form, File, UploadFile, Depends

from app.api.dependencies import room_service, UnitOfWorkDep, get_current_user
from app.schemas.room import RoomFilterParams, RoomCreateIn, RoomUpdateIn, RoomRead

router = APIRouter()


@router.post("/", summary="Create a new room")
async def create(
    unit_of_work: UnitOfWorkDep,
    service: room_service,
    room: str = Form(...),
    image: UploadFile = File(...)
):
    room_dict = json.loads(room)
    room = RoomCreateIn(**room_dict)
    image = await image.read()
    return await service.create(unit_of_work=unit_of_work, room=room, image=image)


@router.get("/", response_model=List[RoomRead], summary="Get all rooms")
async def get_all(unit_of_work: UnitOfWorkDep, service: room_service):
    return await service.get_all(unit_of_work=unit_of_work)


@router.get("/filter", summary="Get rooms using filter parameters")
async def get_filtered_rooms(
    unit_of_work: UnitOfWorkDep,
    service: room_service,
    filters: RoomFilterParams = Depends(),
):
    return await service.get_with_filters(unit_of_work=unit_of_work, filters=filters)


@router.get("/search/{start_date}/{end_date}/{capacity}", summary="Search available rooms by date range and capacity")
async def search(
    unit_of_work: UnitOfWorkDep,
    start_date: date,
    end_date: date,
    capacity: int,
    service: room_service,
):
    return await service.search(unit_of_work=unit_of_work, start_date=start_date, end_date=end_date, capacity=capacity)


@router.get("/not-rated", summary="Get rooms booked but not rated by the user")
async def get_not_rated_rooms(
    unit_of_work: UnitOfWorkDep,
    service: room_service,
    current_user: get_current_user,
):
    return await service.get_rooms_booked_not_rated_by_user(unit_of_work=unit_of_work, user_id=current_user.id)


@router.get("/{room_id}", summary="Get room by ID")
async def get_one(room_id: str, unit_of_work: UnitOfWorkDep, service: room_service):
    return await service.get_one(room_id=room_id, unit_of_work=unit_of_work)


@router.put("/{room_id}", summary="Update room by ID")
async def update(room_id: str, unit_of_work: UnitOfWorkDep, service: room_service, room: RoomUpdateIn):
    return await service.update(room_id=room_id, unit_of_work=unit_of_work, room=room)


@router.delete("/{room_id}", summary="Delete room by ID")
async def delete(room_id: str, unit_of_work: UnitOfWorkDep, service: room_service):
    return await service.delete(room_id=room_id, unit_of_work=unit_of_work)