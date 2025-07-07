"""
Event service for CityPulse API.

This module provides business logic for event operations including
CRUD operations, data validation, and integration with Firestore and BigQuery.
"""

import logging
import os
import sys
from typing import Any, Dict, Optional

# Add parent directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.filtering import FilterParams, build_firestore_filters
from utils.pagination import PaginatedResponse, PaginationParams

from shared_config import get_collections_config, get_config
from shared_exceptions import (
    CityPulseException,
    DatabaseException,
    ErrorCode,
    ValidationException,
    handle_database_error,
    log_exception,
)
from shared_models import CreateEventRequest, EventResponse, UpdateEventRequest
from shared_services import get_database_service

logger = logging.getLogger(__name__)


class EventService:
    """Service class for event operations."""

    def __init__(self):
        """Initialize the event service with unified database service."""
        self.config = get_config()
        self.collections = get_collections_config()
        self.db_service = get_database_service()

        # Legacy properties for backward compatibility
        self.events_collection = self.collections.events
        self.bigquery_table = self.config.database.bigquery_events_table

    async def list_events(
        self,
        filters: FilterParams,
        pagination: PaginationParams,
        user: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResponse[EventResponse]:
        """
        List events with filtering and pagination.

        Args:
            filters: Filter parameters
            pagination: Pagination parameters
            user: Current user context

        Returns:
            Paginated list of events
        """
        try:
            # Build filters for unified service
            firestore_filters = build_firestore_filters(filters)

            # Calculate pagination
            offset = (pagination.page - 1) * pagination.limit
            limit = pagination.limit + 1  # +1 to check if there are more

            # Query events using unified service
            events_data = self.db_service.query_documents(
                collection_name=self.events_collection,
                filters=firestore_filters,
                order_by=filters.sort_by if filters.sort_by else "created_at",
                limit=limit,
                offset=offset,
            )

            # Filter sensitive data for public access
            if user and user.get("role") == "public":
                events_data = [self._filter_public_data(event) for event in events_data]

            # Check if there are more results
            has_more = len(events_data) > pagination.limit
            if has_more:
                events_data = events_data[:-1]  # Remove the extra item

            # Convert to response models
            events = [self._to_event_response(data) for data in events_data]

            # Create paginated response
            return PaginatedResponse(
                data=events,
                meta={
                    "page": pagination.page,
                    "limit": pagination.limit,
                    "total_items": None,  # Would need separate count query
                    "total_pages": None,
                    "has_next": has_more,
                    "has_previous": pagination.page > 1,
                    "next_cursor": None,
                    "previous_cursor": None,
                },
            )

        except Exception as e:
            db_error = handle_database_error("list", self.events_collection, e)
            log_exception(
                logger,
                db_error,
                {
                    "filters": filters.model_dump(),
                    "pagination": pagination.model_dump(),
                },
            )
            raise db_error

    async def get_event(
        self, event_id: str, user: Optional[Dict[str, Any]] = None
    ) -> Optional[EventResponse]:
        """
        Get a specific event by ID.

        Args:
            event_id: Event identifier
            user: Current user context

        Returns:
            Event data or None if not found
        """
        try:
            # Get event using unified service
            event_data = self.db_service.get_event(event_id)

            if not event_data:
                return None

            # Filter sensitive data for public access
            if user and user.get("role") == "public":
                event_data = self._filter_public_data(event_data)

            return self._to_event_response(event_data)

        except Exception as e:
            db_error = handle_database_error("get", self.events_collection, e, event_id)
            log_exception(logger, db_error, {"event_id": event_id})
            raise db_error

    def _validate_event_data(
        self, event_data: CreateEventRequest, user: Dict[str, Any]
    ) -> None:
        """Validate event data and user permissions."""
        if not user.get("uid"):
            raise ValidationException("User ID is required", field="user_id")

        # Add business rule validations
        if event_data.severity == "critical" and user.get("role") == "citizen":
            raise ValidationException(
                "Citizens cannot create critical severity events",
                field="severity",
                value=event_data.severity,
            )

    async def create_event(
        self, event_data: CreateEventRequest, user: Dict[str, Any]
    ) -> EventResponse:
        """
        Create a new event.

        Args:
            event_data: Event creation data
            user: Current user context

        Returns:
            Created event data
        """
        try:
            # Validate input data
            self._validate_event_data(event_data, user)
            # Convert request to EventCore model
            event_core = event_data.to_event_core(user_id=user.get("uid"))

            # Add media URLs to metadata if provided
            if event_data.media_urls:
                event_core.metadata["media_urls"] = event_data.media_urls

            # Convert to dict for storage
            event_doc = event_core.model_dump()

            # Save to Firestore using unified service
            event_id = self.db_service.add_event(event_doc)

            # Also save to BigQuery for analytics (async)
            await self._save_to_bigquery(event_id, event_doc)

            # Return created event
            event_doc["id"] = event_id
            return self._to_event_response(event_doc)

        except Exception as e:
            db_error = handle_database_error("create", self.events_collection, e)
            log_exception(logger, db_error, {"event_data": event_data.model_dump()})
            raise db_error

    async def update_event(
        self, event_id: str, event_data: UpdateEventRequest, user: Dict[str, Any]
    ) -> EventResponse:
        """
        Update an existing event.

        Args:
            event_id: Event identifier
            event_data: Event update data
            user: Current user context

        Returns:
            Updated event data
        """
        try:
            # Convert request to update dictionary using shared model
            update_data = event_data.to_update_dict()

            # Update in Firestore using unified service
            self.db_service.update_event(event_id, update_data)

            # Get updated document
            updated_data = self.db_service.get_event(event_id)

            # Update BigQuery (async)
            await self._save_to_bigquery(event_id, updated_data)

            return self._to_event_response(updated_data)

        except Exception as e:
            db_error = handle_database_error(
                "update", self.events_collection, e, event_id
            )
            log_exception(
                logger,
                db_error,
                {"event_id": event_id, "update_data": event_data.model_dump()},
            )
            raise db_error

    async def delete_event(self, event_id: str, user: Dict[str, Any]) -> bool:
        """
        Delete an event.

        Args:
            event_id: Event identifier
            user: Current user context

        Returns:
            True if deleted, False if not found
        """
        try:
            # Check if event exists
            event_data = self.db_service.get_event(event_id)
            if not event_data:
                return False

            # Delete from Firestore using unified service
            self.db_service.delete_event(event_id)

            # Note: In production, consider soft delete or archiving instead
            # Also update BigQuery to mark as deleted

            return True

        except Exception as e:
            db_error = handle_database_error(
                "delete", self.events_collection, e, event_id
            )
            log_exception(logger, db_error, {"event_id": event_id})
            raise db_error

    def _filter_public_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter event data for public access."""
        # Remove sensitive fields for public access
        filtered_data = event_data.copy()

        # Remove user-specific information
        filtered_data.pop("user_id", None)
        filtered_data.pop("metadata", None)

        # Keep only basic location info
        if "location" in filtered_data and "address" in filtered_data["location"]:
            # Generalize address for privacy
            location = filtered_data["location"]
            if location.get("address"):
                # Keep only general area, not specific address
                location["address"] = location.get("ward", "General Area")

        return filtered_data

    def _to_event_response(self, event_data: Dict[str, Any]) -> EventResponse:
        """Convert event data to response model."""
        return EventResponse(
            id=event_data["id"],
            title=event_data["title"],
            description=event_data.get("description"),
            location=event_data["location"],
            start_time=event_data["start_time"],
            end_time=event_data.get("end_time"),
            category=event_data["category"],
            severity=event_data["severity"],
            source=event_data["source"],
            status=event_data["status"],
            user_id=event_data.get("user_id"),
            created_at=event_data["created_at"],
            updated_at=event_data["updated_at"],
            metadata=event_data.get("metadata", {}),
            ai_summary=event_data.get("ai_summary"),
            ai_category=event_data.get("ai_category"),
            ai_image_tags=event_data.get("ai_image_tags"),
            ai_generated_image_url=event_data.get("ai_generated_image_url"),
        )

    async def _save_to_bigquery(self, event_id: str, event_data: Dict[str, Any]):
        """Save event data to BigQuery for analytics."""
        try:
            # Prepare BigQuery row
            row = {
                "event_id": event_id,
                "title": event_data["title"],
                "description": event_data.get("description"),
                "location": f"POINT({event_data['location']['longitude']} {event_data['location']['latitude']})",
                "start_time": event_data["start_time"].isoformat(),
                "end_time": (
                    event_data.get("end_time").isoformat()
                    if event_data.get("end_time")
                    else None
                ),
                "category": event_data["category"],
                "severity": event_data["severity"],
                "source": event_data["source"],
                "status": event_data["status"],
                "user_id": event_data.get("user_id"),
                "created_at": event_data["created_at"].isoformat(),
                "updated_at": event_data["updated_at"].isoformat(),
                "metadata": event_data.get("metadata", {}),
                "ai_summary": event_data.get("ai_summary"),
                "ai_category": event_data.get("ai_category"),
                "ai_image_tags": event_data.get("ai_image_tags", []),
                "ai_generated_image_url": event_data.get("ai_generated_image_url"),
            }

            # Insert into BigQuery
            table = self.bigquery_client.get_table(self.bigquery_table)
            errors = self.bigquery_client.insert_rows_json(table, [row])

            if errors:
                logger.error(f"BigQuery insert errors: {errors}")

        except Exception as e:
            logger.error(f"Error saving to BigQuery: {e}")
            # Don't raise - this is async operation
