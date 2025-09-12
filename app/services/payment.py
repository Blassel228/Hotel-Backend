import json
from datetime import datetime
from typing import Optional

import stripe
from app.core import settings
from app.schemas.booking import CreateBooking
from app.schemas.guest import GuestCreate
from app.schemas.payment import CreateCheckoutSessionRequest
from app.utils.unitofwork import UnitOfWork
import logging
from app.core.exc.payment import PaymentProviderException, PaymentVerificationFailed

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        if not stripe.api_key:
            raise ValueError("Stripe secret key is not configured")

    async def create_checkout_session(
        self,
        unit_of_work: UnitOfWork,
        user_id: Optional[str] = None,
        request: CreateCheckoutSessionRequest = None,
    ) -> str:
        async with unit_of_work:
            room = await unit_of_work.room.get_one(id=request.room_id)
            customer_email = None
            if user_id:
                user = await unit_of_work.user.get_one(id=user_id)
                customer_email = user.email

        price_in_minor_units = self.convert_to_minor_units(request.price)

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": request.currency,
                            "unit_amount": int(price_in_minor_units),
                            "product_data": {
                                "name": f"Booking: {room.type}",
                                "description": f"{room.beds} beds, {request.start_date.date()} to {request.end_date.date()}",
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=settings.STRIPE_SUCCESS_URL + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=settings.STRIPE_CANCEL_URL,
                metadata={
                    "user_id": str(user_id) if user_id else "",
                    "room_id": str(request.room_id),
                    "start_date": request.start_date.isoformat(),
                    "end_date": request.end_date.isoformat(),
                    "price": str(request.price),
                    "currency": request.currency,
                    "special_requests": request.special_requests or "",
                    "guest_data": json.dumps(request.guest_data.model_dump()) if request.guest_data else "",
                },
                customer_email=customer_email,
            )

            logger.info(f"Stripe session {session.id} created for room {request.room_id}")
            return session.url

        except stripe.StripeError as e:
            logger.error(f"Stripe error for room {request.room_id}: {str(e)}")
            raise PaymentProviderException(detail=f"Payment gateway error: {str(e)}")

    async def handle_successful_payment_and_create_booking(
        self,
        unit_of_work: UnitOfWork,
        session_id: str,
    ) -> dict:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.StripeError as e:
            logger.error(f"Failed to retrieve session {session_id}: {str(e)}")
            raise PaymentVerificationFailed(detail="Payment session not found or invalid")

        if session.payment_status != "paid":
            logger.warning(f"Payment not completed for session {session_id}. Status: {session.payment_status}")
            raise PaymentVerificationFailed(detail="Payment is not completed")

        metadata = session.metadata
        required_keys = ["room_id", "start_date", "end_date", "price", "currency", "special_requests"]
        for key in required_keys:
            if key not in metadata:
                raise PaymentVerificationFailed(detail=f"Missing required metadata: {key}")

        try:
            start_date = datetime.fromisoformat(metadata["start_date"])
            end_date = datetime.fromisoformat(metadata["end_date"])
        except ValueError:
            raise PaymentVerificationFailed(detail="Invalid date format in metadata")

        guest_id = None
        if not metadata.get("user_id") and metadata.get("guest_data"):
            try:
                guest_data_dict = json.loads(metadata["guest_data"])
                guest_create = GuestCreate(**guest_data_dict)
                async with unit_of_work:
                    guest = await unit_of_work.guest.create(guest_create)
                    guest_id = guest.id
            except Exception as e:
                logger.error(f"Failed to create guest: {str(e)}")
                raise PaymentVerificationFailed(detail="Failed to create guest record")

        booking_data = CreateBooking(
            room_id=metadata["room_id"],
            price=float(metadata["price"]),
            start_date=start_date,
            end_date=end_date,
            status="Confirmed",
            special_requests=metadata["special_requests"] or None,
            user_id=metadata.get("user_id") or None,
            guest_id=guest_id,
        )

        if metadata.get("user_id"):
            if not metadata.get("guest_data"):
                raise PaymentVerificationFailed(detail="Guest data is required for authenticated users")
            try:
                guest_data_dict = json.loads(metadata["guest_data"])
                guest_create = GuestCreate(**guest_data_dict)
                async with unit_of_work:
                    guest = await unit_of_work.guest.create(guest_create)
                    guest_id = guest.id
                    booking_data.guest_id = guest_id
                    booking_data.user_id = metadata["user_id"]
            except Exception as e:
                logger.error(f"Failed to create guest for authenticated user: {str(e)}")
                raise PaymentVerificationFailed(detail="Failed to create guest record")

        async with unit_of_work:
            booking = await unit_of_work.booking.create(booking_data.model_dump(exclude_unset=True))

        logger.info(f"Booking {booking.id} created successfully for session {session_id}")
        return {
            "status": "success",
            "booking_id": str(booking.id),
            "message": "Booking created after successful payment",
        }

    @staticmethod
    def convert_to_minor_units(amount: float) -> float:
        return amount * 100