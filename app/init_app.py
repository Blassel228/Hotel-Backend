import logging

from fastapi import FastAPI, HTTPException
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from requests import Request

from app.api.endpoints import api_router
from app.core import settings
from app.core.exc import AuthError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} | URL: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": exc.status_code, "detail": exc.detail}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error at {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "error": {"code": 422, "message": "Validation error", "detail": exc.errors()}},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception at {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500, content={"success": False, "error": {"code": 500, "message": "Internal server error"}}
    )


@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    logger.warning(f"Auth error [{exc.error_code}]: {exc.detail} | URL: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": exc.status_code, "type": exc.error_code, "detail": exc.detail}},
        headers=exc.headers or {},
    )


app.include_router(api_router)
