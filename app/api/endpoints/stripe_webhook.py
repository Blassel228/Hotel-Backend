from fastapi import APIRouter, Request, HTTPException
from app.core import settings
from app.core.exc.payment import PaymentVerificationFailed
from app.api.dependencies import payment_service, UnitOfWorkDep
import stripe
import logging

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
            logger.info(f"✅ Webhook processed: {result}")
            return result

        except PaymentVerificationFailed as e:
            logger.error(f"Payment verification failed: {e.detail}")
            return {"status": "failed", "reason": e.detail}

        except Exception as e:
            logger.error(f"Unexpected error during booking creation: {str(e)}")
            return {"status": "failed", "reason": "Internal error"}

    logger.info(f"Ignored event: {event['type']}")
    return {"status": "ignored", "event_type": event["type"]}