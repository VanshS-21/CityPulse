"""
Users API router for CityPulse.

This module provides endpoints for managing user profiles and preferences
with proper authentication and authorization.
"""

import logging
from typing import Any, Dict

from auth import get_current_user, require_admin, require_user
from auth.permissions import Permission, can_access_resource, check_permission
from fastapi import APIRouter, Depends, HTTPException, status
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared_exceptions import COMMON_ERROR_RESPONSES
from models.requests import UpdateUserProfileRequest
from models.responses import SuccessResponse, UserProfileResponse
from services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize user service
user_service = UserService()


@router.get(
    "/{user_id}",
    response_model=UserProfileResponse,
    summary="Get User Profile",
    description="Retrieve a user profile by ID",
    responses=COMMON_ERROR_RESPONSES,
)
async def get_user_profile(
    user_id: str, current_user: Dict[str, Any] = Depends(require_user)
) -> UserProfileResponse:
    """
    Get a user profile.

    - **Authentication required**: Must be logged in
    - **Permissions**: Users can access their own profile, authorities can access any profile
    """
    try:
        # Check permissions
        can_access = check_permission(
            current_user, Permission.READ_USER_PROFILES
        ) or can_access_resource(current_user, user_id, Permission.READ_USER_PROFILES)

        if not can_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this user profile",
            )

        # Get user profile from service
        user_profile = await user_service.get_user_profile(user_id)

        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User profile with ID '{user_id}' not found",
            )

        return user_profile

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user profile {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile",
        )


@router.put(
    "/{user_id}",
    response_model=UserProfileResponse,
    summary="Update User Profile",
    description="Update a user profile",
    responses=COMMON_ERROR_RESPONSES,
)
async def update_user_profile(
    user_id: str,
    profile_data: UpdateUserProfileRequest,
    current_user: Dict[str, Any] = Depends(require_user),
) -> UserProfileResponse:
    """
    Update a user profile.

    - **Authentication required**: Must be logged in
    - **Permissions**: Users can update their own profile, admins can update any profile
    """
    try:
        # Check permissions
        can_update = check_permission(
            current_user, Permission.UPDATE_USERS
        ) or can_access_resource(current_user, user_id, Permission.UPDATE_USERS)

        if not can_update:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update this user profile",
            )

        # Update user profile through service
        user_profile = await user_service.update_user_profile(
            user_id, profile_data, current_user
        )

        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User profile with ID '{user_id}' not found",
            )

        logger.info(
            f"User profile updated: {user_id} by user {current_user.get('uid')}"
        )
        return user_profile

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile",
        )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get Current User Profile",
    description="Get the current authenticated user's profile",
    responses=COMMON_ERROR_RESPONSES,
)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(require_user),
) -> UserProfileResponse:
    """
    Get the current user's profile.

    - **Authentication required**: Must be logged in
    - **Permissions**: Users can always access their own profile
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user context"
            )

        # Get user profile from service
        user_profile = await user_service.get_user_profile(user_id)

        if not user_profile:
            # Create profile if it doesn't exist
            user_profile = await user_service.create_user_profile(current_user)

        return user_profile

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving current user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile",
        )


@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Update Current User Profile",
    description="Update the current authenticated user's profile",
    responses=COMMON_ERROR_RESPONSES,
)
async def update_current_user_profile(
    profile_data: UpdateUserProfileRequest,
    current_user: Dict[str, Any] = Depends(require_user),
) -> UserProfileResponse:
    """
    Update the current user's profile.

    - **Authentication required**: Must be logged in
    - **Permissions**: Users can always update their own profile
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user context"
            )

        # Update user profile through service
        user_profile = await user_service.update_user_profile(
            user_id, profile_data, current_user
        )

        if not user_profile:
            # Create profile if it doesn't exist
            user_profile = await user_service.create_user_profile(current_user)
            # Then update it
            user_profile = await user_service.update_user_profile(
                user_id, profile_data, current_user
            )

        logger.info(f"User profile updated: {user_id} by self")
        return user_profile

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating current user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile",
        )


@router.delete(
    "/{user_id}",
    response_model=SuccessResponse,
    summary="Delete User",
    description="Delete a user account (admin only)",
    responses=COMMON_ERROR_RESPONSES,
)
async def delete_user(
    user_id: str, current_user: Dict[str, Any] = Depends(require_admin)
) -> SuccessResponse:
    """
    Delete a user account.

    - **Authentication required**: Must be logged in
    - **Permissions**: Admin only
    """
    try:
        # Delete user through service
        success = await user_service.delete_user(user_id, current_user)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID '{user_id}' not found",
            )

        logger.info(f"User deleted: {user_id} by admin {current_user.get('uid')}")
        return SuccessResponse(
            success=True, message=f"User '{user_id}' deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )
