"""
Shared data models for CityPulse platform.

This module provides unified data models that can be used across all components
of the CityPulse platform (API, data models, pipelines, etc.).
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field


# Enums for consistent categorization
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
    PENDING = "pending"
    ACTIVE = "active"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class EventSource(str, Enum):
    """Enumeration for the source of the event data."""
    CITIZEN_REPORT = "citizen_report"
    IOT_SENSOR = "iot_sensor"
    SOCIAL_MEDIA = "social_media"
    CITY_OFFICIAL = "city_official"
    AI_DETECTION = "ai_detection"


class FeedbackType(str, Enum):
    """Enumeration for feedback types."""
    GENERAL = "general"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"


class FeedbackStatus(str, Enum):
    """Enumeration for feedback status."""
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class UserRole(str, Enum):
    """Enumeration for user roles."""
    CITIZEN = "citizen"
    AUTHORITY = "authority"
    ADMIN = "admin"
    PUBLIC = "public"
    USER = "user"  # Legacy compatibility
    MODERATOR = "moderator"  # Legacy compatibility


class NotificationPreference(str, Enum):
    """Enumeration for notification preferences."""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"


# Base location model
class Location(BaseModel):
    """Location data model."""
    latitude: float = Field(..., description="Latitude coordinate", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude coordinate", ge=-180, le=180)
    address: Optional[str] = Field(None, description="Human-readable address", max_length=500)
    ward: Optional[str] = Field(None, description="Ward or district name", max_length=100)
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            float: lambda v: round(v, 6)  # Limit precision for coordinates
        }


# Core Event model
class EventCore(BaseModel):
    """Core event data model used across the platform."""
    title: str = Field(..., description="Event title", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Event description", max_length=2000)
    location: Location = Field(..., description="Event location")
    category: EventCategory = Field(..., description="Event category")
    severity: EventSeverity = Field(EventSeverity.MEDIUM, description="Event severity")
    source: EventSource = Field(EventSource.CITIZEN_REPORT, description="Event source")
    status: EventStatus = Field(EventStatus.PENDING, description="Event status")
    user_id: Optional[str] = Field(None, description="User who created the event")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Timestamps
    start_time: Optional[datetime] = Field(None, description="Event start time")
    end_time: Optional[datetime] = Field(None, description="Event end time")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    # AI-related fields
    ai_summary: Optional[str] = Field(None, description="AI-generated summary")
    ai_category: Optional[str] = Field(None, description="AI-suggested category")
    ai_image_tags: Optional[List[str]] = Field(None, description="AI-generated image tags")
    ai_generated_image_url: Optional[str] = Field(None, description="AI-generated image URL")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# API Request models
class CreateEventRequest(BaseModel):
    """Request model for creating a new event."""
    title: str = Field(..., description="Event title", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Event description", max_length=2000)
    location: Location = Field(..., description="Event location")
    category: EventCategory = Field(..., description="Event category")
    severity: Optional[EventSeverity] = Field(EventSeverity.MEDIUM, description="Event severity")
    source: Optional[EventSource] = Field(EventSource.CITIZEN_REPORT, description="Event source")
    media_urls: Optional[List[str]] = Field([], description="URLs of attached media")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")
    
    def to_event_core(self, user_id: str = None) -> EventCore:
        """Convert to EventCore model."""
        return EventCore(
            title=self.title,
            description=self.description,
            location=self.location,
            category=self.category,
            severity=self.severity or EventSeverity.MEDIUM,
            source=self.source or EventSource.CITIZEN_REPORT,
            user_id=user_id,
            metadata=self.metadata or {},
            start_time=datetime.utcnow()
        )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class UpdateEventRequest(BaseModel):
    """Request model for updating an event."""
    title: Optional[str] = Field(None, description="Event title", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Event description", max_length=2000)
    location: Optional[Location] = Field(None, description="Event location")
    category: Optional[EventCategory] = Field(None, description="Event category")
    severity: Optional[EventSeverity] = Field(None, description="Event severity")
    status: Optional[EventStatus] = Field(None, description="Event status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    def to_update_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for updates, excluding None values."""
        data = {}
        for field, value in self.dict(exclude_none=True).items():
            if value is not None:
                data[field] = value
        return data
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


# API Response models
class EventResponse(BaseModel):
    """Response model for event data."""
    id: str = Field(..., description="Event identifier")
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    location: Location = Field(..., description="Event location")
    category: EventCategory = Field(..., description="Event category")
    severity: EventSeverity = Field(..., description="Event severity")
    source: EventSource = Field(..., description="Event source")
    status: EventStatus = Field(..., description="Event status")
    user_id: Optional[str] = Field(None, description="User who created the event")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Timestamps
    start_time: Optional[datetime] = Field(None, description="Event start time")
    end_time: Optional[datetime] = Field(None, description="Event end time")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    # AI-related fields (optional for public responses)
    ai_summary: Optional[str] = Field(None, description="AI-generated summary")
    ai_category: Optional[str] = Field(None, description="AI-suggested category")
    
    @classmethod
    def from_event_core(cls, event_core: EventCore, event_id: str) -> "EventResponse":
        """Create EventResponse from EventCore."""
        return cls(
            id=event_id,
            **event_core.dict()
        )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# User Profile models
class UserProfile(BaseModel):
    """User profile data model."""
    user_id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    display_name: Optional[str] = Field(None, description="User display name")
    role: UserRole = Field(UserRole.CITIZEN, description="User role")
    location: Optional[Location] = Field(None, description="User's primary location")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    last_active: Optional[datetime] = Field(None, description="Last activity timestamp")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# Feedback models
class Feedback(BaseModel):
    """Feedback data model."""
    user_id: str = Field(..., description="User who provided feedback")
    type: FeedbackType = Field(..., description="Type of feedback")
    status: FeedbackStatus = Field(FeedbackStatus.PENDING, description="Feedback status")
    title: str = Field(..., description="Feedback title", max_length=200)
    content: str = Field(..., description="Feedback content", max_length=5000)
    rating: Optional[int] = Field(None, description="Rating (1-5)", ge=1, le=5)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# Utility functions for model conversion
def dict_to_event_core(data: Dict[str, Any]) -> EventCore:
    """Convert dictionary to EventCore model."""
    # Handle location conversion
    if 'location' in data and isinstance(data['location'], dict):
        data['location'] = Location(**data['location'])
    
    # Handle enum conversions
    if 'category' in data and isinstance(data['category'], str):
        data['category'] = EventCategory(data['category'])
    if 'severity' in data and isinstance(data['severity'], str):
        data['severity'] = EventSeverity(data['severity'])
    if 'source' in data and isinstance(data['source'], str):
        data['source'] = EventSource(data['source'])
    if 'status' in data and isinstance(data['status'], str):
        data['status'] = EventStatus(data['status'])
    
    return EventCore(**data)


def event_core_to_dict(event: EventCore) -> Dict[str, Any]:
    """Convert EventCore to dictionary for storage."""
    data = event.dict()
    
    # Convert location to dict if it's a Location object
    if isinstance(data.get('location'), Location):
        data['location'] = data['location'].dict()
    
    return data


# Generic response models
class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# Export all models and enums
__all__ = [
    # Enums
    "EventCategory", "EventSeverity", "EventStatus", "EventSource",
    "FeedbackType", "FeedbackStatus", "UserRole", "NotificationPreference",

    # Base models
    "BaseModel", "Location", "EventCore", "UserProfile", "Feedback",

    # API models
    "CreateEventRequest", "UpdateEventRequest", "EventResponse", "SuccessResponse",

    # Utility functions
    "dict_to_event_core", "event_core_to_dict"
]
