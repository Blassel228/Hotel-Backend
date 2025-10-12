from fastapi import status

from app.core.exc import BaseHTTPException


class PermissionDeniedException(BaseHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    error_type = "PERMISSION_DENIED"
    message_pattern = ("You do not have permission to perform this action.",)


class BookingConflictException(BaseHTTPException):
    status_code = status.HTTP_409_CONFLICT
    error_type = "BOOKING_CONFLICT"
    message_pattern = ("Booking cannot be {0} in its current state.", "action")