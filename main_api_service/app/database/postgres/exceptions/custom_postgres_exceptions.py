class PostgreSQLDatabaseError(Exception):
    """Base exception for database related errors."""

class PostgreSQLNotFoundError(PostgreSQLDatabaseError):
    """Exception thrown when the record is not found."""

class PostgreSQLIntegrityError(PostgreSQLDatabaseError):
    """Exception thrown when integrity is violated"""
