"""
Role-based access control and permissions for CityPulse API.

This module defines user roles and permission checking logic.
"""

from enum import Enum
from typing import Any, Dict, List


class UserRole(Enum):
    """User roles in the CityPulse system."""

    CITIZEN = "citizen"
    AUTHORITY = "authority"
    ADMIN = "admin"
    PUBLIC = "public"  # For API key access


class Permission(Enum):
    """Permissions for various operations."""

    # Event permissions
    READ_EVENTS = "events:read"
    CREATE_EVENTS = "events:create"
    UPDATE_EVENTS = "events:update"
    DELETE_EVENTS = "events:delete"
    UPDATE_EVENT_STATUS = "events:update_status"

    # User permissions
    READ_USERS = "users:read"
    UPDATE_USERS = "users:update"
    DELETE_USERS = "users:delete"
    READ_USER_PROFILES = "users:read_profiles"

    # Feedback permissions
    READ_FEEDBACK = "feedback:read"
    CREATE_FEEDBACK = "feedback:create"
    UPDATE_FEEDBACK = "feedback:update"
    DELETE_FEEDBACK = "feedback:delete"

    # Analytics permissions
    READ_ANALYTICS = "analytics:read"
    READ_DETAILED_ANALYTICS = "analytics:read_detailed"

    # Admin permissions
    MANAGE_USERS = "admin:manage_users"
    MANAGE_SYSTEM = "admin:manage_system"


# Role-based permission mapping
ROLE_PERMISSIONS = {
    UserRole.PUBLIC: [
        Permission.READ_EVENTS,
    ],
    UserRole.CITIZEN: [
        Permission.READ_EVENTS,
        Permission.CREATE_EVENTS,
        Permission.CREATE_FEEDBACK,
        Permission.READ_USER_PROFILES,
        Permission.UPDATE_USERS,  # Own profile only
    ],
    UserRole.AUTHORITY: [
        Permission.READ_EVENTS,
        Permission.CREATE_EVENTS,
        Permission.UPDATE_EVENTS,
        Permission.UPDATE_EVENT_STATUS,
        Permission.READ_FEEDBACK,
        Permission.UPDATE_FEEDBACK,
        Permission.READ_ANALYTICS,
        Permission.READ_USER_PROFILES,
        Permission.READ_USERS,
    ],
    UserRole.ADMIN: [
        # Admins have all permissions
        Permission.READ_EVENTS,
        Permission.CREATE_EVENTS,
        Permission.UPDATE_EVENTS,
        Permission.DELETE_EVENTS,
        Permission.UPDATE_EVENT_STATUS,
        Permission.READ_USERS,
        Permission.UPDATE_USERS,
        Permission.DELETE_USERS,
        Permission.READ_USER_PROFILES,
        Permission.READ_FEEDBACK,
        Permission.CREATE_FEEDBACK,
        Permission.UPDATE_FEEDBACK,
        Permission.DELETE_FEEDBACK,
        Permission.READ_ANALYTICS,
        Permission.READ_DETAILED_ANALYTICS,
        Permission.MANAGE_USERS,
        Permission.MANAGE_SYSTEM,
    ],
}


def get_user_roles(user: Dict[str, Any]) -> List[UserRole]:
    """Extract user roles from user data."""
    if not user:
        return [UserRole.PUBLIC]

    # Handle public API access
    if user.get("role") == "public":
        return [UserRole.PUBLIC]

    # Extract roles from Firebase custom claims or user data
    roles_data = user.get("roles", [])
    if isinstance(roles_data, str):
        roles_data = [roles_data]

    roles = []
    for role_str in roles_data:
        try:
            roles.append(UserRole(role_str.lower()))
        except ValueError:
            continue

    # Default to citizen if no roles specified
    if not roles:
        roles = [UserRole.CITIZEN]

    return roles


def check_permission(user: Dict[str, Any], required_permission: Permission) -> bool:
    """Check if user has the required permission."""
    user_roles = get_user_roles(user)

    for role in user_roles:
        if required_permission in ROLE_PERMISSIONS.get(role, []):
            return True

    return False


def check_role(user: Dict[str, Any], required_role: UserRole) -> bool:
    """Check if user has the required role."""
    user_roles = get_user_roles(user)
    return required_role in user_roles


def can_access_resource(
    user: Dict[str, Any], resource_owner_id: str, permission: Permission
) -> bool:
    """
    Check if user can access a resource, considering ownership.

    Users can typically access their own resources even without explicit permissions.
    """
    # Check if user has the general permission
    if check_permission(user, permission):
        return True

    # Check if user owns the resource
    user_id = user.get("uid")
    if user_id and user_id == resource_owner_id:
        # Users can access their own resources for certain operations
        own_resource_permissions = [
            Permission.READ_USER_PROFILES,
            Permission.UPDATE_USERS,
            Permission.CREATE_FEEDBACK,
        ]
        return permission in own_resource_permissions

    return False


def get_user_permissions(user: Dict[str, Any]) -> List[Permission]:
    """Get all permissions for a user based on their roles."""
    user_roles = get_user_roles(user)
    permissions = set()

    for role in user_roles:
        permissions.update(ROLE_PERMISSIONS.get(role, []))

    return list(permissions)
