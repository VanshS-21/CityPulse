"""
Feedback service for CityPulse API.

This module provides business logic for feedback operations including
CRUD operations, data validation, and integration with unified services.
"""

import logging
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

# Add parent directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.requests import CreateFeedbackRequest
from models.responses import FeedbackResponse
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
from shared_models import Feedback
from shared_services import get_database_service

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service class for feedback operations."""

    def __init__(self):
        """Initialize the feedback service with unified database service."""
        self.config = get_config()
        self.collections = get_collections_config()
        self.db_service = get_database_service()

        # Legacy properties for backward compatibility
        self.feedback_collection = self.collections.feedback

    async def list_feedback(
        self, pagination: PaginationParams, user: Dict[str, Any]
    ) -> PaginatedResponse[FeedbackResponse]:
        """
        List all feedback with pagination (authority/admin only).

        Args:
            pagination: Pagination parameters
            user: Current user context

        Returns:
            Paginated list of feedback
        """
        try:
            # Build Firestore query
            query = self.firestore_client.collection(self.feedback_collection)

            # Apply sorting (newest first)
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)

            # Execute query with pagination
            offset = (pagination.page - 1) * pagination.limit
            query = query.offset(offset).limit(
                pagination.limit + 1
            )  # +1 to check if there are more

            docs = query.stream()
            feedback_data = []

            for doc in docs:
                feedback_item = doc.to_dict()
                feedback_item["id"] = doc.id
                feedback_data.append(feedback_item)

            # Check if there are more results
            has_more = len(feedback_data) > pagination.limit
            if has_more:
                feedback_data = feedback_data[:-1]  # Remove the extra item

            # Convert to response models
            feedback_list = [self._to_feedback_response(data) for data in feedback_data]

            # Create paginated response
            return PaginatedResponse(
                data=feedback_list,
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
            logger.error(f"Error listing feedback: {e}")
            raise

    async def list_user_feedback(
        self, user_id: str, pagination: PaginationParams
    ) -> PaginatedResponse[FeedbackResponse]:
        """
        List feedback for a specific user.

        Args:
            user_id: User identifier
            pagination: Pagination parameters

        Returns:
            Paginated list of user's feedback
        """
        try:
            # Build Firestore query for user's feedback
            query = self.firestore_client.collection(self.feedback_collection)
            query = query.where("user_id", "==", user_id)
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)

            # Execute query with pagination
            offset = (pagination.page - 1) * pagination.limit
            query = query.offset(offset).limit(pagination.limit + 1)

            docs = query.stream()
            feedback_data = []

            for doc in docs:
                feedback_item = doc.to_dict()
                feedback_item["id"] = doc.id
                feedback_data.append(feedback_item)

            # Check if there are more results
            has_more = len(feedback_data) > pagination.limit
            if has_more:
                feedback_data = feedback_data[:-1]

            # Convert to response models
            feedback_list = [self._to_feedback_response(data) for data in feedback_data]

            # Create paginated response
            return PaginatedResponse(
                data=feedback_list,
                meta={
                    "page": pagination.page,
                    "limit": pagination.limit,
                    "total_items": None,
                    "total_pages": None,
                    "has_next": has_more,
                    "has_previous": pagination.page > 1,
                    "next_cursor": None,
                    "previous_cursor": None,
                },
            )

        except Exception as e:
            logger.error(f"Error listing user feedback for {user_id}: {e}")
            raise

    async def get_feedback(
        self, feedback_id: str, user: Dict[str, Any]
    ) -> Optional[FeedbackResponse]:
        """
        Get a specific feedback by ID.

        Args:
            feedback_id: Feedback identifier
            user: Current user context

        Returns:
            Feedback data or None if not found
        """
        try:
            doc_ref = self.firestore_client.collection(
                self.feedback_collection
            ).document(feedback_id)
            doc = doc_ref.get()

            if not doc.exists:
                return None

            feedback_data = doc.to_dict()
            feedback_data["id"] = doc.id

            return self._to_feedback_response(feedback_data)

        except Exception as e:
            logger.error(f"Error getting feedback {feedback_id}: {e}")
            raise

    async def create_feedback(
        self, feedback_data: CreateFeedbackRequest, user: Dict[str, Any]
    ) -> FeedbackResponse:
        """
        Create new feedback.

        Args:
            feedback_data: Feedback creation data
            user: Current user context

        Returns:
            Created feedback data
        """
        try:
            # Generate feedback ID
            feedback_id = str(uuid.uuid4())

            # Prepare feedback document
            now = datetime.utcnow()
            feedback_doc = {
                "user_id": user.get("uid"),
                "type": feedback_data.type,
                "title": feedback_data.title,
                "description": feedback_data.description,
                "status": "open",
                "metadata": feedback_data.metadata or {},
                "admin_notes": None,
                "assigned_to": None,
                "resolution_date": None,
                "related_entity": feedback_data.related_entity,
                "created_at": now,
                "updated_at": now,
            }

            # Add AI feedback specific fields
            if feedback_data.ai_accuracy_rating is not None:
                feedback_doc["ai_accuracy_rating"] = feedback_data.ai_accuracy_rating

            if feedback_data.corrected_category is not None:
                feedback_doc["corrected_category"] = feedback_data.corrected_category

            if feedback_data.corrected_summary is not None:
                feedback_doc["corrected_summary"] = feedback_data.corrected_summary

            # Save to Firestore
            doc_ref = self.firestore_client.collection(
                self.feedback_collection
            ).document(feedback_id)
            doc_ref.set(feedback_doc)

            # Return created feedback
            feedback_doc["id"] = feedback_id
            return self._to_feedback_response(feedback_doc)

        except Exception as e:
            logger.error(f"Error creating feedback: {e}")
            raise

    async def update_feedback_status(
        self,
        feedback_id: str,
        status: str,
        admin_notes: Optional[str],
        user: Dict[str, Any],
    ) -> Optional[FeedbackResponse]:
        """
        Update feedback status.

        Args:
            feedback_id: Feedback identifier
            status: New status
            admin_notes: Admin notes
            user: Current user context

        Returns:
            Updated feedback data or None if not found
        """
        try:
            doc_ref = self.firestore_client.collection(
                self.feedback_collection
            ).document(feedback_id)
            doc = doc_ref.get()

            if not doc.exists:
                return None

            # Prepare update data
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow(),
                "assigned_to": user.get("uid"),
            }

            if admin_notes:
                update_data["admin_notes"] = admin_notes

            if status in ["resolved", "closed"]:
                update_data["resolution_date"] = datetime.utcnow()

            # Update in Firestore
            doc_ref.update(update_data)

            # Get updated document
            updated_doc = doc_ref.get()
            updated_data = updated_doc.to_dict()
            updated_data["id"] = feedback_id

            return self._to_feedback_response(updated_data)

        except Exception as e:
            logger.error(f"Error updating feedback status {feedback_id}: {e}")
            raise

    async def delete_feedback(self, feedback_id: str, user: Dict[str, Any]) -> bool:
        """
        Delete feedback.

        Args:
            feedback_id: Feedback identifier
            user: Current user context

        Returns:
            True if deleted, False if not found
        """
        try:
            doc_ref = self.firestore_client.collection(
                self.feedback_collection
            ).document(feedback_id)
            doc = doc_ref.get()

            if not doc.exists:
                return False

            # Delete from Firestore
            doc_ref.delete()

            return True

        except Exception as e:
            logger.error(f"Error deleting feedback {feedback_id}: {e}")
            raise

    def _to_feedback_response(self, feedback_data: Dict[str, Any]) -> FeedbackResponse:
        """Convert feedback data to response model."""
        return FeedbackResponse(
            id=feedback_data["id"],
            user_id=feedback_data["user_id"],
            type=feedback_data["type"],
            title=feedback_data.get("title"),
            description=feedback_data["description"],
            status=feedback_data["status"],
            metadata=feedback_data.get("metadata", {}),
            admin_notes=feedback_data.get("admin_notes"),
            assigned_to=feedback_data.get("assigned_to"),
            resolution_date=feedback_data.get("resolution_date"),
            related_entity=feedback_data.get("related_entity"),
            created_at=feedback_data["created_at"],
            updated_at=feedback_data["updated_at"],
            ai_accuracy_rating=feedback_data.get("ai_accuracy_rating"),
            corrected_category=feedback_data.get("corrected_category"),
            corrected_summary=feedback_data.get("corrected_summary"),
        )
