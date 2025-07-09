"""Response models for CityPulse API."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class FeedbackStatus(str, Enum):
    """Feedback status options."""
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    CLOSED = "closed"


class FeedbackType(str, Enum):
    """Types of feedback."""
    GENERAL = "general"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"


class AnalyticsKPIResponse(BaseModel):
    """Response model for analytics KPIs."""
    
    total_events: int = Field(..., description="Total number of events")
    active_users: int = Field(..., description="Number of active users")
    resolved_issues: int = Field(..., description="Number of resolved issues")
    pending_issues: int = Field(..., description="Number of pending issues")
    response_time_avg: float = Field(..., description="Average response time in hours")
    satisfaction_score: float = Field(..., description="User satisfaction score (0-5)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_events": 1250,
                "active_users": 342,
                "resolved_issues": 890,
                "pending_issues": 156,
                "response_time_avg": 24.5,
                "satisfaction_score": 4.2
            }
        }


class TrendDataPoint(BaseModel):
    """Single data point in a trend."""
    
    date: datetime = Field(..., description="Date of the data point")
    value: float = Field(..., description="Value at this date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-15T00:00:00Z",
                "value": 125.5
            }
        }


class AnalyticsTrendResponse(BaseModel):
    """Response model for analytics trends."""
    
    metric_name: str = Field(..., description="Name of the metric")
    time_period: str = Field(..., description="Time period of the trend")
    data_points: List[TrendDataPoint] = Field(..., description="Trend data points")
    trend_direction: str = Field(..., description="Overall trend direction (up/down/stable)")
    percentage_change: float = Field(..., description="Percentage change over the period")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "Event Reports",
                "time_period": "last_30_days",
                "data_points": [
                    {"date": "2024-01-01T00:00:00Z", "value": 100},
                    {"date": "2024-01-15T00:00:00Z", "value": 125},
                    {"date": "2024-01-30T00:00:00Z", "value": 150}
                ],
                "trend_direction": "up",
                "percentage_change": 50.0
            }
        }


class FeedbackResponse(BaseModel):
    """Response model for feedback."""

    id: str = Field(..., description="Feedback ID")
    title: str = Field(..., description="Feedback title")
    content: str = Field(..., description="Feedback content")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    status: FeedbackStatus = Field(..., description="Feedback status")
    rating: Optional[int] = Field(None, description="Rating from 1-5")
    contact_email: Optional[str] = Field(None, description="Contact email")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    user_id: Optional[str] = Field(None, description="User ID who submitted feedback")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "feedback_123",
                "title": "Great app!",
                "content": "I love using this platform to report issues.",
                "feedback_type": "compliment",
                "status": "reviewed",
                "rating": 5,
                "contact_email": "user@example.com",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "user_id": "user_456"
            }
        }


class UserProfileResponse(BaseModel):
    """Response model for user profile."""

    id: str = Field(..., description="User ID")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    phone: Optional[str] = Field(None, description="User's phone number")
    address: Optional[str] = Field(None, description="User's address")
    preferences: Optional[dict] = Field(None, description="User preferences")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(..., description="Whether the user account is active")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-123-4567",
                "address": "123 Main St, City, State 12345",
                "preferences": {
                    "notifications": True,
                    "theme": "dark"
                },
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "is_active": True
            }
        }


class SuccessResponse(BaseModel):
    """Generic success response."""

    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[dict] = Field(None, description="Additional response data")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": "123"}
            }
        }
