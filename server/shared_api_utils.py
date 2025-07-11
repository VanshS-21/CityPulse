"""
Shared API utilities for FastAPI routers to eliminate code duplication.
"""

import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from auth.permissions import Permission, check_permission
from shared_exceptions import CityPulseException, create_error_response

logger = logging.getLogger(__name__)


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


def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator to handle common API errors consistently.
    
    Args:
        func: The async function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except CityPulseException as e:
            # Convert custom exceptions to HTTP exceptions
            raise HTTPException(
                status_code=e.status_code,
                detail=e.message
            )
        except Exception as e:
            # Log unexpected errors and return generic error
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
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
