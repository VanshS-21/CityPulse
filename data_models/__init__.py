"""
Data models package for CityPulse application.

This package contains all the data models and database interaction code.
Now using shared models for consistency across the platform.
"""

import os
import sys

# Add parent directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from shared_models import (
    EventCategory,
)
from shared_models import EventCore as Event
from shared_models import (
    EventSeverity,
    EventSource,
    EventStatus,
    Feedback,
    FeedbackStatus,
    FeedbackType,
    Location,
    UserProfile,
    UserRole,
)

from .services.firestore_service import FirestoreService

__all__ = [
    "Event",
    "UserProfile",
    "Feedback",
    "FeedbackStatus",
    "FeedbackType",
    "EventCategory",
    "EventSeverity",
    "EventStatus",
    "EventSource",
    "UserRole",
    "Location",
    "FirestoreService",
]
