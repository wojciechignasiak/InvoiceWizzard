class CustomException(Exception):
    def __init__(
        self,
        status_code: int,
        message: str,
        class_and_method: str,
        argument: dict | None = None,
        child_error: Exception | "CustomException" | None = None,
    ):
        self.status_code = status_code
        self.message = message
        self.class_and_method= class_and_method
        self.argument = argument
        self.child_error = child_error

class AuthError(CustomException):
    """Base exception for auth related errors."""

class ServiceError(CustomException):
    """Base exception for service related errors."""

class DataNotFoundError(CustomException):
    """Base exception for service related errors."""

class DatabaseError(CustomException):
    """Base exception for database related errors."""

class LogicError(CustomException):
    """Base exception for other related errors."""

class EventError(CustomException):
    """Base exception for events related errors"""