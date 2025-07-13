"""
Enhanced shared API utilities for FastAPI routers with correlation tracking.
"""

import logging
import structlog
from functools import wraps
from typing import Any, Callable, Dict, Optional
from uuid import uuid4

from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse

from auth.permissions import Permission, check_permission
from shared_exceptions import (
    CityPulseException,
    create_error_response,
    error_context,
    ErrorContext
)

logger = structlog.get_logger(__name__)


class APIConstants:
    """Commonly used API constants."""
    
    COMMON_ERROR_RESPONSES = {
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
    
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


def handle_api_errors(operation: str = None):
    """
    Enhanced decorator to handle API errors with correlation tracking.

    Args:
        operation: Name of the operation for logging context

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request information if available
            request = None
            user_id = None
            request_id = None

            # Try to find Request object in args/kwargs
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if request:
                request_id = getattr(request.state, 'request_id', None) or str(uuid4())
                user_id = getattr(request.state, 'user_id', None)

            operation_name = operation or func.__name__

            with error_context(
                operation=operation_name,
                user_id=user_id,
                request_id=request_id,
                function=func.__name__,
                module=func.__module__
            ) as ctx:
                try:
                    result = await func(*args, **kwargs)

                    # Log successful operation
                    logger.info(
                        "API operation completed successfully",
                        correlation_id=ctx.correlation_id,
                        operation=operation_name,
                        user_id=user_id,
                        request_id=request_id
                    )

                    return result

                except HTTPException as e:
                    # Log HTTP exceptions with context
                    logger.warning(
                        "HTTP exception in API operation",
                        correlation_id=ctx.correlation_id,
                        operation=operation_name,
                        status_code=e.status_code,
                        detail=e.detail,
                        user_id=user_id,
                        request_id=request_id
                    )

                    # Add correlation ID to headers if possible
                    if hasattr(e, 'headers') and e.headers:
                        e.headers['X-Correlation-ID'] = ctx.correlation_id
                    else:
                        e.headers = {'X-Correlation-ID': ctx.correlation_id}

                    raise

                except CityPulseException as e:
                    # Update exception with correlation context
                    e.correlation_id = ctx.correlation_id
                    e.user_id = user_id
                    e.request_id = request_id
                    e.operation = operation_name

                    # Log the exception
                    e.log_error(logger)

                    # Convert to HTTP exception with enhanced detail
                    detail = {
                        "message": e.message,
                        "error_code": e.error_code.value,
                        "correlation_id": e.correlation_id,
                        "details": e.details
                    }

                    raise HTTPException(
                        status_code=getattr(e, 'status_code', 500),
                        detail=detail,
                        headers={'X-Correlation-ID': e.correlation_id}
                    )

                except Exception as e:
                    # Log unexpected errors with full context
                    logger.error(
                        "Unexpected error in API operation",
                        correlation_id=ctx.correlation_id,
                        operation=operation_name,
                        error_type=type(e).__name__,
                        error_message=str(e),
                        user_id=user_id,
                        request_id=request_id,
                        exc_info=True
                    )

                    # Create enhanced error response
                    detail = {
                        "message": "Internal server error",
                        "error_code": "INTERNAL_ERROR",
                        "correlation_id": ctx.correlation_id
                    }

                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=detail,
                        headers={'X-Correlation-ID': ctx.correlation_id}
                    )

        return wrapper
    return decorator
    
    return wrapper


def require_permission(permission: Permission):
    """
    Decorator to require specific permission for endpoint access.
    
    Args:
        permission: Required permission
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs (assumes it's passed as dependency)
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not check_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {permission.value} required"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_pagination_params(page: int = 1, size: int = APIConstants.DEFAULT_PAGE_SIZE) -> tuple[int, int]:
    """
    Validate and normalize pagination parameters.
    
    Args:
        page: Page number (1-indexed)
        size: Page size
        
    Returns:
        Tuple of (validated_page, validated_size)
        
    Raises:
        HTTPException: If parameters are invalid
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be >= 1"
        )
    
    if size < 1 or size > APIConstants.MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Page size must be between 1 and {APIConstants.MAX_PAGE_SIZE}"
        )
    
    return page, size


def create_success_response(data: Any, message: str = "Success") -> JSONResponse:
    """
    Create standardized success response.
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        JSONResponse with standardized format
    """
    return JSONResponse(
        content={
            "success": True,
            "message": message,
            "data": data
        }
    )


def create_error_response_json(
    message: str, 
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        JSONResponse with standardized error format
    """
    content = {
        "success": False,
        "error": message
    }
    
    if details:
        content["details"] = details
    
    return JSONResponse(
        content=content,
        status_code=status_code
    )


def log_api_call(endpoint: str, user_id: Optional[str] = None, **kwargs):
    """
    Log API call for monitoring and debugging.
    
    Args:
        endpoint: API endpoint name
        user_id: User ID making the request
        **kwargs: Additional logging context
    """
    context = {
        "endpoint": endpoint,
        "user_id": user_id,
        **kwargs
    }
    
    logger.info(f"API call: {endpoint}", extra=context)


class ResponseBuilder:
    """Builder class for creating consistent API responses."""
    
    def __init__(self):
        self.response_data = {
            "success": True,
            "data": None,
            "message": None,
            "meta": {}
        }
    
    def success(self, data: Any = None) -> 'ResponseBuilder':
        """Set success data."""
        self.response_data["success"] = True
        self.response_data["data"] = data
        return self
    
    def error(self, message: str, details: Any = None) -> 'ResponseBuilder':
        """Set error information."""
        self.response_data["success"] = False
        self.response_data["error"] = message
        if details:
            self.response_data["details"] = details
        return self
    
    def message(self, msg: str) -> 'ResponseBuilder':
        """Set response message."""
        self.response_data["message"] = msg
        return self
    
    def meta(self, key: str, value: Any) -> 'ResponseBuilder':
        """Add metadata."""
        self.response_data["meta"][key] = value
        return self
    
    def pagination(self, page: int, size: int, total: int) -> 'ResponseBuilder':
        """Add pagination metadata."""
        self.response_data["meta"]["pagination"] = {
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size  # Ceiling division
        }
        return self
    
    def build(self, status_code: int = status.HTTP_200_OK) -> JSONResponse:
        """Build the final response."""
        # Remove empty meta if no metadata was added
        if not self.response_data["meta"]:
            del self.response_data["meta"]
        
        return JSONResponse(
            content=self.response_data,
            status_code=status_code
        )


# Convenience functions for common response patterns
def success_response(data: Any = None, message: str = None) -> JSONResponse:
    """Create a success response quickly."""
    builder = ResponseBuilder().success(data)
    if message:
        builder.message(message)
    return builder.build()


def error_response(message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: Any = None) -> JSONResponse:
    """Create an error response quickly."""
    builder = ResponseBuilder().error(message, details)
    return builder.build(status_code)


def paginated_response(data: Any, page: int, size: int, total: int, message: str = None) -> JSONResponse:
    """Create a paginated response quickly."""
    builder = ResponseBuilder().success(data).pagination(page, size, total)
    if message:
        builder.message(message)
    return builder.build()
