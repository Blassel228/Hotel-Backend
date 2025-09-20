import json

from fastapi import APIRouter, Request, HTTPException
from app.core import settings
from app.core.exc.payment import PaymentVerificationFailed
from app.api.dependencies import payment_service, UnitOfWorkDep
import stripe
import logging

from app.enums.booking_status import BookingStatus
from app.schemas.refund import CreateRefund

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/stripe_webhook")
async def stripe_webhook(
    request: Request,
    service: payment_service,
    unit_of_work: UnitOfWorkDep,
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.SignatureVerificationError:
        logger.error("Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session["id"]

        try:
            result = await service.handle_successful_payment_and_create_booking(
                unit_of_work, session_id
            )
            logger.info(f"✅ Booking created via webhook: {result}")
            return result

        except PaymentVerificationFailed as e:
            logger.error(f"Payment verification failed: {e.detail}")
            return {"status": "failed", "reason": e.detail}

        except Exception as e:
            logger.error(f"Unexpected error during booking creation: {str(e)}")
            return {"status": "failed", "reason": "Internal error"}


    elif event["type"] == "refund.created":
        refund = event["data"]["object"]

        stripe_refund_id = refund["id"]

        amount_refunded = refund["amount"] / 100.0

        reason = refund.get("reason") or "unknown"

        payment_intent_id = refund["payment_intent"]

        print(f"REFUND OBJECT: {json.dumps(refund, indent=2, ensure_ascii=False)}")

        try:
            async with unit_of_work:
                booking = await unit_of_work.booking.get_one_or_none(intent_id=payment_intent_id)

                if not booking:
                    logger.warning(f"Booking not found for intent {payment_intent_id}")

                    return {"status": "ignored", "reason": "booking_not_found"}

                existing_refund = await unit_of_work.refund.get_one_or_none(stripe_refund_id=stripe_refund_id)

                if existing_refund:
                    logger.info(f"Refund {stripe_refund_id} already processed")

                    return {"status": "ignored", "reason": "duplicate_refund"}

                refund_data = CreateRefund(
                    booking_id=booking.id,
                    refund_amount=amount_refunded,
                    refund_reason=reason,
                    stripe_refund_id=stripe_refund_id,
                )

                await unit_of_work.refund.create(refund_data)
                await unit_of_work.booking.update(
                    {"status": BookingStatus.REFUNDED.value},
                    id=booking.id
                )

            logger.info(f"✅ Refund {stripe_refund_id} processed for booking {booking.id}")

            return {"status": "success", "refund_id": stripe_refund_id}


        except Exception as e:

            logger.error(f"Failed to process refund webhook: {str(e)}")

            return {"status": "failed", "reason": str(e)}

    logger.info(f"Ignored event: {event['type']}")

    return {"status": "ignored", "event_type": event["type"]}