"""Authentication module for CityPulse API."""

from .firebase_auth import (
    FirebaseAuthMiddleware,
    get_current_user,
    get_optional_user,
    require_role,
    require_admin,
    require_authority,
    require_user
)
from .permissions import UserRole, check_permission

__all__ = [
    "FirebaseAuthMiddleware",
    "get_current_user",
    "get_optional_user",
    "require_role",
    "require_admin",
    "require_authority",
    "require_user",
    "UserRole",
    "check_permission",
]
