"""
Comprehensive unit tests for CityPulse Firestore models.
Tests all business logic, validation, and data model functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from typing import Dict, Any

from data_models import (
    Event, UserProfile, Feedback,
    FeedbackStatus, FeedbackType,
    EventCategory, EventSeverity, EventSource, EventStatus,
    UserRole
)
from shared_models import BaseModel, NotificationPreference


class TestBaseModel:
    """Test cases for BaseModel functionality."""
    
    def test_base_model_creation(self):
        """Test BaseModel creation with default values."""
        # Create a concrete implementation for testing
        class TestModel(BaseModel):
            name: str
            value: int = 10
        
        model = TestModel(name="test")
        
        assert model.name == "test"
        assert model.value == 10
        assert model.id is not None
        assert isinstance(model.created_at, datetime)
        assert isinstance(model.updated_at, datetime)
        assert model.created_at == model.updated_at
    
    def test_base_model_custom_id(self):
        """Test BaseModel with custom ID."""
        class TestModel(BaseModel):
            name: str
        
        custom_id = "custom-test-id"
        model = TestModel(id=custom_id, name="test")
        
        assert model.id == custom_id
    
    def test_base_model_to_dict(self):
        """Test BaseModel to_dict conversion."""
        class TestModel(BaseModel):
            name: str
            value: int = 10
        
        model = TestModel(name="test")
        data = model.to_dict()
        
        assert isinstance(data, dict)
        assert data["name"] == "test"
        assert data["value"] == 10
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_base_model_from_dict(self):
        """Test BaseModel from_dict creation."""
        class TestModel(BaseModel):
            name: str
            value: int = 10
        
        data = {
            "id": "test-id",
            "name": "test",
            "value": 20,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        model = TestModel.from_dict(data)
        
        assert model.id == "test-id"
        assert model.name == "test"
        assert model.value == 20


class TestEvent:
    """Test cases for Event model."""
    
    def test_event_creation_minimal(self):
        """Test Event creation with minimal required fields."""
        event = Event(title="Test Event")
        
        assert event.title == "Test Event"
        assert event.description is None
        assert event.location is None
        assert isinstance(event.start_time, datetime)
        assert event.end_time is None
        assert event.category is None
        assert event.severity is None
        assert event.source is None
        assert event.status == EventStatus.ACTIVE
        assert event.user_id is None
        assert event.metadata == {}
    
    def test_event_creation_full(self):
        """Test Event creation with all fields."""
        location = {"lat": 40.7128, "lng": -74.0060}
        metadata = {"reporter": "citizen", "urgency": "high"}
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=2)
        
        event = Event(
            title="Traffic Incident",
            description="Major traffic jam on Main Street",
            location=location,
            start_time=start_time,
            end_time=end_time,
            category=EventCategory.TRAFFIC,
            severity=EventSeverity.HIGH,
            source=EventSource.CITIZEN_REPORT,
            status=EventStatus.ACTIVE,
            user_id="user123",
            metadata=metadata,
            ai_summary="AI-generated summary",
            ai_category="traffic_incident",
            ai_image_tags=["car", "road", "traffic"]
        )
        
        assert event.title == "Traffic Incident"
        assert event.description == "Major traffic jam on Main Street"
        assert event.location == location
        assert event.start_time == start_time
        assert event.end_time == end_time
        assert event.category == EventCategory.TRAFFIC
        assert event.severity == EventSeverity.HIGH
        assert event.source == EventSource.CITIZEN_REPORT
        assert event.status == EventStatus.ACTIVE
        assert event.user_id == "user123"
        assert event.metadata == metadata
        assert event.ai_summary == "AI-generated summary"
        assert event.ai_category == "traffic_incident"
        assert event.ai_image_tags == ["car", "road", "traffic"]
    
    def test_event_validation_title_required(self):
        """Test Event validation for required title field."""
        with pytest.raises(ValueError):
            Event()
    
    def test_event_location_validation(self):
        """Test Event location validation."""
        # Valid location
        valid_location = {"lat": 40.7128, "lng": -74.0060}
        event = Event(title="Test", location=valid_location)
        assert event.location == valid_location
        
        # Invalid location - missing longitude
        with pytest.raises(ValueError):
            Event(title="Test", location={"lat": 40.7128})
        
        # Invalid location - invalid latitude
        with pytest.raises(ValueError):
            Event(title="Test", location={"lat": 91.0, "lng": -74.0060})
    
    def test_event_time_validation(self):
        """Test Event time validation."""
        start_time = datetime.utcnow()
        end_time = start_time - timedelta(hours=1)  # End before start
        
        with pytest.raises(ValueError):
            Event(title="Test", start_time=start_time, end_time=end_time)
    
    def test_event_to_dict(self):
        """Test Event to_dict conversion."""
        event = Event(
            title="Test Event",
            category=EventCategory.TRAFFIC,
            severity=EventSeverity.MEDIUM
        )
        
        data = event.to_dict()
        
        assert data["title"] == "Test Event"
        assert data["category"] == "traffic"
        assert data["severity"] == "medium"
        assert data["status"] == "active"
    
    def test_event_from_dict(self):
        """Test Event from_dict creation."""
        data = {
            "id": "event-123",
            "title": "Test Event",
            "category": "traffic",
            "severity": "high",
            "status": "resolved",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        event = Event.from_dict(data)
        
        assert event.id == "event-123"
        assert event.title == "Test Event"
        assert event.category == EventCategory.TRAFFIC
        assert event.severity == EventSeverity.HIGH
        assert event.status == EventStatus.RESOLVED


class TestUserProfile:
    """Test cases for UserProfile model."""
    
    def test_user_profile_creation_minimal(self):
        """Test UserProfile creation with minimal fields."""
        profile = UserProfile(
            user_id="user123",
            email="test@example.com"
        )
        
        assert profile.user_id == "user123"
        assert profile.email == "test@example.com"
        assert profile.display_name is None
        assert profile.roles == [UserRole.USER]
        assert profile.is_active is True
        assert profile.notification_preferences == {}
    
    def test_user_profile_creation_full(self):
        """Test UserProfile creation with all fields."""
        notification_prefs = {
            NotificationPreference.EMAIL: True,
            NotificationPreference.PUSH: False,
            NotificationPreference.SMS: True
        }
        
        profile = UserProfile(
            user_id="user123",
            email="admin@example.com",
            display_name="Admin User",
            roles=[UserRole.USER, UserRole.ADMIN],
            is_active=True,
            notification_preferences=notification_prefs,
            last_login=datetime.utcnow(),
            profile_picture_url="https://example.com/avatar.jpg"
        )
        
        assert profile.user_id == "user123"
        assert profile.email == "admin@example.com"
        assert profile.display_name == "Admin User"
        assert UserRole.USER in profile.roles
        assert UserRole.ADMIN in profile.roles
        assert profile.is_active is True
        assert profile.notification_preferences == notification_prefs
    
    def test_user_profile_email_validation(self):
        """Test UserProfile email validation."""
        # Valid email
        profile = UserProfile(user_id="user123", email="valid@example.com")
        assert profile.email == "valid@example.com"
        
        # Invalid email
        with pytest.raises(ValueError):
            UserProfile(user_id="user123", email="invalid-email")
    
    def test_user_profile_role_validation(self):
        """Test UserProfile role validation."""
        # Valid roles
        profile = UserProfile(
            user_id="user123",
            email="test@example.com",
            roles=[UserRole.USER, UserRole.MODERATOR]
        )
        assert len(profile.roles) == 2
        
        # Empty roles should default to USER
        profile = UserProfile(
            user_id="user123",
            email="test@example.com",
            roles=[]
        )
        assert profile.roles == [UserRole.USER]
    
    def test_user_profile_has_role(self):
        """Test UserProfile has_role method."""
        profile = UserProfile(
            user_id="user123",
            email="test@example.com",
            roles=[UserRole.USER, UserRole.MODERATOR]
        )
        
        assert profile.has_role(UserRole.USER) is True
        assert profile.has_role(UserRole.MODERATOR) is True
        assert profile.has_role(UserRole.ADMIN) is False
    
    def test_user_profile_add_role(self):
        """Test UserProfile add_role method."""
        profile = UserProfile(
            user_id="user123",
            email="test@example.com"
        )
        
        assert profile.has_role(UserRole.MODERATOR) is False
        profile.add_role(UserRole.MODERATOR)
        assert profile.has_role(UserRole.MODERATOR) is True
        
        # Adding duplicate role should not create duplicates
        profile.add_role(UserRole.MODERATOR)
        assert profile.roles.count(UserRole.MODERATOR) == 1
    
    def test_user_profile_remove_role(self):
        """Test UserProfile remove_role method."""
        profile = UserProfile(
            user_id="user123",
            email="test@example.com",
            roles=[UserRole.USER, UserRole.MODERATOR]
        )
        
        assert profile.has_role(UserRole.MODERATOR) is True
        profile.remove_role(UserRole.MODERATOR)
        assert profile.has_role(UserRole.MODERATOR) is False
        
        # Should not be able to remove USER role (always required)
        with pytest.raises(ValueError):
            profile.remove_role(UserRole.USER)


class TestFeedback:
    """Test cases for Feedback model."""
    
    def test_feedback_creation_minimal(self):
        """Test Feedback creation with minimal fields."""
        feedback = Feedback(
            event_id="event123",
            user_id="user123",
            content="This is helpful feedback"
        )
        
        assert feedback.event_id == "event123"
        assert feedback.user_id == "user123"
        assert feedback.content == "This is helpful feedback"
        assert feedback.feedback_type == FeedbackType.GENERAL
        assert feedback.status == FeedbackStatus.PENDING
        assert feedback.rating is None
        assert feedback.is_anonymous is False
    
    def test_feedback_creation_full(self):
        """Test Feedback creation with all fields."""
        feedback = Feedback(
            event_id="event123",
            user_id="user123",
            content="Detailed feedback with rating",
            feedback_type=FeedbackType.COMPLAINT,
            status=FeedbackStatus.REVIEWED,
            rating=4,
            is_anonymous=True,
            moderator_notes="Reviewed and approved"
        )
        
        assert feedback.event_id == "event123"
        assert feedback.user_id == "user123"
        assert feedback.content == "Detailed feedback with rating"
        assert feedback.feedback_type == FeedbackType.COMPLAINT
        assert feedback.status == FeedbackStatus.REVIEWED
        assert feedback.rating == 4
        assert feedback.is_anonymous is True
        assert feedback.moderator_notes == "Reviewed and approved"
    
    def test_feedback_rating_validation(self):
        """Test Feedback rating validation."""
        # Valid rating
        feedback = Feedback(
            event_id="event123",
            user_id="user123",
            content="Good feedback",
            rating=5
        )
        assert feedback.rating == 5
        
        # Invalid rating - too low
        with pytest.raises(ValueError):
            Feedback(
                event_id="event123",
                user_id="user123",
                content="Bad rating",
                rating=0
            )
        
        # Invalid rating - too high
        with pytest.raises(ValueError):
            Feedback(
                event_id="event123",
                user_id="user123",
                content="Bad rating",
                rating=6
            )
    
    def test_feedback_content_validation(self):
        """Test Feedback content validation."""
        # Valid content
        feedback = Feedback(
            event_id="event123",
            user_id="user123",
            content="This is valid feedback content"
        )
        assert feedback.content == "This is valid feedback content"
        
        # Empty content should raise error
        with pytest.raises(ValueError):
            Feedback(
                event_id="event123",
                user_id="user123",
                content=""
            )
        
        # Content too long should raise error
        long_content = "x" * 1001  # Assuming 1000 char limit
        with pytest.raises(ValueError):
            Feedback(
                event_id="event123",
                user_id="user123",
                content=long_content
            )
    
    def test_feedback_approve(self):
        """Test Feedback approve method."""
        feedback = Feedback(
            event_id="event123",
            user_id="user123",
            content="Test feedback"
        )
        
        assert feedback.status == FeedbackStatus.PENDING
        feedback.approve("Approved by moderator")
        assert feedback.status == FeedbackStatus.APPROVED
        assert feedback.moderator_notes == "Approved by moderator"
    
    def test_feedback_reject(self):
        """Test Feedback reject method."""
        feedback = Feedback(
            event_id="event123",
            user_id="user123",
            content="Test feedback"
        )
        
        assert feedback.status == FeedbackStatus.PENDING
        feedback.reject("Inappropriate content")
        assert feedback.status == FeedbackStatus.REJECTED
        assert feedback.moderator_notes == "Inappropriate content"


# Test fixtures and utilities
@pytest.fixture
def sample_event():
    """Fixture providing a sample Event instance."""
    return Event(
        title="Sample Event",
        description="A sample event for testing",
        location={"lat": 40.7128, "lng": -74.0060},
        category=EventCategory.TRAFFIC,
        severity=EventSeverity.MEDIUM,
        source=EventSource.CITIZEN_REPORT
    )


@pytest.fixture
def sample_user_profile():
    """Fixture providing a sample UserProfile instance."""
    return UserProfile(
        user_id="test-user-123",
        email="test@example.com",
        display_name="Test User",
        roles=[UserRole.USER]
    )


@pytest.fixture
def sample_feedback():
    """Fixture providing a sample Feedback instance."""
    return Feedback(
        event_id="event-123",
        user_id="user-123",
        content="This is sample feedback",
        feedback_type=FeedbackType.GENERAL,
        rating=4
    )


# Integration tests for model interactions
class TestModelIntegrations:
    """Test cases for model interactions and integrations."""
    
    def test_event_with_user_profile(self, sample_event, sample_user_profile):
        """Test Event creation with associated UserProfile."""
        sample_event.user_id = sample_user_profile.user_id
        
        assert sample_event.user_id == sample_user_profile.user_id
        # In a real scenario, we'd test the relationship through the service layer
    
    def test_feedback_with_event(self, sample_feedback, sample_event):
        """Test Feedback creation with associated Event."""
        sample_feedback.event_id = sample_event.id
        
        assert sample_feedback.event_id == sample_event.id
        # In a real scenario, we'd test the relationship through the service layer
    
    def test_model_serialization_roundtrip(self, sample_event):
        """Test model serialization and deserialization."""
        # Convert to dict
        event_dict = sample_event.to_dict()
        
        # Convert back to model
        restored_event = Event.from_dict(event_dict)
        
        # Verify all fields match
        assert restored_event.title == sample_event.title
        assert restored_event.description == sample_event.description
        assert restored_event.location == sample_event.location
        assert restored_event.category == sample_event.category
        assert restored_event.severity == sample_event.severity
        assert restored_event.source == sample_event.source
