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
def firestore_repository(mock_firestore):  # pylint: disable=redefined-outer-name
    """Fixture for a FirestoreRepository instance initialized with a mock client."""
    return FirestoreService(project_id='test-project').repository


def test_event_model_comprehensive():
    """Test comprehensive Event model creation and serialization."""
    start_time = datetime(2023, 1, 1, 12, 0)
    end_time = datetime(2023, 1, 1, 13, 0)
    event = Event(
        title='Comprehensive Test Event',
        description='A more detailed test event',
        location={'latitude': 37.7749, 'longitude': -122.4194},
        start_time=start_time,
        end_time=end_time,
        category=EventCategory.INFRASTRUCTURE,
        severity='high',
        source=EventSource.CITY_OFFICIAL,
        user_id='user456',
        metadata={'source_id': 'official-report-123'}
    )

    # Test serialization
    event_dict = event.model_dump(mode='json')
    assert event_dict['title'] == 'Comprehensive Test Event'
    assert event_dict['description'] == 'A more detailed test event'
    assert event_dict['location'] == {'latitude': 37.7749, 'longitude': -122.4194}
    assert event_dict['start_time'] == start_time.isoformat()
    assert event_dict['end_time'] == end_time.isoformat()
    assert event_dict['category'] == 'infrastructure'
    assert event_dict['severity'] == 'high'
    assert event_dict['source'] == 'city_official'
    assert event_dict['status'] == 'active'  # Default value
    assert event_dict['user_id'] == 'user456'
    assert event_dict['metadata'] == {'source_id': 'official-report-123'}

    # Test deserialization with doc_id
    new_event = Event(id='event-abc', **event.model_dump(exclude={'id'}))
    assert new_event.id == 'event-abc'
    assert new_event.title == 'Comprehensive Test Event'
    assert new_event.category == EventCategory.INFRASTRUCTURE
    assert new_event.to_dict() is not None


@pytest.mark.parametrize("category", list(EventCategory))
def test_event_categories(category):
    """Test all event categories."""
    event = Event(title="Test", category=category)
    assert event.category == category


@pytest.mark.parametrize("severity", ["low", "medium", "high", "critical"])
def test_event_severities(severity):
    """Test all event severities."""
    event = Event(title="Test", severity=severity)
    assert event.severity == severity


@pytest.mark.parametrize("status", ["active", "resolved", "false_positive"])
def test_event_statuses(status):
    """Test all event statuses."""
    event = Event(title="Test", status=status)
    assert event.status == status


@pytest.mark.parametrize("source", list(EventSource))
def test_event_sources(source):
    """Test all event sources."""
    event = Event(title="Test", source=source)
    assert event.source == source


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


@pytest.mark.parametrize("role", list(UserProfile.UserRole))
def test_user_profile_roles(role):
    """Test all user profile roles."""
    profile = UserProfile(user_id="test_user", roles=[role])
    assert profile.has_role(role)


def test_feedback_model_comprehensive():
    """Test comprehensive Feedback model creation and serialization."""
    feedback = Feedback(
        user_id='user789',
        type=FeedbackType.FEATURE_REQUEST,
        title='Add Dark Mode',
        description='A dark mode option would be great for night-time use.',
        metadata={'device': 'mobile'},
        related_entity={'type': 'app_feature', 'id': 'dark_mode'}
    )

    # Test serialization
    feedback_dict = feedback.model_dump(mode='json')
    assert feedback_dict['type'] == 'feature_request'
    assert feedback_dict['title'] == 'Add Dark Mode'
    assert feedback_dict['status'] == 'open'  # Default value
    assert feedback_dict['metadata'] == {'device': 'mobile'}

    # Test deserialization
    new_feedback = Feedback(id='feedback-xyz', **feedback.model_dump(exclude={'id'}))
    assert new_feedback.id == 'feedback-xyz'
    assert new_feedback.type == FeedbackType.FEATURE_REQUEST

    # Test status update
    feedback.update_status(
        FeedbackStatus.IN_REVIEW,
        admin_notes='This is a popular request.',
        assigned_to='dev1'
    )
    assert feedback.status == FeedbackStatus.IN_REVIEW
    assert feedback.admin_notes == 'This is a popular request.'
    assert feedback.assigned_to == 'dev1'
    assert feedback.resolution_date is None

    feedback.update_status(FeedbackStatus.RESOLVED)
    assert feedback.status == FeedbackStatus.RESOLVED
    assert feedback.resolution_date is not None


@pytest.mark.parametrize("feedback_type", list(FeedbackType))
def test_feedback_types(feedback_type):
    """Test all feedback types."""
    feedback = Feedback(user_id="test", type=feedback_type)
    assert feedback.type == feedback_type


@pytest.mark.parametrize("status", list(FeedbackStatus))
def test_feedback_statuses(status):
    """Test all feedback statuses."""
    feedback = Feedback(user_id="test", status=status)
    assert feedback.status == status


def test_firestore_repository_get_document(firestore_repository, mock_firestore):
    """Test getting a document from Firestore."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.id = 'doc123'
    mock_doc.to_dict.return_value = {'title': 'Test Event'}
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc

    event = firestore_repository.get(Event, 'doc123')

    assert event is not None
    assert event.id == 'doc123'
    assert event.title == 'Test Event'


def test_firestore_repository_get_document_not_found(firestore_repository, mock_firestore):
    """Test getting a document that does not exist."""
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc

    event = firestore_repository.get(Event, 'nonexistent')

    assert event is None


def test_firestore_repository_add_document(firestore_repository, mock_firestore):
    """Test adding a document to Firestore."""
    event = Event(title='New Event')
    mock_doc_ref = mock_firestore.collection.return_value.document.return_value
    mock_doc_ref.id = 'new123'

    result_event = firestore_repository.add(event)

    mock_firestore.collection.return_value.document.assert_called_with()
    mock_doc_ref.set.assert_called_once()
    assert result_event.id == 'new123'


def test_firestore_repository_add_document_with_id(firestore_repository, mock_firestore):
    """Test adding a document with a specific ID."""
    event = Event(id='custom123', title='Custom ID Event')
    mock_doc_ref = mock_firestore.collection.return_value.document.return_value

    firestore_repository.add(event)

    mock_firestore.collection.return_value.document.assert_called_with('custom123')
    mock_doc_ref.set.assert_called_once()


def test_firestore_repository_update_document(firestore_repository, mock_firestore):
    """Test updating a document in Firestore."""
    event = Event(id='doc123', title='Updated Title')

    firestore_repository.update(event)

    mock_firestore.collection.return_value.document.assert_called_with('doc123')
    mock_firestore.collection.return_value.document.return_value.update.assert_called_once()


def test_firestore_repository_update_document_no_id(firestore_repository):
    """Test that updating a document without an ID raises an error."""
    event = Event(title='No ID')
    with pytest.raises(ValueError):
        firestore_repository.update(event)


def test_firestore_repository_delete_document(firestore_repository, mock_firestore):
    """Test deleting a document from Firestore."""
    firestore_repository.delete(Event, 'doc123')

    mock_firestore.collection.return_value.document.assert_called_with('doc123')
    mock_firestore.collection.return_value.document.return_value.delete.assert_called_once()


def test_firestore_repository_query_documents(firestore_repository, mock_firestore):
    """Test querying documents in Firestore."""
    mock_doc1 = MagicMock()
    mock_doc1.id = 'doc1'
    mock_doc1.to_dict.return_value = {'title': 'Event 1'}
    mock_doc2 = MagicMock()
    mock_doc2.id = 'doc2'
    mock_doc2.to_dict.return_value = {'title': 'Event 2'}
    mock_firestore.collection.return_value.where.return_value.stream.return_value = [
        mock_doc1, mock_doc2
    ]

    events = firestore_repository.query(Event, status=('==', 'active'))

    assert len(events) == 2
    assert events[0].id == 'doc1'
    assert events[1].title == 'Event 2'


def test_firestore_repository_query_no_results(firestore_repository, mock_firestore):
    """Test querying documents with no results."""
    mock_firestore.collection.return_value.where.return_value.stream.return_value = []

    events = firestore_repository.query(Event, status=('==', 'nonexistent'))

    assert len(events) == 0
