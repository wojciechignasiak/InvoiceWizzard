class RedisDatabaseError(Exception):
    """Base exception for database related errors."""

class RedisNotFoundError(RedisDatabaseError):
    """Exception thrown when the record is not found."""

class RedisSetError(RedisDatabaseError):
    """Exception thrown when the record is not found."""