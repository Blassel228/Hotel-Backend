from fastapi import APIRouter, HTTPException

from app.api.dependencies import UnitOfWorkDep, get_current_user, payment_service
from app.schemas.email import EmailIn
from app.schemas.payment import CreateCheckoutSessionRequest, CreateRefundRequestByUser, CreateRefundRequestByAdmin

router = APIRouter()


@router.post("/create-checkout-session")
async def create_checkout_session_with_token(
    request: CreateCheckoutSessionRequest,
    unit_of_work: UnitOfWorkDep,
    service: payment_service,
    current_user: get_current_user,
):
    url = await service.create_checkout_session(
        unit_of_work=unit_of_work, user_id=str(current_user.id), request=request
    )
    return {"url": url}


@router.post("/user-refund")
async def refund_booking(unit_of_work: UnitOfWorkDep, request: CreateRefundRequestByUser, service: payment_service):
    return await service.refund_booking_by_user(unit_of_work=unit_of_work, request=request)


@router.post("/admin-refund")
async def refund_booking(unit_of_work: UnitOfWorkDep, request: CreateRefundRequestByAdmin, service: payment_service):
    return await service.refund_booking_by_admin(unit_of_work=unit_of_work, request=request)


@router.post("/send_email")
async def send_booking_confirmation_email(email: str, email_in: EmailIn, service: payment_service):
    return await service.send_booking_confirmation_email(email, booking_data=email_in)