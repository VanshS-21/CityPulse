"""
User Profile model for storing user-related data in Firestore.

This module defines the UserProfile class, which manages user information such as
contact details, preferences, roles, and activity status. It links to Firebase
Authentication via the `user_id`.

Example:
    ```python
    # Create a new user profile
    profile = UserProfile(
        user_id="some_firebase_auth_uid",
        email="user@example.com",
        display_name="John Doe",
        roles=[UserRole.USER, UserRole.MODERATOR]
    )

    # To save to Firestore
    # firestore_service.set('user_profiles', profile.user_id, profile.to_dict())
    ```
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import Field, model_validator
from .base_model import BaseModel


class UserRole(str, Enum):
    """Defines the roles a user can have within the system."""
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class UserProfile(BaseModel):
    """
    Represents a user's profile in the CityPulse system.

    This model stores extended information about a user beyond what Firebase
    Authentication provides, such as application-specific settings and roles.

    Attributes:
        user_id (str): The unique identifier from Firebase Authentication.
        email (Optional[str]): The user's email address.
        display_name (Optional[str]): The user's public display name.
        photo_url (Optional[str]): A URL to the user's profile picture.
        preferences (Dict[str, Any]): User-specific settings and preferences.
        notification_settings (Dict[str, bool]): Settings for different notification channels.
        roles (List[UserRole]): A list of roles assigned to the user.
        is_active (bool): A flag indicating if the user's account is active.
        last_login (Optional[datetime]): The timestamp of the user's last login.
    """
    user_id: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    notification_settings: Dict[str, bool] = Field(default_factory=lambda: {
        'email': True, 'push': True, 'in_app': True
    })
    roles: List[UserRole] = Field(default_factory=list)
    is_active: bool = True
    last_login: Optional[datetime] = None

    @model_validator(mode='after')
    def set_default_roles(self) -> 'UserProfile':
        """Sets default roles for a user if none are provided."""
        if not self.roles:
            self.roles = [UserRole.USER]
        return self

    @classmethod
    def collection_name(cls) -> str:
        """Returns the Firestore collection name for user profiles."""
        return 'user_profiles'

    def to_firestore_dict(self, exclude_id: bool = True) -> Dict[str, Any]:
        """
        Converts the UserProfile instance to a dictionary for Firestore.

        This method prepares the data for storage, converting enums to their string
        values and ensuring all data is in a Firestore-compatible format.

        Returns:
            Dict[str, Any]: A dictionary representation of the user profile.
        """
        data = self.model_dump(exclude={'id'} if exclude_id else None, exclude_none=True)
        return data

    def has_role(self, role: UserRole) -> bool:
        """
        Checks if the user has a specific role.

        Args:
            role (UserRole): The role to check for.

        Returns:
            bool: True if the user has the role, False otherwise.
        """
        return role in self.roles

    def add_role(self, role: UserRole):
        """
        Adds a role to the user if it's not already present.

        Args:
            role (UserRole): The role to add.
        """
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role: UserRole):
        """
        Removes a role from the user if it exists.

        Args:
            role (UserRole): The role to remove.
        """
        if role in self.roles:
            self.roles.remove(role)
