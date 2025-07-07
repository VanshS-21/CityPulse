"""
Events API router for CityPulse.

This module provides CRUD endpoints for managing events including
creation, retrieval, updating, and deletion with proper authentication
and authorization.
"""

import logging
import os
import sys
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

# Add parent directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from auth import get_current_user, get_optional_user, require_authority, require_user
from auth.permissions import Permission, can_access_resource, check_permission
from services.event_service import EventService
from utils.filtering import FilterParams, create_filter_params
from utils.pagination import (
    PaginatedResponse,
    PaginationParams,
    create_pagination_params,
)

from shared_exceptions import CityPulseException, create_error_response
from shared_models import (
    CreateEventRequest,
    EventResponse,
    SuccessResponse,
    UpdateEventRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize event service
event_service = EventService()


@router.get(
    "",
    response_model=PaginatedResponse[EventResponse],
    summary="List Events",
    description="Retrieve a paginated list of events with optional filtering",
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
)
async def list_events(
    filters: FilterParams = Depends(create_filter_params),
    pagination: PaginationParams = Depends(create_pagination_params),
    current_user: Dict[str, Any] = Depends(get_optional_user),
) -> PaginatedResponse[EventResponse]:
    """
    List events with pagination and filtering.

    - **Public access**: Available with API key for basic event data
    - **Authenticated access**: Full event details for authenticated users
    - **Filtering**: Support for category, status, location, date range, etc.
    - **Pagination**: Cursor-based and offset-based pagination
    """
    try:
        # Check permissions
        if not current_user or not check_permission(
            current_user, Permission.READ_EVENTS
        ):
            # Public access - return limited data
            if not current_user or current_user.get("role") != "public":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required for full event access",
                )

        # Get events from service
        events = await event_service.list_events(
            filters=filters, pagination=pagination, user=current_user
        )

        return events

    except Exception as e:
        logger.error(f"Error listing events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve events",
        )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get Event",
    description="Retrieve a specific event by ID",
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
)
async def get_event(
    event_id: str, current_user: Dict[str, Any] = Depends(get_optional_user)
) -> EventResponse:
    """
    Get a specific event by ID.

    - **Public access**: Available with API key for basic event data
    - **Authenticated access**: Full event details for authenticated users
    """
    try:
        # Check permissions
        if not current_user or not check_permission(
            current_user, Permission.READ_EVENTS
        ):
            # Public access - return limited data
            if not current_user or current_user.get("role") != "public":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required for full event access",
                )

        # Get event from service
        event = await event_service.get_event(event_id, user=current_user)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID '{event_id}' not found",
            )

        return event

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving event {event_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve event",
        )


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Event",
    description="Create a new event report",
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    },
)
async def create_event(
    event_data: CreateEventRequest, current_user: Dict[str, Any] = Depends(require_user)
) -> EventResponse:
    """
    Create a new event.

    - **Authentication required**: Must be logged in
    - **Permissions**: Citizens can create events
    - **Validation**: Full request validation and sanitization
    """
    try:
        # Check permissions
        if not check_permission(current_user, Permission.CREATE_EVENTS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create events",
            )

        # Create event through service
        event = await event_service.create_event(event_data, user=current_user)

        logger.info(f"Event created: {event.id} by user {current_user.get('uid')}")
        return event

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event",
        )


@router.put(
    "/{event_id}",
    response_model=EventResponse,
    summary="Update Event",
    description="Update an existing event",
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not Found"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    },
)
async def update_event(
    event_id: str,
    event_data: UpdateEventRequest,
    current_user: Dict[str, Any] = Depends(require_user),
) -> EventResponse:
    """
    Update an existing event.

    - **Authentication required**: Must be logged in
    - **Permissions**: Event owner or authority/admin can update
    - **Status updates**: Only authorities can update event status
    """
    try:
        # Get existing event to check ownership
        existing_event = await event_service.get_event(event_id, user=current_user)
        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID '{event_id}' not found",
            )

        # Check permissions
        can_update = check_permission(
            current_user, Permission.UPDATE_EVENTS
        ) or can_access_resource(
            current_user, existing_event.user_id, Permission.UPDATE_EVENTS
        )

        if not can_update:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update this event",
            )

        # Check status update permissions
        if event_data.status and not check_permission(
            current_user, Permission.UPDATE_EVENT_STATUS
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update event status",
            )

        # Update event through service
        event = await event_service.update_event(
            event_id, event_data, user=current_user
        )

        logger.info(f"Event updated: {event_id} by user {current_user.get('uid')}")
        return event

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event",
        )


@router.delete(
    "/{event_id}",
    response_model=SuccessResponse,
    summary="Delete Event",
    description="Delete an event (admin only)",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
)
async def delete_event(
    event_id: str, current_user: Dict[str, Any] = Depends(require_user)
) -> SuccessResponse:
    """
    Delete an event.

    - **Authentication required**: Must be logged in
    - **Permissions**: Admin only
    """
    try:
        # Check permissions (admin only)
        if not check_permission(current_user, Permission.DELETE_EVENTS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete events",
            )

        # Delete event through service
        success = await event_service.delete_event(event_id, user=current_user)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID '{event_id}' not found",
            )

        logger.info(f"Event deleted: {event_id} by user {current_user.get('uid')}")
        return SuccessResponse(
            success=True, message=f"Event '{event_id}' deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete event",
        )
