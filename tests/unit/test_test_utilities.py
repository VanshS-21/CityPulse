"""
Tests for the centralized test utilities.
Validates that test factories, mocks, and helpers work correctly.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import patch

# Import test utilities
import sys
sys.path.append('tests')

from utils.factories import (
    EventFactory, UserProfileFactory, FeedbackFactory, LocationFactory,
    TestDataSets, create_test_event, create_test_user, create_test_feedback
)
from utils.mocks import (
    MockFirestoreService, MockBigQueryService, MockPubSubService,
    MockStorageService, MockAIService, MockServiceContainer
)
from utils.helpers import (
    assert_valid_event, assert_valid_user, assert_valid_feedback,
    wait_for_condition, cleanup_test_data, assert_datetime_recent,
    assert_coordinates_valid, assert_json_structure, measure_execution_time
)

# Import shared models
sys.path.append('server')
from shared_models import EventCategory, EventSeverity, UserRole, FeedbackType


class TestFactories:
    """Test the data factories."""
    
    def test_location_factory(self):
        """Test LocationFactory creates valid locations."""
        location = LocationFactory.create()
        
        assert location.latitude is not None
        assert location.longitude is not None
        assert location.address is not None
        assert location.city is not None
        assert location.state is not None
        assert location.country == 'US'
        assert location.postal_code is not None
        
        # Test coordinates are within valid ranges
        assert_coordinates_valid(location.latitude, location.longitude)
    
    def test_location_factory_with_overrides(self):
        """Test LocationFactory with custom values."""
        custom_location = LocationFactory.create(
            city="Test City",
            state="TC",
            country="TEST"
        )
        
        assert custom_location.city == "Test City"
        assert custom_location.state == "TC"
        assert custom_location.country == "TEST"
    
    def test_location_factory_batch(self):
        """Test creating multiple locations."""
        locations = LocationFactory.create_batch(5)
        
        assert len(locations) == 5
        for location in locations:
            assert_coordinates_valid(location.latitude, location.longitude)
    
    def test_event_factory(self):
        """Test EventFactory creates valid events."""
        event = EventFactory.create()

        assert_valid_event(event)
        assert event.category in [cat.value for cat in EventCategory]
        assert event.severity in [sev.value for sev in EventSeverity]
        assert event.location is not None
        assert event.metadata.get('test_data') is True
        assert event.metadata.get('factory_created') is True
    
    def test_event_factory_by_category(self):
        """Test creating events with specific categories."""
        event = EventFactory.create_by_category(EventCategory.POTHOLE)
        assert event.category == EventCategory.POTHOLE
    
    def test_event_factory_by_severity(self):
        """Test creating events with specific severity."""
        event = EventFactory.create_by_severity(EventSeverity.HIGH)
        assert event.severity == EventSeverity.HIGH
    
    def test_event_factory_recent(self):
        """Test creating recent events."""
        event = EventFactory.create_recent(hours_ago=2)
        
        expected_time = datetime.utcnow() - timedelta(hours=2)
        time_diff = abs((event.created_at - expected_time).total_seconds())
        assert time_diff < 60  # Within 1 minute tolerance
    
    def test_user_factory(self):
        """Test UserProfileFactory creates valid users."""
        user = UserProfileFactory.create()

        assert_valid_user(user)
        assert user.role in [role.value for role in UserRole]
        assert "@" in user.email
        assert user.is_active is True
        assert user.metadata.get('test_user') is True
    
    def test_user_factory_by_role(self):
        """Test creating users with specific roles."""
        admin = UserProfileFactory.create_admin()
        citizen = UserProfileFactory.create_citizen()
        
        assert admin.role == UserRole.ADMIN
        assert citizen.role == UserRole.CITIZEN
    
    def test_feedback_factory(self):
        """Test FeedbackFactory creates valid feedback."""
        feedback = FeedbackFactory.create()

        assert_valid_feedback(feedback)
        assert feedback.type in [ftype.value for ftype in FeedbackType]
        assert 1 <= feedback.rating <= 5
        assert feedback.metadata.get('test_feedback') is True
    
    def test_feedback_factory_for_event(self):
        """Test creating feedback for specific events."""
        event_id = "test-event-123"
        feedback = FeedbackFactory.create_for_event(event_id)
        
        assert feedback.event_id == event_id


class TestTestDataSets:
    """Test the predefined test data sets."""
    
    def test_complete_event_scenario(self):
        """Test complete event scenario creation."""
        scenario = TestDataSets.create_complete_event_scenario()
        
        assert 'user' in scenario
        assert 'event' in scenario
        assert 'feedback' in scenario
        assert 'scenario' in scenario
        
        user = scenario['user']
        event = scenario['event']
        feedback_list = scenario['feedback']
        
        assert_valid_user(user)
        assert_valid_event(event)
        assert event.reported_by == user.id
        assert len(feedback_list) == 3
        
        for feedback in feedback_list:
            assert_valid_feedback(feedback)
            assert feedback.event_id == event.id
            assert feedback.user_id == user.id
    
    def test_multi_user_scenario(self):
        """Test multi-user scenario creation."""
        scenario = TestDataSets.create_multi_user_scenario()
        
        assert 'admin' in scenario
        assert 'citizens' in scenario
        assert 'events' in scenario
        
        admin = scenario['admin']
        citizens = scenario['citizens']
        events = scenario['events']
        
        assert admin.role == UserRole.ADMIN
        assert len(citizens) == 5
        assert len(events) == 5
        
        for citizen in citizens:
            assert citizen.role == UserRole.CITIZEN
    
    def test_severity_test_data(self):
        """Test severity test data creation."""
        scenario = TestDataSets.create_severity_test_data()
        
        assert 'events_by_severity' in scenario
        events_by_severity = scenario['events_by_severity']
        
        for severity in EventSeverity:
            assert severity.value in events_by_severity
            events = events_by_severity[severity.value]
            assert len(events) == 3
            
            for event in events:
                assert event.severity == severity
    
    def test_time_series_data(self):
        """Test time series data creation."""
        scenario = TestDataSets.create_time_series_data()
        
        assert 'events' in scenario
        assert 'time_periods' in scenario
        
        events = scenario['events']
        time_periods = scenario['time_periods']
        
        assert len(events) == len(time_periods)
        
        # Events should be ordered by creation time (newest first)
        for i in range(len(events) - 1):
            assert events[i].created_at >= events[i + 1].created_at


class TestMockServices:
    """Test the mock services."""
    
    def test_mock_firestore_service(self):
        """Test MockFirestoreService functionality."""
        mock_firestore = MockFirestoreService()
        
        # Test adding documents
        event = create_test_event()
        doc_id = mock_firestore.add_document(event, 'events')
        
        assert doc_id == event.id
        assert 'events' in mock_firestore.documents
        assert event.id in mock_firestore.documents['events']
        
        # Test getting documents
        retrieved_event = mock_firestore.get_document(event.id, 'events')
        assert retrieved_event == event
        
        # Test querying documents
        results = mock_firestore.query_documents('events')
        assert len(results) == 1
        assert results[0] == event
        
        # Test call history
        assert len(mock_firestore.call_history) == 3
        assert mock_firestore.call_history[0][0] == 'add_document'
    
    def test_mock_firestore_failure_mode(self):
        """Test MockFirestoreService failure mode."""
        mock_firestore = MockFirestoreService()
        mock_firestore.set_failure_mode(True, "Test failure")
        
        event = create_test_event()
        
        with pytest.raises(Exception, match="Test failure"):
            mock_firestore.add_document(event, 'events')
    
    def test_mock_bigquery_service(self):
        """Test MockBigQueryService functionality."""
        mock_bigquery = MockBigQueryService()
        
        # Test inserting rows
        rows = [
            {'id': '1', 'name': 'Test Event 1'},
            {'id': '2', 'name': 'Test Event 2'}
        ]
        
        result = mock_bigquery.insert_rows('events', rows)
        assert result == 2
        
        # Test getting table data
        table_data = mock_bigquery.get_table_data('events')
        assert len(table_data) == 2
        assert table_data[0]['name'] == 'Test Event 1'
        
        # Test queries
        mock_bigquery.set_query_result('select * from events', [{'count': 2}])
        query_result = mock_bigquery.query('SELECT * FROM events')
        assert query_result == [{'count': 2}]
    
    def test_mock_pubsub_service(self):
        """Test MockPubSubService functionality."""
        mock_pubsub = MockPubSubService()
        
        # Test publishing messages
        message = {'event_id': '123', 'type': 'new_event'}
        attributes = {'source': 'test'}
        
        message_id = mock_pubsub.publish_message('test-topic', message, attributes)
        assert message_id is not None
        
        # Test getting messages
        messages = mock_pubsub.get_messages_for_topic('test-topic')
        assert len(messages) == 1
        assert messages[0]['message'] == message
        assert messages[0]['attributes'] == attributes
    
    def test_mock_service_container(self):
        """Test MockServiceContainer functionality."""
        container = MockServiceContainer()
        
        # Test that all services are available
        assert hasattr(container, 'firestore')
        assert hasattr(container, 'bigquery')
        assert hasattr(container, 'pubsub')
        assert hasattr(container, 'storage')
        assert hasattr(container, 'ai')
        
        # Test reset all
        container.firestore.add_document(create_test_event(), 'events')
        container.bigquery.insert_rows('events', [{'id': '1'}])
        
        container.reset_all()
        
        assert len(container.firestore.documents) == 0
        assert len(container.bigquery.tables) == 0
        
        # Test failure mode
        container.set_all_failure_mode(True, "Container failure")
        
        with pytest.raises(Exception, match="Container failure"):
            container.firestore.add_document(create_test_event(), 'events')


class TestHelpers:
    """Test the helper functions."""
    
    def test_assert_valid_event(self):
        """Test event validation helper."""
        valid_event = create_test_event()
        
        # Should not raise any exceptions
        assert_valid_event(valid_event)
        
        # Test with required fields
        assert_valid_event(valid_event, required_fields=['title', 'description'])
    
    def test_assert_valid_user(self):
        """Test user validation helper."""
        valid_user = create_test_user()
        
        # Should not raise any exceptions
        assert_valid_user(valid_user)
        
        # Test with required fields
        assert_valid_user(valid_user, required_fields=['name', 'email'])
    
    def test_wait_for_condition(self):
        """Test wait_for_condition helper."""
        # Test successful condition
        counter = [0]
        
        def increment_condition():
            counter[0] += 1
            return counter[0] >= 3
        
        result = wait_for_condition(increment_condition, timeout=1.0, interval=0.1)
        assert result is True
        assert counter[0] >= 3
    
    def test_wait_for_condition_timeout(self):
        """Test wait_for_condition timeout."""
        def never_true():
            return False
        
        with pytest.raises(TimeoutError, match="Condition not met"):
            wait_for_condition(never_true, timeout=0.2, interval=0.1)
    
    def test_assert_datetime_recent(self):
        """Test datetime recency assertion."""
        recent_time = datetime.utcnow()
        old_time = datetime.utcnow() - timedelta(minutes=5)
        
        # Should not raise
        assert_datetime_recent(recent_time, max_age_seconds=60)
        
        # Should raise
        with pytest.raises(AssertionError):
            assert_datetime_recent(old_time, max_age_seconds=60)
    
    def test_assert_coordinates_valid(self):
        """Test coordinate validation."""
        # Valid coordinates
        assert_coordinates_valid(40.7128, -74.0060)  # New York
        assert_coordinates_valid(0, 0)  # Equator/Prime Meridian
        
        # Invalid coordinates
        with pytest.raises(AssertionError):
            assert_coordinates_valid(91, 0)  # Invalid latitude
        
        with pytest.raises(AssertionError):
            assert_coordinates_valid(0, 181)  # Invalid longitude
    
    def test_assert_json_structure(self):
        """Test JSON structure validation."""
        data = {
            'id': '123',
            'name': 'Test',
            'count': 42,
            'active': True,
            'optional_field': None
        }
        
        expected_structure = {
            'id': str,
            'name': str,
            'count': int,
            'active': bool,
            'optional_field': "optional"
        }
        
        # Should not raise
        assert_json_structure(data, expected_structure)
        
        # Test missing field
        del data['name']
        with pytest.raises(AssertionError, match="Missing field: name"):
            assert_json_structure(data, expected_structure)
    
    def test_measure_execution_time(self):
        """Test execution time measurement."""
        def slow_function():
            time.sleep(0.1)
            return "result"
        
        result, execution_time = measure_execution_time(slow_function)
        
        assert result == "result"
        assert 0.09 <= execution_time <= 0.2  # Allow some tolerance
    
    def test_cleanup_test_data(self):
        """Test test data cleanup."""
        container = MockServiceContainer()
        
        # Add some test data
        container.firestore.add_document(create_test_event(), 'events')
        container.bigquery.insert_rows('events', [{'id': '1'}])
        
        # Clean up specific collections
        cleanup_test_data(container, collections=['events'])
        
        # Verify cleanup
        assert len(container.firestore.documents.get('events', {})) == 0
        assert len(container.bigquery.tables.get('events', [])) == 0


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_create_test_event(self):
        """Test create_test_event convenience function."""
        event = create_test_event(title="Custom Event")
        
        assert_valid_event(event)
        assert event.title == "Custom Event"
    
    def test_create_test_user(self):
        """Test create_test_user convenience function."""
        user = create_test_user(name="Custom User")
        
        assert_valid_user(user)
        assert user.name == "Custom User"
    
    def test_create_test_feedback(self):
        """Test create_test_feedback convenience function."""
        feedback = create_test_feedback(rating=5)
        
        assert_valid_feedback(feedback)
        assert feedback.rating == 5
