import json
import logging
from datetime import datetime
from typing import Optional

import stripe

from app.core import settings
from app.core.exc.payment import PaymentProviderException, PaymentVerificationFailed
from app.enums.booking_status import BookingStatus
from app.schemas.booking import CreateBooking
from app.schemas.email import EmailIn
from app.schemas.guest import GuestCreate
from app.schemas.payment import CreateCheckoutSessionRequest, CreateRefundRequestByUser, CreateRefundRequestByAdmin
from app.services.email import EmailService
from app.utils.unitofwork import UnitOfWork

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        stripe.api_key = settings.stripe.STRIPE_SECRET_KEY
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
                success_url=settings.stripe.STRIPE_SUCCESS_URL + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=settings.stripe.STRIPE_CANCEL_URL,
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

    @staticmethod
    async def handle_successful_payment_and_create_booking(
        unit_of_work: UnitOfWork,
        session_id: str,
        service: EmailService
    ) -> dict:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.StripeError as e:
            logger.error(f"Failed to retrieve session {session_id}: {str(e)}")
            raise PaymentVerificationFailed(detail="Payment session not found or invalid")

        if session.payment_status != "paid":
            logger.warning(f"Payment not completed for session {session_id}. Status: {session.payment_status}")
            raise PaymentVerificationFailed(detail="Payment is not completed")

        intent_id = session.payment_intent
        if not intent_id:
            raise PaymentVerificationFailed(detail="Payment intent ID not found")

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
            intent_id=intent_id,
            room_id=metadata["room_id"],
            price=float(metadata["price"]),
            start_date=start_date,
            end_date=end_date,
            status=BookingStatus.CONFIRMED.CONFIRMED,
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

        customer_email = session.get("customer_details", {}).get("email") or session.get("customer_email")
        email_in = EmailIn(
            id=str(booking.id),
            start_date=start_date,
            end_date=end_date,
            price=float(metadata["price"])
        )

        await service.send_booking_confirmation_email(customer_email, email_in)

        logger.info(f"Booking {booking.id} created successfully for session {session_id}")
        return {
            "status": "success",
            "booking_id": str(booking.id),
            "message": "Booking created after successful payment",
        }

    async def refund_booking_by_user(
        self,
        unit_of_work: UnitOfWork,
        request: CreateRefundRequestByUser,
    ) -> dict:
        async with unit_of_work:
            booking = await unit_of_work.booking.get_one(id=request.booking_id)
            if not booking.intent_id:
                raise PaymentVerificationFailed(detail="No payment intent associated with this booking")

        refund_amount_in_cents = self.calculate_refund_amount(booking)

        try:
            stripe_refund = stripe.Refund.create(
                payment_intent=booking.intent_id,
                amount=refund_amount_in_cents,
                reason="requested_by_customer",
                metadata={"refund_reason": request.refund_reason, "initiated_by": "user"},
            )

            logger.info(f"User-initiated refund {stripe_refund.id} for booking {request.booking_id}")

            refund_amount_in_big_units = self.convert_from_minor_units(refund_amount_in_cents)

            async with unit_of_work:
                await unit_of_work.refund.create(
                    {
                        "booking_id": booking.id,
                        "stripe_refund_id": stripe_refund.id,
                        "refund_amount": refund_amount_in_big_units,
                        "refund_reason": request.refund_reason,
                        "user_id": booking.user_id,
                    }
                )
                await unit_of_work.booking.update({"status": BookingStatus.REFUNDED.value}, id=booking.id)

        except stripe.StripeError as e:
            logger.error(f"Stripe refund failed for booking {request.booking_id}: {str(e)}")
            raise PaymentProviderException(detail=f"Refund failed: {str(e)}")

        return {
            "status": "success",
            "refund_id": stripe_refund.id,
            "refund_amount": refund_amount_in_big_units,
            "currency": stripe_refund.currency,
            "booking_id": request.booking_id,
            "message": "Refund processed according to cancellation policy",
        }

    async def refund_booking_by_admin(
        self,
        unit_of_work: UnitOfWork,
        request: CreateRefundRequestByAdmin,
    ) -> dict:
        async with unit_of_work:
            booking = await unit_of_work.booking.get_one(id=request.booking_id)
            if not booking.intent_id:
                raise PaymentVerificationFailed(detail="No payment intent associated with this booking")

            if request.amount > booking.price:
                raise ValueError("Refund amount cannot exceed the original booking price")

        refund_amount_in_cents = int(round(self.convert_to_minor_units(request.amount)))

        try:
            stripe_refund = stripe.Refund.create(
                payment_intent=booking.intent_id,
                amount=refund_amount_in_cents,
                metadata={
                    "initiated_by": "admin",
                    "requested_amount": str(request.amount),
                },
            )

            logger.info(
                f"Admin-initiated refund {stripe_refund.id} for booking {request.booking_id}, "
                f"amount: {request.amount} {stripe_refund.currency}"
            )

            async with unit_of_work:
                await unit_of_work.refund.create(
                    {
                        "booking_id": booking.id,
                        "stripe_refund_id": stripe_refund.id,
                        "refund_amount": request.amount,
                        "refund_reason": request.refund_reason,
                        "user_id": booking.user_id,
                    }
                )
                await unit_of_work.booking.update({"status": BookingStatus.REFUNDED.value}, id=booking.id)

        except stripe.StripeError as e:
            logger.error(f"Stripe refund failed for booking {request.booking_id}: {str(e)}")
            raise PaymentProviderException(detail=f"Refund failed: {str(e)}")

        return {
            "status": "success",
            "refund_id": stripe_refund.id,
            "refund_amount": request.amount,
            "currency": stripe_refund.currency,
            "booking_id": request.booking_id,
            "message": "Admin refund processed successfully",
        }

    @staticmethod
    def convert_to_minor_units(amount: float) -> float:
        return amount * 100

    @staticmethod
    def convert_from_minor_units(amount: float) -> float:
        return amount / 100

    @staticmethod
    def calculate_refund_amount(booking) -> float:
        """
        Calculate refund amount based on days left before check-in:
        - > 12: 100% refund
        - 12 to 10 days: 70% refund
        - 7 to 9 days: 50% refund
        - < 7 days: 35% refund
        """
        now = datetime.now()
        days_until_checkin = (booking.start_date - now).days
        refund_percent = 1

        if 12 >= days_until_checkin >= 10:
            refund_percent = 0.70
        elif 9 >= days_until_checkin >= 7:  # 7 to 9 days
            refund_percent = 0.50
        elif days_until_checkin < 7:  # less than 7 days
            refund_percent = 0.35

        return int(round(booking.price * refund_percent * 100))
