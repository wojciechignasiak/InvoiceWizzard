import inspect

class CustomException(Exception):
    __slots__ = ('status_code', 'message', 'class_and_method', 'argument', 'child_error')
    def __init__(
        self,
        status_code: int,
        message: str,
        class_and_method: str | None = None,
        argument: dict | None = None,
        child_error: Exception | "CustomException" | None = None,
    ):
        self.status_code = status_code
        self.message = message
        self.class_and_method= class_and_method or self.get_class_method_name()
        self.argument = argument
        self.child_error = child_error

    @staticmethod
    def get_class_method_name() -> str:
        result: inspect.FrameInfo = inspect.stack()[2]
        class_method_name_where_exception_occurred: str = result.function
        class_name_where_exception_occurred: None = None
        if 'self' in result.frame.f_locals:
            class_name_where_exception_occurred: str = type(result.frame.f_locals['self']).__name__

        return f"{class_name_where_exception_occurred}.{class_method_name_where_exception_occurred}"

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