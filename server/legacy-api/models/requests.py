"""Request models for CityPulse API."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class FeedbackType(str, Enum):
    """Types of feedback."""
    GENERAL = "general"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"


class EventCategory(str, Enum):
    """Event categories."""
    INFRASTRUCTURE = "infrastructure"
    TRANSPORTATION = "transportation"
    ENVIRONMENT = "environment"
    SAFETY = "safety"
    UTILITIES = "utilities"
    OTHER = "other"


class EventSeverity(str, Enum):
    """Event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CreateFeedbackRequest(BaseModel):
    """Request model for creating feedback."""
    
    title: str = Field(..., min_length=1, max_length=200, description="Feedback title")
    content: str = Field(..., min_length=1, max_length=2000, description="Feedback content")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1-5")
    contact_email: Optional[str] = Field(None, description="Contact email for follow-up")
    
    @validator('contact_email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Great app!",
                "content": "I love using this platform to report issues in my neighborhood.",
                "feedback_type": "compliment",
                "rating": 5,
                "contact_email": "user@example.com"
            }
        }


class CreateEventRequest(BaseModel):
    """Request model for creating an event."""
    
    title: str = Field(..., min_length=1, max_length=200, description="Event title")
    description: str = Field(..., min_length=1, max_length=2000, description="Event description")
    category: EventCategory = Field(..., description="Event category")
    severity: EventSeverity = Field(..., description="Event severity")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    address: Optional[str] = Field(None, max_length=500, description="Street address")
    images: Optional[List[str]] = Field(None, description="List of image URLs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Pothole on Main Street",
                "description": "Large pothole causing traffic issues",
                "category": "infrastructure",
                "severity": "medium",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "address": "123 Main Street, New York, NY",
                "images": ["https://example.com/image1.jpg"]
            }
        }


class UpdateEventRequest(BaseModel):
    """Request model for updating an event."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Event title")
    description: Optional[str] = Field(None, min_length=1, max_length=2000, description="Event description")
    category: Optional[EventCategory] = Field(None, description="Event category")
    severity: Optional[EventSeverity] = Field(None, description="Event severity")
    status: Optional[str] = Field(None, description="Event status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated: Pothole on Main Street",
                "description": "Large pothole causing traffic issues - repair scheduled",
                "status": "in_progress"
            }
        }


class UpdateUserProfileRequest(BaseModel):
    """Request model for updating user profile."""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's full name")
    email: Optional[str] = Field(None, description="User's email address")
    phone: Optional[str] = Field(None, description="User's phone number")
    address: Optional[str] = Field(None, max_length=500, description="User's address")
    preferences: Optional[dict] = Field(None, description="User preferences")

    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-123-4567",
                "address": "123 Main St, City, State 12345",
                "preferences": {
                    "notifications": True,
                    "theme": "dark"
                }
            }
        }
