from fastapi import APIRouter
from app.api.dependencies import get_current_user, UnitOfWorkDep, email_service as email_service_dep, user_service as user_service_dep
from app.schemas.email import ChangeEmailRequest

router = APIRouter()

@router.post("/send-verification-email")
async def send_verification_email(
    current_user: get_current_user,
    unit_of_work: UnitOfWorkDep,
    service: email_service_dep,
):
    await service.send_verification_email(current_user.id, unit_of_work)
    return {"message": "Verification email sent"}


@router.get("/verify-email")
async def verify_email(
        token: str,
        unit_of_work: UnitOfWorkDep,
        service: email_service_dep
):
    return await service.verify_token(token=token, unit_of_work=unit_of_work)


@router.get("/verify-email-change")
async def verify_email_change(
    token: str,
    user_service: user_service_dep,
    uow: UnitOfWorkDep
):
    updated_user = await user_service.confirm_email_change(token, uow)
    return {"message": "Email successfully changed", "user": updated_user}


@router.post("/me/change-email")
async def request_email_change(
    change_email_request: ChangeEmailRequest,
    current_user: get_current_user,
    user_service: user_service_dep,
    email_service: email_service_dep,
    unit_of_work: UnitOfWorkDep
):
    token = await user_service.initiate_email_change(user_id=current_user.id, new_email=change_email_request.new_email, password=change_email_request.password, unit_of_work=unit_of_work)
    await email_service.send_email_change_verification(new_email=change_email_request.new_email, token=token)
    return {"message": "Verification email sent to new address"}