"""Shared utilities and mock data for tests."""
from unittest.mock import MagicMock


def create_mock_firestore_service():
    """Creates a mock FirestoreService for testing."""
    mock_service = MagicMock()
    mock_service.add_document.return_value = None
    return mock_service


MOCK_EVENT_DATA = {
    'id': 'test-event-123',
    'title': 'Community Cleanup Day',
    'description': 'Join us for a community cleanup event.',
    'category': 'community',
    'severity': 'low',
    'status': 'active',
    'source': 'city_official'
}
