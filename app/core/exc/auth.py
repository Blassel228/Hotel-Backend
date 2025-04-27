from .base import BaseHTTPException


class AuthError(BaseHTTPException):
    message_pattern = ("Failed to auth: {0}", "error")
