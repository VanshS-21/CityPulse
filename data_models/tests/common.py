"""Shared utilities and mock data for tests."""
import unittest
from apache_beam.testing.test_pipeline import TestPipeline
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


class BaseBeamTest(unittest.TestCase):
    """Base class for Apache Beam tests to handle pipeline setup and teardown."""

    def get_pipeline_options(self):
        """Return pipeline options for the test. Subclasses can override this."""
        return None

    def setUp(self):
        """Set up the test pipeline."""
        self.pipeline = TestPipeline(options=self.get_pipeline_options())
        self.pipeline.__enter__()

    def tearDown(self):
        """Tear down the test pipeline."""
        self.pipeline.__exit__(None, None, None)
