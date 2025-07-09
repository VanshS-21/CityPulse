"""
Feedback API router for CityPulse.

This module provides endpoints for managing user feedback and suggestions
with proper authentication and authorization.
"""

import logging
from typing import Any, Dict, List

from auth import get_current_user, require_authority, require_user
from auth.permissions import Permission, check_permission
from fastapi import APIRouter, Depends, HTTPException, status
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared_exceptions import COMMON_ERROR_RESPONSES
from models.requests import CreateFeedbackRequest
from models.responses import FeedbackResponse, SuccessResponse
from services.feedback_service import FeedbackService
from utils.pagination import (
    PaginatedResponse,
    PaginationParams,
    create_pagination_params,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize feedback service
feedback_service = FeedbackService()


@router.get(
    "",
    response_model=PaginatedResponse[FeedbackResponse],
    summary="List Feedback",
    description="Retrieve a paginated list of feedback (authority/admin only)",
    responses=COMMON_ERROR_RESPONSES,
)
async def list_feedback(
    pagination: PaginationParams = Depends(create_pagination_params),
    current_user: Dict[str, Any] = Depends(require_authority),
) -> PaginatedResponse[FeedbackResponse]:
    """
    List feedback with pagination.

    - **Authentication required**: Must be logged in
    - **Permissions**: Authority or admin access required
    """
    try:
        # Check permissions
        if not check_permission(current_user, Permission.READ_FEEDBACK):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to read feedback",
            )

        # Get feedback from service
        feedback_list = await feedback_service.list_feedback(
            pagination=pagination, user=current_user
        )

        return feedback_list

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback",
        )


@router.get(
    "/my",
    response_model=PaginatedResponse[FeedbackResponse],
    summary="List My Feedback",
    description="Retrieve current user's feedback",
    responses=COMMON_ERROR_RESPONSES,
)
async def list_my_feedback(
    pagination: PaginationParams = Depends(create_pagination_params),
    current_user: Dict[str, Any] = Depends(require_user),
) -> PaginatedResponse[FeedbackResponse]:
    """
    List current user's feedback.

    - **Authentication required**: Must be logged in
    - **Permissions**: Users can access their own feedback
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user context"
            )

        # Get user's feedback from service
        feedback_list = await feedback_service.list_user_feedback(
            user_id=user_id, pagination=pagination
        )

        return feedback_list

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing user feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback",
        )


@router.get(
    "/{feedback_id}",
    response_model=FeedbackResponse,
    summary="Get Feedback",
    description="Retrieve a specific feedback by ID",
    responses=COMMON_ERROR_RESPONSES,
)
async def get_feedback(
    feedback_id: str, current_user: Dict[str, Any] = Depends(require_user)
) -> FeedbackResponse:
    """
    Get a specific feedback by ID.

    - **Authentication required**: Must be logged in
    - **Permissions**: Feedback owner or authority/admin can access
    """
    try:
        # Get feedback from service
        feedback = await feedback_service.get_feedback(feedback_id, user=current_user)

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feedback with ID '{feedback_id}' not found",
            )

        # Check permissions
        can_access = check_permission(
            current_user, Permission.READ_FEEDBACK
        ) or feedback.user_id == current_user.get("uid")

        if not can_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this feedback",
            )

        return feedback

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving feedback {feedback_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback",
        )


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Feedback",
    description="Submit new feedback",
    responses=COMMON_ERROR_RESPONSES,
)
async def create_feedback(
    feedback_data: CreateFeedbackRequest,
    current_user: Dict[str, Any] = Depends(require_user),
) -> FeedbackResponse:
    """
    Create new feedback.

    - **Authentication required**: Must be logged in
    - **Permissions**: All authenticated users can submit feedback
    """
    try:
        # Check permissions
        if not check_permission(current_user, Permission.CREATE_FEEDBACK):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create feedback",
            )

        # Create feedback through service
        feedback = await feedback_service.create_feedback(
            feedback_data, user=current_user
        )

        logger.info(
            f"Feedback created: {feedback.id} by user {current_user.get('uid')}"
        )
        return feedback

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create feedback",
        )


@router.put(
    "/{feedback_id}/status",
    response_model=FeedbackResponse,
    summary="Update Feedback Status",
    description="Update feedback status (authority/admin only)",
    responses=COMMON_ERROR_RESPONSES,
)
async def update_feedback_status(
    feedback_id: str,
    status: str,
    admin_notes: str = None,
    current_user: Dict[str, Any] = Depends(require_authority),
) -> FeedbackResponse:
    """
    Update feedback status.

    - **Authentication required**: Must be logged in
    - **Permissions**: Authority or admin access required
    """
    try:
        # Check permissions
        if not check_permission(current_user, Permission.UPDATE_FEEDBACK):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update feedback",
            )

        # Update feedback status through service
        feedback = await feedback_service.update_feedback_status(
            feedback_id=feedback_id,
            status=status,
            admin_notes=admin_notes,
            user=current_user,
        )

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feedback with ID '{feedback_id}' not found",
            )

        logger.info(
            f"Feedback status updated: {feedback_id} by user {current_user.get('uid')}"
        )
        return feedback

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating feedback status {feedback_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update feedback status",
        )


@router.delete(
    "/{feedback_id}",
    response_model=SuccessResponse,
    summary="Delete Feedback",
    description="Delete feedback (admin only)",
    responses=COMMON_ERROR_RESPONSES,
)
async def delete_feedback(
    feedback_id: str, current_user: Dict[str, Any] = Depends(require_user)
) -> SuccessResponse:
    """
    Delete feedback.

    - **Authentication required**: Must be logged in
    - **Permissions**: Admin only or feedback owner
    """
    try:
        # Get feedback to check ownership
        feedback = await feedback_service.get_feedback(feedback_id, user=current_user)
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feedback with ID '{feedback_id}' not found",
            )

        # Check permissions
        can_delete = check_permission(
            current_user, Permission.DELETE_FEEDBACK
        ) or feedback.user_id == current_user.get("uid")

        if not can_delete:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete this feedback",
            )

        # Delete feedback through service
        success = await feedback_service.delete_feedback(feedback_id, user=current_user)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feedback with ID '{feedback_id}' not found",
            )

        logger.info(
            f"Feedback deleted: {feedback_id} by user {current_user.get('uid')}"
        )
        return SuccessResponse(
            success=True, message=f"Feedback '{feedback_id}' deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feedback {feedback_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete feedback",
        )
