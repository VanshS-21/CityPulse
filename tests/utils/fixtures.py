"""
Centralized pytest fixtures for CityPulse testing.
Provides reusable fixtures for common testing scenarios.
"""

import pytest
import os
from typing import Dict, Any
from unittest.mock import patch

# Import test utilities
from .mocks import MockServiceContainer
from .factories import TestDataSets, EventFactory, UserProfileFactory, FeedbackFactory

# Import configuration
import sys
sys.path.append('server')

from shared_config import CityPulseConfig, reset_config


@pytest.fixture
def mock_services():
    """Provide a container with all mock services."""
    container = MockServiceContainer()
    yield container
    container.reset_all()


@pytest.fixture
def test_config():
    """Provide a test configuration instance."""
    # Reset any existing config
    reset_config()
    
    # Set test environment variables
    test_env = {
        'GOOGLE_CLOUD_PROJECT': 'test-project',
        'CITYPULSE_ENV': 'development',
        'DB_BIGQUERY_DATASET': 'test_analytics',
        'API_PORT': '8001',
        'API_DEBUG': 'true'
    }
    
    with patch.dict(os.environ, test_env):
        config = CityPulseConfig()
        yield config
    
    # Clean up
    reset_config()


@pytest.fixture
def sample_data():
    """Provide sample test data for various scenarios."""
    return {
        'complete_event_scenario': TestDataSets.create_complete_event_scenario(),
        'multi_user_scenario': TestDataSets.create_multi_user_scenario(),
        'severity_test_data': TestDataSets.create_severity_test_data(),
        'time_series_data': TestDataSets.create_time_series_data()
    }


@pytest.fixture
def auth_headers():
    """Provide authentication headers for API testing."""
    return {
        "user": {"Authorization": "Bearer test-user-token"},
        "admin": {"Authorization": "Bearer test-admin-token"},
        "moderator": {"Authorization": "Bearer test-moderator-token"}
    }


@pytest.fixture
def test_event():
    """Provide a single test event."""
    return EventFactory.create()


@pytest.fixture
def test_events():
    """Provide multiple test events."""
    return EventFactory.create_batch(5)


@pytest.fixture
def test_user():
    """Provide a single test user."""
    return UserProfileFactory.create()


@pytest.fixture
def test_users():
    """Provide multiple test users."""
    return UserProfileFactory.create_batch(3)


@pytest.fixture
def test_feedback():
    """Provide a single test feedback."""
    return FeedbackFactory.create()


@pytest.fixture
def test_feedback_batch():
    """Provide multiple test feedback items."""
    return FeedbackFactory.create_batch(4)


@pytest.fixture
def admin_user():
    """Provide an admin user."""
    return UserProfileFactory.create_admin()


@pytest.fixture
def citizen_user():
    """Provide a citizen user."""
    return UserProfileFactory.create_citizen()


@pytest.fixture(scope="session")
def browser_config():
    """Browser configuration for E2E testing."""
    return {
        "headless": True,
        "viewport": {"width": 1280, "height": 720},
        "timeout": 30000,
        "slow_mo": 0  # Set to > 0 for debugging
    }


@pytest.fixture
def api_client():
    """API test client fixture."""
    from fastapi.testclient import TestClient
    # This would be imported from the actual API app
    # from main import app
    # return TestClient(app)
    
    # For now, return a mock client
    class MockAPIClient:
        def __init__(self):
            self.base_url = "http://testserver"
        
        def get(self, url, **kwargs):
            return MockResponse(200, {"message": "GET success"})
        
        def post(self, url, **kwargs):
            return MockResponse(201, {"message": "POST success"})
        
        def put(self, url, **kwargs):
            return MockResponse(200, {"message": "PUT success"})
        
        def delete(self, url, **kwargs):
            return MockResponse(204, {"message": "DELETE success"})
    
    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json_data = json_data
        
        def json(self):
            return self._json_data
    
    return MockAPIClient()


@pytest.fixture
def database_cleanup():
    """Fixture to ensure database cleanup after tests."""
    # Setup
    yield
    
    # Cleanup - this would clean up test data from actual databases
    # For now, it's a placeholder
    pass


@pytest.fixture
def temp_files():
    """Fixture for managing temporary files in tests."""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_external_services():
    """Mock all external services for isolated testing."""
    with patch('google.cloud.firestore.Client') as mock_firestore, \
         patch('google.cloud.bigquery.Client') as mock_bigquery, \
         patch('google.cloud.pubsub_v1.PublisherClient') as mock_pubsub, \
         patch('google.cloud.storage.Client') as mock_storage:
        
        yield {
            'firestore': mock_firestore,
            'bigquery': mock_bigquery,
            'pubsub': mock_pubsub,
            'storage': mock_storage
        }


@pytest.fixture
def performance_monitor():
    """Monitor performance during tests."""
    import time
    
    start_time = time.time()
    yield
    end_time = time.time()
    
    execution_time = end_time - start_time
    if execution_time > 5.0:  # Warn if test takes more than 5 seconds
        print(f"Warning: Test took {execution_time:.2f} seconds")


@pytest.fixture(autouse=True)
def reset_environment():
    """Automatically reset environment between tests."""
    # Store original environment
    original_env = os.environ.copy()
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# Parametrized fixtures for testing different scenarios
@pytest.fixture(params=['development', 'staging', 'production'])
def environment_config(request):
    """Test configuration for different environments."""
    env = request.param
    with patch.dict(os.environ, {'CITYPULSE_ENV': env, 'GOOGLE_CLOUD_PROJECT': 'test-project'}):
        reset_config()
        config = CityPulseConfig()
        yield config
        reset_config()


@pytest.fixture(params=[1, 5, 10, 50])
def batch_sizes(request):
    """Different batch sizes for testing scalability."""
    return request.param


@pytest.fixture(params=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])
def event_severities(request):
    """Different event severities for testing."""
    from shared_models import EventSeverity
    return EventSeverity(request.param)


@pytest.fixture(params=['CITIZEN', 'ADMIN', 'MODERATOR'])
def user_roles(request):
    """Different user roles for testing."""
    from shared_models import UserRole
    return UserRole(request.param)


# Async fixtures for testing async operations
@pytest.fixture
async def async_mock_services():
    """Async version of mock services."""
    container = MockServiceContainer()
    yield container
    container.reset_all()


# Scope-based fixtures for expensive operations
@pytest.fixture(scope="session")
def expensive_setup():
    """Expensive setup that runs once per test session."""
    # This would be used for expensive operations like
    # setting up test databases, loading large datasets, etc.
    print("Performing expensive setup...")
    yield "expensive_resource"
    print("Cleaning up expensive setup...")


@pytest.fixture(scope="module")
def module_level_data():
    """Data that persists for an entire test module."""
    return {
        'module_start_time': time.time(),
        'test_counter': 0
    }


# Custom markers for different test types
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "external: mark test as requiring external services"
    )


# Add missing import
import time
