from fastapi import APIRouter, HTTPException

from app.api.dependencies import UnitOfWorkDep, get_current_user, payment_service
from app.schemas.payment import CreateCheckoutSessionRequest

router = APIRouter()


@router.post("/create-checkout-session-with-token")
async def create_checkout_session_with_token(
    request: CreateCheckoutSessionRequest,
    unit_of_work: UnitOfWorkDep,
    service: payment_service,
    current_user: get_current_user,
):
    if not request.guest_data:
        raise HTTPException(status_code=400, detail="Guest data is required")
    url = await service.create_checkout_session(
        unit_of_work=unit_of_work, user_id=str(current_user.id), request=request
    )
    return {"url": url}

@router.post("/create-checkout-session-without-token")
async def create_checkout_session_without_token(
    request: CreateCheckoutSessionRequest,
    service: payment_service,
    unit_of_work: UnitOfWorkDep,
):
    if not request.guest_data:
        raise HTTPException(status_code=400, detail="Guest data is required")
    url = await service.create_checkout_session(
        unit_of_work=unit_of_work, user_id=None, request=request
    )
    return {"url": url}