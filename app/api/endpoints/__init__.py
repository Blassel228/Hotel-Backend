from fastapi import APIRouter

from app.api.endpoints import room, healthcheck, auth, user, booking, guest, image, payment, rating, stripe_webhook

api_router = APIRouter(prefix="/api")

api_router.include_router(healthcheck.router, prefix="/healthcheck", tags=["Healthcheck"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(room.router, prefix="/room", tags=["Room"])
api_router.include_router(booking.router, prefix="/booking", tags=["Booking"])
api_router.include_router(guest.router, prefix="/guest", tags=["Guest"])
api_router.include_router(image.router, prefix="/image", tags=["Image"])
api_router.include_router(payment.router, prefix="/payment", tags=["Payment"])
api_router.include_router(rating.router, prefix="/rating", tags=["Rating"])
api_router.include_router(stripe_webhook.router, tags=["Stripe Webhook"])
