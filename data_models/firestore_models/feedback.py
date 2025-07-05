"""
Feedback model for collecting and managing user feedback in Firestore.

This module defines the Feedback class, which is used to store various types of
user-submitted feedback, such as bug reports, feature requests, and general comments.

Example:
    ```python
    # Create a new feedback item
    feedback = Feedback(
        user_id="some_firebase_auth_uid",
        type=FeedbackType.BUG,
        title="App crashes on startup",
        description="The app closes immediately after I open it on my device."
    )

    # To save to Firestore
    # firestore_service.add('user_feedback', feedback.to_dict())
    ```
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import Field
from .base_model import BaseModel


class FeedbackType(str, Enum):
    """Enumeration for the types of user feedback."""
    BUG = 'bug'
    FEATURE_REQUEST = 'feature_request'
    GENERAL = 'general'
    DATA_ISSUE = 'data_issue'
    AI_CORRECTION = 'ai_correction'
    OTHER = 'other'


class FeedbackStatus(str, Enum):
    """Enumeration for the status of feedback items."""
    OPEN = 'open'
    IN_REVIEW = 'in_review'
    RESOLVED = 'resolved'
    WONT_FIX = 'wont_fix'
    DUPLICATE = 'duplicate'


class Feedback(BaseModel):
    """
    Represents a single piece of user feedback.

    This model captures all the necessary information for tracking and addressing
    user feedback, including its type, status, and associated metadata.

    Attributes:
        user_id (str): The ID of the user who submitted the feedback.
        type (FeedbackType): The type of feedback (e.g., 'bug', 'feature_request').
        title (Optional[str]): A brief title for the feedback.
        description (str): The detailed content of the feedback.
        status (FeedbackStatus): The current status of the feedback item.
        metadata (Dict[str, Any]): A dictionary for additional context or data.
        admin_notes (Optional[str]): Notes added by an administrator.
        assigned_to (Optional[str]): The ID of the admin or team member assigned to this feedback.
        resolution_date (Optional[datetime]): The date when the feedback was resolved.
        related_entity (Optional[Dict[str, str]]): A link to another entity,
            e.g., {'type': 'event', 'id': 'event123'}.
    """
    user_id: str
    type: FeedbackType = FeedbackType.GENERAL
    title: Optional[str] = None
    description: str = ""
    status: FeedbackStatus = FeedbackStatus.OPEN
    metadata: Dict[str, Any] = Field(default_factory=dict)
    admin_notes: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_date: Optional[datetime] = None
    related_entity: Optional[Dict[str, str]] = None

    # Fields specific to AI feedback
    ai_accuracy_rating: Optional[int] = None
    corrected_category: Optional[str] = None
    corrected_summary: Optional[str] = None

    @classmethod
    def collection_name(cls) -> str:
        """Returns the Firestore collection name for feedback models."""
        return 'user_feedback'

    def to_firestore_dict(self, exclude_id: bool = True) -> Dict[str, Any]:
        """
        Converts the Feedback instance to a dictionary for Firestore.

        This method prepares the data for storage, converting enums to their string
        values and ensuring all data is in a Firestore-compatible format.

        Returns:
            Dict[str, Any]: A dictionary representation of the feedback.
        """
        data = self.model_dump(exclude={'id'} if exclude_id else None, exclude_none=True)
        return data

    def update_status(
        self, new_status: FeedbackStatus, admin_notes: str = None, assigned_to: str = None
    ):
        """
        Updates the status of the feedback item and sets the resolution date if applicable.

        Args:
            new_status (FeedbackStatus): The new status to set.
            admin_notes (str, optional): Optional notes to add.
            assigned_to (str, optional): Optional assignee ID.
        """
        self.status = new_status
        if self.status in [
            FeedbackStatus.RESOLVED, FeedbackStatus.WONT_FIX, FeedbackStatus.DUPLICATE
        ]:
            self.resolution_date = datetime.utcnow()

        if admin_notes:
            self.admin_notes = admin_notes
        if assigned_to:
            self.assigned_to = assigned_to
