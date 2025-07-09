"""
User service for CityPulse API.

This module provides business logic for user profile operations including
CRUD operations, data validation, and integration with unified services.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

# Add parent directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from firebase_admin import auth
from models.requests import UpdateUserProfileRequest
from models.responses import UserProfileResponse

from shared_config import get_collections_config, get_config
from shared_exceptions import (
    CityPulseException,
    DatabaseException,
    ErrorCode,
    ValidationException,
    handle_database_error,
    log_exception,
)
from shared_models import UserProfile
from shared_services import get_database_service

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user operations."""

    def __init__(self):
        """Initialize the user service with unified database service."""
        self.config = get_config()
        self.collections = get_collections_config()
        self.db_service = get_database_service()

        # Legacy properties for backward compatibility
        self.users_collection = self.collections.user_profiles

    async def get_user_profile(self, user_id: str) -> Optional[UserProfileResponse]:
        """
        Get a user profile by ID.

        Args:
            user_id: User identifier

        Returns:
            User profile data or None if not found
        """
        try:
            # Get user using unified service
            user_data = self.db_service.get_user_profile(user_id)

            if not user_data:
                return None

            return self._to_user_response(user_data)

        except Exception as e:
            db_error = handle_database_error("get", self.users_collection, e, user_id)
            log_exception(logger, db_error, {"user_id": user_id})
            raise db_error

    async def create_user_profile(self, user: Dict[str, Any]) -> UserProfileResponse:
        """
        Create a new user profile from Firebase Auth user.

        Args:
            user: Firebase Auth user data

        Returns:
            Created user profile data
        """
        try:
            user_id = user.get("uid")
            if not user_id:
                raise ValidationException("User ID is required", field="user_id")

            # Create UserProfile model
            user_profile = UserProfile(
                user_id=user_id,
                email=user.get("email"),
                display_name=user.get("name") or user.get("display_name"),
                photo_url=user.get("picture") or user.get("photo_url"),
                preferences={"language": "en", "theme": "light", "alert_radius": 5},
                notification_settings={"email": True, "push": True, "in_app": True},
                roles=["citizen"],  # Default role
                is_active=True,
            )

            # Convert to dict for storage
            user_doc = user_profile.model_dump()

            # Save using unified service
            self.db_service.add_user_profile(user_id, user_doc)

            # Return created user profile
            user_doc["user_id"] = user_id
            return self._to_user_response(user_doc)

        except Exception as e:
            db_error = handle_database_error(
                "create", self.users_collection, e, user_id
            )
            log_exception(logger, db_error, {"user_id": user_id})
            raise db_error

    async def update_user_profile(
        self,
        user_id: str,
        profile_data: UpdateUserProfileRequest,
        current_user: Dict[str, Any],
    ) -> Optional[UserProfileResponse]:
        """
        Update an existing user profile.

        Args:
            user_id: User identifier
            profile_data: Profile update data
            current_user: Current user context

        Returns:
            Updated user profile data or None if not found
        """
        try:
            doc_ref = self.firestore_client.collection(self.users_collection).document(
                user_id
            )
            doc = doc_ref.get()

            if not doc.exists:
                return None

            # Prepare update data
            update_data = {"updated_at": datetime.utcnow()}

            if profile_data.display_name is not None:
                update_data["display_name"] = profile_data.display_name

            if profile_data.photo_url is not None:
                update_data["photo_url"] = profile_data.photo_url

            if profile_data.preferences is not None:
                # Merge with existing preferences
                existing_data = doc.to_dict()
                existing_preferences = existing_data.get("preferences", {})
                existing_preferences.update(profile_data.preferences)
                update_data["preferences"] = existing_preferences

            if profile_data.notification_settings is not None:
                # Merge with existing notification settings
                existing_data = doc.to_dict()
                existing_notifications = existing_data.get("notification_settings", {})
                existing_notifications.update(profile_data.notification_settings)
                update_data["notification_settings"] = existing_notifications

            # Update last login if this is the user updating their own profile
            if current_user.get("uid") == user_id:
                update_data["last_login"] = datetime.utcnow()

            # Update in Firestore
            doc_ref.update(update_data)

            # Get updated document
            updated_doc = doc_ref.get()
            updated_data = updated_doc.to_dict()
            updated_data["user_id"] = user_id

            return self._to_user_response(updated_data)

        except Exception as e:
            logger.error(f"Error updating user profile {user_id}: {e}")
            raise

    async def delete_user(self, user_id: str, current_user: Dict[str, Any]) -> bool:
        """
        Delete a user profile and Firebase Auth account.

        Args:
            user_id: User identifier
            current_user: Current user context

        Returns:
            True if deleted, False if not found
        """
        try:
            # Check if user profile exists
            doc_ref = self.firestore_client.collection(self.users_collection).document(
                user_id
            )
            doc = doc_ref.get()

            if not doc.exists:
                return False

            # Delete from Firestore
            doc_ref.delete()

            # Delete from Firebase Auth
            try:
                auth.delete_user(user_id)
            except Exception as e:
                logger.warning(f"Failed to delete Firebase Auth user {user_id}: {e}")
                # Continue even if Firebase Auth deletion fails

            return True

        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise

    async def update_user_roles(
        self, user_id: str, roles: list, current_user: Dict[str, Any]
    ) -> Optional[UserProfileResponse]:
        """
        Update user roles (admin only).

        Args:
            user_id: User identifier
            roles: New roles list
            current_user: Current user context

        Returns:
            Updated user profile data or None if not found
        """
        try:
            doc_ref = self.firestore_client.collection(self.users_collection).document(
                user_id
            )
            doc = doc_ref.get()

            if not doc.exists:
                return None

            # Update roles
            update_data = {"roles": roles, "updated_at": datetime.utcnow()}

            doc_ref.update(update_data)

            # Also update Firebase Auth custom claims
            try:
                auth.set_custom_user_claims(user_id, {"roles": roles})
            except Exception as e:
                logger.warning(
                    f"Failed to update Firebase Auth claims for {user_id}: {e}"
                )

            # Get updated document
            updated_doc = doc_ref.get()
            updated_data = updated_doc.to_dict()
            updated_data["user_id"] = user_id

            return self._to_user_response(updated_data)

        except Exception as e:
            logger.error(f"Error updating user roles {user_id}: {e}")
            raise

    def _to_user_response(self, user_data: Dict[str, Any]) -> UserProfileResponse:
        """Convert user data to response model."""
        return UserProfileResponse(
            user_id=user_data["user_id"],
            email=user_data.get("email"),
            display_name=user_data.get("display_name"),
            photo_url=user_data.get("photo_url"),
            preferences=user_data.get("preferences", {}),
            notification_settings=user_data.get("notification_settings", {}),
            roles=user_data.get("roles", []),
            is_active=user_data.get("is_active", True),
            last_login=user_data.get("last_login"),
            created_at=user_data["created_at"],
            updated_at=user_data["updated_at"],
        )
