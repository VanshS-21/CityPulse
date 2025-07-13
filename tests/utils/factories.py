"""
Test data factories for generating consistent test data.
Uses factory_boy pattern for creating test objects.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from uuid import uuid4

# Import the shared models
import sys
sys.path.append('server')

from shared_models import (
    EventCore, 
    UserProfile, 
    Feedback, 
    Location,
    EventCategory,
    EventSeverity,
    EventStatus,
    EventSource,
    FeedbackType,
    FeedbackStatus,
    UserRole,
    NotificationPreference
)


class BaseFactory:
    """Base factory class with common utilities."""
    
    @staticmethod
    def random_string(length: int = 10) -> str:
        """Generate a random string of specified length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def random_email() -> str:
        """Generate a random email address."""
        username = BaseFactory.random_string(8)
        domain = random.choice(['example.com', 'test.org', 'demo.net'])
        return f"{username}@{domain}"
    
    @staticmethod
    def random_phone() -> str:
        """Generate a random phone number."""
        return f"+1{random.randint(1000000000, 9999999999)}"
    
    @staticmethod
    def random_coordinate() -> float:
        """Generate a random coordinate within reasonable bounds."""
        return round(random.uniform(-90, 90), 6)


class LocationFactory(BaseFactory):
    """Factory for creating Location objects."""
    
    @classmethod
    def create(cls, **kwargs) -> Location:
        """Create a Location object with default or provided values."""
        defaults = {
            'latitude': cls.random_coordinate(),
            'longitude': cls.random_coordinate(),
            'address': f"{random.randint(1, 9999)} {cls.random_string(8)} St",
            'city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
            'state': random.choice(['NY', 'CA', 'IL', 'TX', 'AZ']),
            'country': 'US',
            'postal_code': f"{random.randint(10000, 99999)}"
        }
        defaults.update(kwargs)
        return Location(**defaults)
    
    @classmethod
    def create_batch(cls, count: int, **kwargs) -> list[Location]:
        """Create multiple Location objects."""
        return [cls.create(**kwargs) for _ in range(count)]


class EventFactory(BaseFactory):
    """Factory for creating EventCore objects."""
    
    @classmethod
    def create(cls, **kwargs) -> EventCore:
        """Create an EventCore object with default or provided values."""
        defaults = {
            'title': f"Test Event {cls.random_string(5)}",
            'description': f"This is a test event description {cls.random_string(20)}",
            'category': random.choice(list(EventCategory)),
            'severity': random.choice(list(EventSeverity)),
            'status': random.choice(list(EventStatus)),
            'source': random.choice(list(EventSource)),
            'location': LocationFactory.create(),
            'user_id': str(uuid4()),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'metadata': {
                'test_data': True,
                'factory_created': True,
                'random_key': cls.random_string(10),
                'event_id': str(uuid4())  # Add event_id to metadata for tracking
            }
        }
        defaults.update(kwargs)
        return EventCore(**defaults)
    
    @classmethod
    def create_batch(cls, count: int, **kwargs) -> list[EventCore]:
        """Create multiple EventCore objects."""
        return [cls.create(**kwargs) for _ in range(count)]
    
    @classmethod
    def create_by_category(cls, category: EventCategory, **kwargs) -> EventCore:
        """Create an event with a specific category."""
        kwargs['category'] = category
        return cls.create(**kwargs)
    
    @classmethod
    def create_by_severity(cls, severity: EventSeverity, **kwargs) -> EventCore:
        """Create an event with a specific severity."""
        kwargs['severity'] = severity
        return cls.create(**kwargs)
    
    @classmethod
    def create_recent(cls, hours_ago: int = 1, **kwargs) -> EventCore:
        """Create an event from a specific time ago."""
        created_time = datetime.utcnow() - timedelta(hours=hours_ago)
        kwargs.update({
            'created_at': created_time,
            'updated_at': created_time
        })
        return cls.create(**kwargs)


class UserProfileFactory(BaseFactory):
    """Factory for creating UserProfile objects."""
    
    @classmethod
    def create(cls, **kwargs) -> UserProfile:
        """Create a UserProfile object with default or provided values."""
        defaults = {
            'user_id': str(uuid4()),
            'email': cls.random_email(),
            'display_name': f"Test User {cls.random_string(5)}",
            'role': random.choice(list(UserRole)),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True,
            'metadata': {
                'test_user': True,
                'factory_created': True
            }
        }
        defaults.update(kwargs)
        return UserProfile(**defaults)
    
    @classmethod
    def create_batch(cls, count: int, **kwargs) -> list[UserProfile]:
        """Create multiple UserProfile objects."""
        return [cls.create(**kwargs) for _ in range(count)]
    
    @classmethod
    def create_by_role(cls, role: UserRole, **kwargs) -> UserProfile:
        """Create a user with a specific role."""
        kwargs['role'] = role
        return cls.create(**kwargs)
    
    @classmethod
    def create_admin(cls, **kwargs) -> UserProfile:
        """Create an admin user."""
        return cls.create_by_role(UserRole.ADMIN, **kwargs)
    
    @classmethod
    def create_citizen(cls, **kwargs) -> UserProfile:
        """Create a citizen user."""
        return cls.create_by_role(UserRole.CITIZEN, **kwargs)


class FeedbackFactory(BaseFactory):
    """Factory for creating Feedback objects."""
    
    @classmethod
    def create(cls, **kwargs) -> Feedback:
        """Create a Feedback object with default or provided values."""
        defaults = {
            'user_id': str(uuid4()),
            'type': random.choice(list(FeedbackType)),
            'status': random.choice(list(FeedbackStatus)),
            'title': f"Test Feedback {cls.random_string(5)}",
            'content': f"Test feedback content {cls.random_string(30)}",
            'rating': random.randint(1, 5),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'metadata': {
                'test_feedback': True,
                'factory_created': True,
                'feedback_id': str(uuid4())  # Add feedback_id to metadata for tracking
            }
        }
        defaults.update(kwargs)
        return Feedback(**defaults)
    
    @classmethod
    def create_batch(cls, count: int, **kwargs) -> list[Feedback]:
        """Create multiple Feedback objects."""
        return [cls.create(**kwargs) for _ in range(count)]
    
    @classmethod
    def create_for_user(cls, user_id: str, **kwargs) -> Feedback:
        """Create feedback for a specific user."""
        kwargs['user_id'] = user_id
        return cls.create(**kwargs)
    
    @classmethod
    def create_by_type(cls, feedback_type: FeedbackType, **kwargs) -> Feedback:
        """Create feedback with a specific type."""
        kwargs['type'] = feedback_type
        return cls.create(**kwargs)


class TestDataSets:
    """Pre-defined test data sets for common scenarios."""
    
    @staticmethod
    def create_complete_event_scenario() -> Dict[str, Any]:
        """Create a complete event scenario with related data."""
        user = UserProfileFactory.create_citizen()
        event = EventFactory.create(user_id=user.user_id)
        feedback_list = FeedbackFactory.create_batch(3, user_id=user.user_id)

        return {
            'user': user,
            'event': event,
            'feedback': feedback_list,
            'scenario': 'complete_event_with_feedback'
        }
    
    @staticmethod
    def create_multi_user_scenario() -> Dict[str, Any]:
        """Create a scenario with multiple users and events."""
        admin = UserProfileFactory.create_admin()
        citizens = UserProfileFactory.create_batch(5, role=UserRole.CITIZEN)
        events = []
        
        for citizen in citizens:
            event = EventFactory.create(user_id=citizen.user_id)
            events.append(event)
        
        return {
            'admin': admin,
            'citizens': citizens,
            'events': events,
            'scenario': 'multi_user_events'
        }
    
    @staticmethod
    def create_severity_test_data() -> Dict[str, Any]:
        """Create events with different severity levels."""
        events_by_severity = {}
        
        for severity in EventSeverity:
            events_by_severity[severity.value] = EventFactory.create_batch(
                3, severity=severity
            )
        
        return {
            'events_by_severity': events_by_severity,
            'scenario': 'severity_testing'
        }
    
    @staticmethod
    def create_time_series_data() -> Dict[str, Any]:
        """Create events across different time periods."""
        events = []
        
        # Create events from different time periods
        for hours_ago in [1, 6, 12, 24, 48, 72]:
            event = EventFactory.create_recent(hours_ago=hours_ago)
            events.append(event)
        
        return {
            'events': events,
            'time_periods': [1, 6, 12, 24, 48, 72],
            'scenario': 'time_series_analysis'
        }


# Convenience functions for quick access
def create_test_event(**kwargs) -> EventCore:
    """Quick function to create a test event."""
    return EventFactory.create(**kwargs)


def create_test_user(**kwargs) -> UserProfile:
    """Quick function to create a test user."""
    return UserProfileFactory.create(**kwargs)


def create_test_feedback(**kwargs) -> Feedback:
    """Quick function to create test feedback."""
    return FeedbackFactory.create(**kwargs)


def create_test_location(**kwargs) -> Location:
    """Quick function to create a test location."""
    return LocationFactory.create(**kwargs)
