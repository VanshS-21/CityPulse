"""
Firestore models for CityPulse application.

This module contains all the Firestore data models.
Now using shared models for consistency across the platform.
"""

import os
import sys

# Add parent directories to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

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
    UserProfile,
    UserRole,
)

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
]
