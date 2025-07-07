"""Authentication module for CityPulse API."""

from .firebase_auth import FirebaseAuthMiddleware, get_current_user, require_role
from .permissions import UserRole, check_permission

__all__ = [
    "FirebaseAuthMiddleware",
    "get_current_user",
    "require_role",
    "UserRole",
    "check_permission",
]
