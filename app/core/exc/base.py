from typing import Any, Callable

from fastapi import HTTPException, status
from loguru import logger


class BaseHTTPException(HTTPException):
    """
    Base class for all custom exceptions.
    *_pattern is a tuple with a message and arguments to format it. Example: ('{0} not found!', 'class_name')
    """

    status_code: int = 400
    message_pattern: tuple[str, ...] | None = None

    log_level: str | None = "debug"
    log_message_pattern: tuple | None = None

    def __init__(
        self, detail: str | dict[str, str] | None = None, headers: dict[str, str] | None = None, **kwargs: Any
    ) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
        if self.message_pattern:
            message, *args = self.message_pattern
            formatted_args = [getattr(self, arg) for arg in args]
            detail = message.format(*formatted_args)
        self.log_exception(str(detail))

        super().__init__(status_code=self.status_code, detail=[{"msg": detail}], headers=headers)

    def log_exception(self, detail: str = None) -> None:
        if self.log_level in {"debug", "info", "warning", "error", "critical"}:
            logger.name = self.__class__.__name__
            logger_method: Callable = getattr(logger, self.log_level)

            if self.log_message_pattern:
                log_message, *args = self.log_message_pattern
                formatted_args = [getattr(self, arg) for arg in args]
                logger_method(log_message, *formatted_args)
            else:
                logger_method(detail)


class ObjectNotFoundException(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    log_message_pattern = ("{0} not found, statement= {1} ", "class_name", "statement")
    message_pattern = ("{0} not found", "class_name")


class ObjectExistsException(BaseHTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message_pattern = ("{0} with this {1} already exists.", "class_name", "obj")


class DBConnectionException(BaseHTTPException):
    log_level = "error"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    message_pattern = ("Connection to db refused",)
