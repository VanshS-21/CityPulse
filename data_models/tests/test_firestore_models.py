"""Tests for Firestore models and service."""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from data_models import FirestoreService
from data_models.firestore_models.event import Event, EventCategory, EventSource
from data_models.firestore_models.feedback import (
    Feedback, FeedbackStatus, FeedbackType
)
from data_models.firestore_models.user_profile import UserProfile


@pytest.fixture
def mock_firestore():
    """Fixture for a mock Firestore client."""
    with patch('google.cloud.firestore.Client') as mock_client:
        yield mock_client()


@pytest.fixture
def firestore_service(mock_firestore):  # pylint: disable=redefined-outer-name
    """Fixture for a FirestoreService instance initialized with a mock client."""
    # The mock_firestore fixture is not directly used, but it patches the client.
    _ = mock_firestore
    return FirestoreService(project_id='test-project')


def test_event_model():
    """Test Event model creation and serialization."""
    event = Event(
        title='Test Event',
        description='A test event',
        location={'latitude': 37.7749, 'longitude': -122.4194},
        start_time=datetime(2023, 1, 1, 12, 0),
        category=EventCategory.COMMUNITY,
        severity='medium',
        source=EventSource.USER_REPORT,
        user_id='user123'
    )

    # Test serialization
    event_dict = event.model_dump(mode='json')
    assert event_dict['title'] == 'Test Event'
    assert 'location' in event_dict
    assert event_dict['status'] == 'active'  # Default value
    assert event_dict['category'] == 'community'

    # Test deserialization with doc_id
    new_event = Event(id='test123', **event.model_dump(exclude={'id'}))
    assert new_event.title == 'Test Event'
    assert new_event.category == EventCategory.COMMUNITY
    assert new_event.id == 'test123'


def test_user_profile_model():
    """Test UserProfile model creation and serialization."""
    profile = UserProfile(
        user_id='user123',
        email='test@example.com',
        display_name='Test User',
        preferences={'theme': 'dark'},
        roles=['user', 'admin']
    )

    # Test serialization
    profile_dict = profile.model_dump(mode='json')
    assert profile_dict['email'] == 'test@example.com'
    assert 'notification_settings' in profile_dict
    assert 'admin' in profile_dict['roles']

    # Test deserialization with doc_id
    new_profile = UserProfile(
        id='user123', **profile.model_dump(exclude={'id'})
    )
    assert new_profile.email == 'test@example.com'
    assert new_profile.id == 'user123'

    # Test role management
    assert profile.has_role('admin') is True
    profile.remove_role('admin')
    assert profile.has_role('admin') is False
    profile.add_role('admin')
    assert profile.has_role('admin') is True


def test_feedback_model():
    """Test Feedback model creation and serialization."""
    feedback = Feedback(
        user_id='user123',
        type=FeedbackType.BUG,
        title='Test Bug',
        description='This is a test bug',
        metadata={'page': 'home'}
    )

    # Test serialization
    feedback_dict = feedback.model_dump(mode='json')
    assert feedback_dict['type'] == 'bug'
    assert feedback_dict['status'] == 'open'  # Default value

    # Test deserialization with doc_id
    new_feedback = Feedback(
        id='feedback123', **feedback.model_dump(exclude={'id'})
    )
    assert new_feedback.type == FeedbackType.BUG
    assert new_feedback.id == 'feedback123'

    # Test status update
    feedback.update_status(FeedbackStatus.IN_REVIEW, 'Looking into this')
    assert feedback.status == FeedbackStatus.IN_REVIEW
    assert feedback.admin_notes == 'Looking into this'


def test_firestore_service_get_document(firestore_service, mock_firestore):  # pylint: disable=redefined-outer-name
    """Test getting a document from Firestore."""
    # Setup mock
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.id = 'doc123'
    mock_doc.to_dict.return_value = {
        'title': 'Test Event',
        'created_at': '2023-01-01T12:00:00',
        'updated_at': '2023-01-01T12:00:00'
    }
    mock_collection = MagicMock()
    mock_collection.document.return_value.get.return_value = mock_doc
    mock_firestore.collection.return_value = mock_collection

    # Test
    event = firestore_service.get_document(Event, 'doc123')
    assert event is not None
    assert event.id == 'doc123'
    assert event.title == 'Test Event'


def test_firestore_service_create_document(firestore_service, mock_firestore):  # pylint: disable=redefined-outer-name
    """Test creating a document in Firestore."""
    # Setup mock
    mock_doc = MagicMock()
    mock_doc.id = 'new123'
    mock_collection = MagicMock()
    mock_collection.document.return_value.set.return_value = None
    mock_collection.document.return_value.id = 'new123'
    mock_firestore.collection.return_value = mock_collection

    # Test
    event = Event(title='New Event')
    result_event = firestore_service.add_document(event)
    assert result_event.id == 'new123'
    (
        mock_firestore.collection.return_value.document.return_value.set
        .assert_called_once()
    )


def test_firestore_service_query_documents(firestore_service, mock_firestore):  # pylint: disable=redefined-outer-name
    """Test querying documents in Firestore."""
    # Setup mock
    mock_doc1 = MagicMock()
    mock_doc1.id = 'doc1'
    mock_doc1.to_dict.return_value = {
        'title': 'Event 1',
        'created_at': '2023-01-01T12:00:00',
        'updated_at': '2023-01-01T12:00:00'
    }

    mock_doc2 = MagicMock()
    mock_doc2.id = 'doc2'
    mock_doc2.to_dict.return_value = {
        'title': 'Event 2',
        'created_at': '2023-01-01T13:00:00',
        'updated_at': '2023-01-01T13:00:00'
    }

    mock_query = MagicMock()
    mock_query.where.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.stream.return_value = [mock_doc1, mock_doc2]

    mock_collection = MagicMock()
    mock_collection.where.return_value = mock_query
    mock_firestore.collection.return_value = mock_collection

    # Test
    events = firestore_service.query_documents(
        model_class=Event,
        filters=[('status', '==', 'active')],
        order_by='created_at',
        limit=10
    )

    assert len(events) == 2
    assert events[0].id == 'doc1'
    assert events[0].title == 'Event 1'
    assert events[1].id == 'doc2'
    assert events[1].title == 'Event 2'
