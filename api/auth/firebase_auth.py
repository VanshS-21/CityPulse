"""
Firebase Authentication middleware and utilities for CityPulse API.

This module provides Firebase Authentication integration, including middleware
for token verification and dependency injection for protected endpoints.
"""

import logging
import os
from functools import wraps
from typing import Any, Dict, List, Optional

import firebase_admin
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .permissions import UserRole, check_permission

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    # Try to initialize with service account key or use default credentials
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # Use default credentials (for Cloud Run, etc.)
        firebase_admin.initialize_app()

security = HTTPBearer(auto_error=False)


class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to handle Firebase authentication for all requests."""

    # Public endpoints that don't require authentication
    PUBLIC_PATHS = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    # Endpoints that allow API key authentication
    API_KEY_PATHS = {
        "/v1/events",  # GET only for public events
        "/v1/analytics/public",  # Public analytics
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and verify authentication if required."""
        path = request.url.path
        method = request.method

        # Skip authentication for public paths
        if path in self.PUBLIC_PATHS:
            return await call_next(request)

        # Check for API key authentication for public endpoints
        if path in self.API_KEY_PATHS and method == "GET":
            api_key = request.headers.get("X-API-Key")
            if api_key and self._verify_api_key(api_key):
                request.state.user = {"role": "public", "uid": None}
                return await call_next(request)

        # Verify Firebase token for protected endpoints
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header",
            )

        token = auth_header.split(" ")[1]
        try:
            decoded_token = auth.verify_id_token(token)
            request.state.user = decoded_token
        except Exception as e:
            logger.warning(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        return await call_next(request)

    def _verify_api_key(self, api_key: str) -> bool:
        """Verify API key for public endpoints."""
        # In production, this should check against a database or secure store
        valid_api_keys = os.getenv("VALID_API_KEYS", "").split(",")
        return api_key in valid_api_keys


async def get_current_user(request: Request) -> Dict[str, Any]:
    """Dependency to get the current authenticated user."""
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    return request.state.user


async def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    """Dependency to get the current user if authenticated, None otherwise."""
    return getattr(request.state, "user", None)


def require_role(required_roles: List[UserRole]):
    """Decorator to require specific user roles for endpoint access."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs (injected by dependency)
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, dict) and "uid" in value:
                    current_user = value
                    break

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check if user has required role
            user_roles = current_user.get("roles", [])
            if not any(role.value in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Dependency to require admin role."""
    if not check_permission(current_user, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


async def require_authority(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Dependency to require authority role or higher."""
    if not (
        check_permission(current_user, UserRole.AUTHORITY)
        or check_permission(current_user, UserRole.ADMIN)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Authority access required"
        )
    return current_user


async def require_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Dependency to require any authenticated user."""
    return current_user
