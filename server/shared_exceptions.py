"""
Enhanced shared exception handling for CityPulse platform.

This module provides unified exception classes and error handling utilities
with correlation IDs, structured logging, and comprehensive error context.
"""

import logging
import structlog
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass, field
from contextlib import contextmanager
from uuid import uuid4
import traceback
import time
from pydantic import BaseModel, Field

# Configure structured logging
logger = structlog.get_logger(__name__)


@dataclass
class ErrorContext:
    """Enhanced error context with correlation ID and metadata."""
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    operation: Optional[str] = None

    def add_context(self, **kwargs):
        """Add additional context information."""
        self.context.update(kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error context to dictionary."""
        return {
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "context": self.context,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "operation": self.operation
        }


@contextmanager
def error_context(operation: str = None, user_id: str = None, request_id: str = None, **context):
    """
    Context manager for error handling with correlation IDs and structured logging.

    Args:
        operation: Name of the operation being performed
        user_id: ID of the user performing the operation
        request_id: ID of the request
        **context: Additional context information

    Yields:
        ErrorContext: The error context object
    """
    error_ctx = ErrorContext(
        user_id=user_id,
        request_id=request_id,
        operation=operation
    )
    error_ctx.add_context(**context)

    try:
        yield error_ctx
    except Exception as e:
        # Log the error with full context
        logger.error(
            "Operation failed",
            correlation_id=error_ctx.correlation_id,
            operation=operation,
            user_id=user_id,
            request_id=request_id,
            error_type=type(e).__name__,
            error_message=str(e),
            context=error_ctx.context,
            traceback=traceback.format_exc()
        )

        # Add correlation ID to the exception if it's a CityPulse exception
        if hasattr(e, 'correlation_id'):
            e.correlation_id = error_ctx.correlation_id

        raise


class ErrorCode(str, Enum):
    """Standardized error codes for the CityPulse platform."""
    
    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_FIELD = "MISSING_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    VALUE_OUT_OF_RANGE = "VALUE_OUT_OF_RANGE"
    
    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"
    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"
    DUPLICATE_DOCUMENT = "DUPLICATE_DOCUMENT"
    QUERY_FAILED = "QUERY_FAILED"
    CONNECTION_FAILED = "CONNECTION_FAILED"
    
    # External service errors
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    API_TIMEOUT = "API_TIMEOUT"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # Business logic errors
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    RESOURCE_LIMIT_EXCEEDED = "RESOURCE_LIMIT_EXCEEDED"
    
    # Data processing errors
    DATA_PROCESSING_ERROR = "DATA_PROCESSING_ERROR"
    INVALID_DATA_FORMAT = "INVALID_DATA_FORMAT"
    DATA_CORRUPTION = "DATA_CORRUPTION"


class CityPulseException(Exception):
    """Enhanced base exception class for CityPulse platform with correlation tracking."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        operation: Optional[str] = None
    ):
        """
        Initialize enhanced CityPulse exception.

        Args:
            message: Human-readable error message
            error_code: Standardized error code
            details: Additional error details
            cause: Original exception that caused this error
            correlation_id: Correlation ID for tracking
            user_id: ID of the user associated with the error
            request_id: ID of the request that caused the error
            operation: Name of the operation that failed
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
        self.correlation_id = correlation_id or str(uuid4())
        self.user_id = user_id
        self.request_id = request_id
        self.operation = operation
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        result = {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp
        }

        if self.cause:
            result["cause"] = str(self.cause)

        if self.user_id:
            result["user_id"] = self.user_id

        if self.request_id:
            result["request_id"] = self.request_id

        if self.operation:
            result["operation"] = self.operation

        return result
    
    def __str__(self) -> str:
        """String representation of the exception."""
        return f"[{self.correlation_id}] {self.error_code.value}: {self.message}"

    def log_error(self, logger_instance: Optional[logging.Logger] = None):
        """Log the error with full context."""
        log = logger_instance or logger
        log.error(
            "CityPulse Exception",
            correlation_id=self.correlation_id,
            error_code=self.error_code.value,
            message=self.message,
            details=self.details,
            user_id=self.user_id,
            request_id=self.request_id,
            operation=self.operation,
            timestamp=self.timestamp,
            cause=str(self.cause) if self.cause else None
        )


class ValidationException(CityPulseException):
    """Exception for validation errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize validation exception.
        
        Args:
            message: Validation error message
            field: Field that failed validation
            value: Value that failed validation
            details: Additional validation details
        """
        validation_details = details or {}
        if field:
            validation_details["field"] = field
        if value is not None:
            validation_details["value"] = str(value)
        
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            details=validation_details
        )
        self.field = field
        self.value = value


class DatabaseException(CityPulseException):
    """Exception for database-related errors."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        collection: Optional[str] = None,
        document_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize database exception.
        
        Args:
            message: Database error message
            operation: Database operation that failed
            collection: Collection/table involved
            document_id: Document ID involved
            cause: Original database exception
        """
        details = {}
        if operation:
            details["operation"] = operation
        if collection:
            details["collection"] = collection
        if document_id:
            details["document_id"] = document_id
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR,
            details=details,
            cause=cause
        )
        self.operation = operation
        self.collection = collection
        self.document_id = document_id


class ExternalServiceException(CityPulseException):
    """Exception for external service errors."""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize external service exception.
        
        Args:
            message: Service error message
            service_name: Name of the external service
            status_code: HTTP status code (if applicable)
            response_body: Response body from service
            cause: Original exception
        """
        details = {"service_name": service_name}
        if status_code:
            details["status_code"] = status_code
        if response_body:
            details["response_body"] = response_body
        
        super().__init__(
            message=message,
            error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            details=details,
            cause=cause
        )
        self.service_name = service_name
        self.status_code = status_code


class BusinessRuleException(CityPulseException):
    """Exception for business rule violations."""
    
    def __init__(
        self,
        message: str,
        rule_name: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize business rule exception.
        
        Args:
            message: Business rule violation message
            rule_name: Name of the violated rule
            context: Additional context about the violation
        """
        details = {"rule_name": rule_name}
        if context:
            details.update(context)
        
        super().__init__(
            message=message,
            error_code=ErrorCode.BUSINESS_RULE_VIOLATION,
            details=details
        )
        self.rule_name = rule_name


# Error handling utilities
def handle_database_error(
    operation: str,
    collection: str,
    error: Exception,
    document_id: Optional[str] = None
) -> DatabaseException:
    """
    Convert database errors to standardized exceptions.
    
    Args:
        operation: Database operation that failed
        collection: Collection/table involved
        error: Original error
        document_id: Document ID (if applicable)
        
    Returns:
        DatabaseException with appropriate error code
    """
    error_message = str(error)
    
    # Map specific error types to error codes
    if "not found" in error_message.lower():
        error_code = ErrorCode.DOCUMENT_NOT_FOUND
    elif "already exists" in error_message.lower() or "duplicate" in error_message.lower():
        error_code = ErrorCode.DUPLICATE_DOCUMENT
    elif "connection" in error_message.lower():
        error_code = ErrorCode.CONNECTION_FAILED
    else:
        error_code = ErrorCode.DATABASE_ERROR
    
    exception = DatabaseException(
        message=f"Database {operation} failed: {error_message}",
        operation=operation,
        collection=collection,
        document_id=document_id,
        cause=error
    )
    exception.error_code = error_code
    
    return exception


def handle_validation_error(
    field: str,
    value: Any,
    constraint: str
) -> ValidationException:
    """
    Create validation exception for field validation failures.
    
    Args:
        field: Field that failed validation
        value: Value that failed validation
        constraint: Validation constraint that was violated
        
    Returns:
        ValidationException with details
    """
    return ValidationException(
        message=f"Validation failed for field '{field}': {constraint}",
        field=field,
        value=value,
        details={"constraint": constraint}
    )


def log_exception(
    logger: logging.Logger,
    exception: CityPulseException,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log exception with standardized format.
    
    Args:
        logger: Logger instance
        exception: Exception to log
        context: Additional context for logging
    """
    log_data = {
        "error_code": exception.error_code.value,
        "message": exception.message,
        "details": exception.details
    }
    
    if context:
        log_data["context"] = context
    
    if exception.cause:
        log_data["cause"] = str(exception.cause)
    
    # Log at appropriate level based on error type
    if exception.error_code in [ErrorCode.INTERNAL_ERROR, ErrorCode.DATABASE_ERROR]:
        logger.error("CityPulse Exception", extra=log_data)
    elif exception.error_code in [ErrorCode.VALIDATION_ERROR, ErrorCode.NOT_FOUND]:
        logger.warning("CityPulse Exception", extra=log_data)
    else:
        logger.info("CityPulse Exception", extra=log_data)


# Exception mapping for common scenarios
def map_http_status_to_error_code(status_code: int) -> ErrorCode:
    """Map HTTP status codes to error codes."""
    mapping = {
        400: ErrorCode.INVALID_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        409: ErrorCode.CONFLICT,
        422: ErrorCode.VALIDATION_ERROR,
        429: ErrorCode.RATE_LIMITED,
        500: ErrorCode.INTERNAL_ERROR,
        502: ErrorCode.EXTERNAL_SERVICE_ERROR,
        503: ErrorCode.SERVICE_UNAVAILABLE,
        504: ErrorCode.API_TIMEOUT
    }
    return mapping.get(status_code, ErrorCode.INTERNAL_ERROR)


class ErrorResponse(BaseModel):
    """Standardized error response model for API responses."""
    error: str = Field(..., description="Error code identifying the type of error")
    message: str = Field(..., description="Human-readable error message")
    status_code: int = Field(..., description="HTTP status code")
    path: str = Field(..., description="API endpoint path where error occurred")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: Optional[str] = Field(None, description="ISO timestamp when error occurred")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "status_code": 422,
                "path": "/v1/events",
                "details": {
                    "field_errors": [
                        {
                            "field": "title",
                            "message": "Title is required"
                        }
                    ]
                },
                "timestamp": "2025-01-07T12:00:00Z"
            }
        }


class ValidationErrorDetail(BaseModel):
    """Details for validation errors."""
    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Optional[Any] = Field(None, description="Invalid value that was provided")


def create_error_response(
    exception: CityPulseException,
    include_details: bool = True
) -> Dict[str, Any]:
    """
    Create standardized error response dictionary.

    Args:
        exception: Exception to convert
        include_details: Whether to include detailed error information

    Returns:
        Error response dictionary
    """
    response = {
        "error": True,
        "error_code": exception.error_code.value,
        "message": exception.message
    }

    if include_details and exception.details:
        response["details"] = exception.details

    return response


# Common error responses for OpenAPI documentation
COMMON_ERROR_RESPONSES = {
    400: {
        "description": "Bad Request",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": "BAD_REQUEST",
                    "message": "Invalid request parameters",
                    "status_code": 400,
                    "path": "/v1/events"
                }
            }
        }
    },
    401: {
        "description": "Unauthorized",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": "UNAUTHORIZED",
                    "message": "Authentication required",
                    "status_code": 401,
                    "path": "/v1/events"
                }
            }
        }
    },
    404: {
        "description": "Not Found",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": "NOT_FOUND",
                    "message": "Resource not found",
                    "status_code": 404,
                    "path": "/v1/events/123"
                }
            }
        }
    },
    422: {
        "description": "Validation Error",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "status_code": 422,
                    "path": "/v1/events",
                    "details": {
                        "field_errors": [
                            {
                                "field": "title",
                                "message": "Title is required"
                            }
                        ]
                    }
                }
            }
        }
    },
    500: {
        "description": "Internal Server Error",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "status_code": 500,
                    "path": "/v1/events"
                }
            }
        }
    }
}


# Export all exception classes and utilities
__all__ = [
    "ErrorCode",
    "CityPulseException",
    "ValidationException",
    "DatabaseException",
    "ExternalServiceException",
    "BusinessRuleException",
    "ErrorResponse",
    "ValidationErrorDetail",
    "handle_database_error",
    "handle_validation_error",
    "log_exception",
    "map_http_status_to_error_code",
    "create_error_response",
    "COMMON_ERROR_RESPONSES"
]
