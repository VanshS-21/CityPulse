"""
Event model for storing and managing city events in Firestore.

This module defines the Event class, which represents various types of city events
like traffic incidents, public safety alerts, and community happenings. It uses Enums
for better type safety and clarity of categorical data.

Example:
    ```python
    # Create a new event
    event = Event(
        title="Road Closure on Main St",
        description="Emergency water main repair.",
        location={"latitude": 34.0522, "longitude": -118.2437},
        start_time=datetime.utcnow(),
        category=EventCategory.INFRASTRUCTURE,
        severity=EventSeverity.HIGH,
        source=EventSource.CITY_OFFICIAL
    )
    
    # To save to Firestore (assuming a firestore_service is available)
    # firestore_service.add(Event.collection_name(), event.to_dict())
    ```
"""
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any, List

from pydantic import Field

from .base_model import BaseModel


class EventCategory(str, Enum):
    """Enumeration for event categories."""
    TRAFFIC = "traffic"
    WEATHER = "weather"
    PUBLIC_SAFETY = "public_safety"
    INFRASTRUCTURE = "infrastructure"
    COMMUNITY = "community"
    OTHER = "other"


class EventSeverity(str, Enum):
    """Enumeration for event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(str, Enum):
    """Enumeration for event status."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class EventSource(str, Enum):
    """Enumeration for the source of the event data."""
    USER_REPORT = "user_report"
    SENSOR = "sensor"
    SOCIAL_MEDIA = "social_media"
    CITY_OFFICIAL = "city_official"


class Event(BaseModel):
    """Represents a single event in the CityPulse system."""
    title: str
    description: Optional[str] = None
    location: Optional[Dict[str, float]] = None
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    category: Optional[EventCategory] = None
    severity: Optional[EventSeverity] = None
    source: Optional[EventSource] = None
    status: EventStatus = Field(default=EventStatus.ACTIVE)
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ai_summary: Optional[str] = None
    ai_category: Optional[str] = None
    ai_image_tags: Optional[List[str]] = None
    ai_generated_image_url: Optional[str] = None

    @classmethod
    def collection_name(cls) -> str:
        """Returns the Firestore collection name for events."""
        return 'events'

    def to_dict(self) -> Dict[str, Any]:
        """Alias for to_firestore_dict for backward compatibility."""
        return self.to_firestore_dict()
