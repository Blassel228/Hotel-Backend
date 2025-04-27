from fastapi import APIRouter

from app.api.endpoints import property, healthcheck, auth, user, booking

api_router = APIRouter(prefix="/api")

api_router.include_router(healthcheck.router, prefix="/healthcheck", tags=["Healthcheck"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(property.router, prefix="/property", tags=["Property"])
api_router.include_router(booking.router, prefix="/booking", tags=["Booking"])
