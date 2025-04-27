from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.endpoints import api_router
from app.core import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Content-Type", "X-Telegram-Init-Data"],
)
app.include_router(api_router)
