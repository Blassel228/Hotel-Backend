from datetime import datetime

from fastapi import APIRouter
from app.api.dependencies import get_current_user, UnitOfWorkDep, email_service

router = APIRouter()

@router.post("/send-verification-email")
async def send_verification_email(
    current_user: get_current_user,
    unit_of_work: UnitOfWorkDep,
    service: email_service,
):
    await service.send_verification_email(current_user.id, unit_of_work)
    return {"message": "Verification email sent"}


@router.get("/verify-email")
async def verify_email(
        token: str,
        unit_of_work: UnitOfWorkDep,
        service: email_service
):
    return await service.verify_token(token=token, unit_of_work=unit_of_work)