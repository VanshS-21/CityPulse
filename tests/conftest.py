"""
Comprehensive test configuration for CityPulse testing framework.
Provides fixtures, utilities, and configuration for all test types.
"""

import pytest
import asyncio
import os
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List, Optional
import logging

# Configure test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Test Environment Configuration
@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture."""
    return {
        "environment": "test",
        "database": {
            "firestore_project": "citypulse-test",
            "bigquery_project": "citypulse-test",
            "bigquery_dataset": "test_analytics"
        },
        "api": {
            "base_url": "http://localhost:8000",
            "timeout": 30
        },
        "frontend": {
            "base_url": "http://localhost:3000",
            "timeout": 10
        },
        "external_services": {
            "pubsub_project": "citypulse-test",
            "storage_bucket": "citypulse-test-media",
            "ai_api_key": "test-api-key"
        }
    }


# Database Fixtures
@pytest.fixture
def mock_firestore_client():
    """Mock Firestore client for testing."""
    with patch('google.cloud.firestore.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock collection and document operations
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc_snapshot = Mock()
        
        mock_client.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc_snapshot
        
        yield mock_client


@pytest.fixture
def mock_bigquery_client():
    """Mock BigQuery client for testing."""
    with patch('google.cloud.bigquery.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock query operations
        mock_job = Mock()
        mock_client.query.return_value = mock_job
        mock_job.result.return_value = []
        
        # Mock table operations
        mock_table = Mock()
        mock_client.get_table.return_value = mock_table
        mock_table.insert_rows_json.return_value = []
        
        yield mock_client


# External Service Fixtures
@pytest.fixture
def mock_pubsub_publisher():
    """Mock Pub/Sub publisher for testing."""
    with patch('google.cloud.pubsub_v1.PublisherClient') as mock_publisher_class:
        mock_publisher = Mock()
        mock_publisher_class.return_value = mock_publisher
        
        # Mock publish operations
        mock_future = Mock()
        mock_future.result.return_value = "test-message-id"
        mock_publisher.publish.return_value = mock_future
        
        yield mock_publisher


@pytest.fixture
def mock_storage_client():
    """Mock Cloud Storage client for testing."""
    with patch('google.cloud.storage.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock bucket and blob operations
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        yield mock_client


@pytest.fixture
def mock_ai_services():
    """Mock AI/ML services for testing."""
    with patch('google.cloud.language_v1.LanguageServiceClient') as mock_language_class:
        mock_language = Mock()
        mock_language_class.return_value = mock_language
        
        # Mock sentiment analysis
        mock_sentiment = Mock()
        mock_sentiment.score = 0.5
        mock_sentiment.magnitude = 0.8
        
        mock_response = Mock()
        mock_response.document_sentiment = mock_sentiment
        mock_language.analyze_sentiment.return_value = mock_response
        
        yield {
            "language": mock_language
        }


# Test Data Fixtures
@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "id": "test-event-123",
        "title": "Test Traffic Incident",
        "description": "Traffic jam on Main Street causing delays",
        "category": "infrastructure",
        "priority": "medium",
        "status": "pending",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "address": "123 Main Street, New York, NY"
        },
        "user_id": "test-user-456",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "metadata": {
            "source": "web_app",
            "reporter_type": "citizen"
        }
    }


@pytest.fixture
def sample_user_data():
    """Sample user profile data for testing."""
    return {
        "user_id": "test-user-123",
        "email": "test@example.com",
        "display_name": "Test User",
        "roles": ["user"],
        "is_active": True,
        "notification_preferences": {
            "email": True,
            "push": True,
            "sms": False
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@pytest.fixture
def sample_feedback_data():
    """Sample feedback data for testing."""
    return {
        "id": "test-feedback-789",
        "event_id": "test-event-123",
        "user_id": "test-user-456",
        "content": "Thank you for addressing this issue quickly!",
        "rating": 5,
        "feedback_type": "compliment",
        "is_anonymous": False,
        "status": "approved",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


# API Testing Fixtures
@pytest.fixture
def api_client():
    """API test client fixture."""
    from fastapi.testclient import TestClient
    from main import app  # Assuming main.py contains the FastAPI app
    
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Authentication headers for API testing."""
    return {
        "user": {"Authorization": "Bearer test-user-token"},
        "admin": {"Authorization": "Bearer test-admin-token"},
        "moderator": {"Authorization": "Bearer test-moderator-token"}
    }


# Browser Testing Fixtures
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
async def browser_page():
    """Browser page fixture for E2E testing."""
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        yield page
        
        await context.close()
        await browser.close()


# Performance Testing Fixtures
@pytest.fixture
def performance_config():
    """Performance testing configuration."""
    return {
        "load_test": {
            "concurrent_users": 10,
            "duration_seconds": 60,
            "ramp_up_seconds": 10
        },
        "stress_test": {
            "concurrent_users": 100,
            "duration_seconds": 300,
            "ramp_up_seconds": 30
        },
        "thresholds": {
            "response_time_p95": 2000,  # 95th percentile < 2 seconds
            "response_time_p99": 5000,  # 99th percentile < 5 seconds
            "error_rate": 0.01  # < 1% error rate
        }
    }


# Security Testing Fixtures
@pytest.fixture
def security_test_data():
    """Security test data and payloads."""
    return {
        "sql_injection": [
            "'; DROP TABLE events; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --"
        ],
        "xss_payloads": [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ],
        "csrf_tokens": [
            "invalid-csrf-token",
            "",
            "expired-token-123"
        ],
        "invalid_auth_tokens": [
            "invalid-jwt-token",
            "expired.jwt.token",
            "malformed-token",
            ""
        ]
    }


# Accessibility Testing Fixtures
@pytest.fixture
def accessibility_config():
    """Accessibility testing configuration."""
    return {
        "standards": ["WCAG2A", "WCAG2AA"],
        "rules": {
            "color_contrast": True,
            "keyboard_navigation": True,
            "screen_reader": True,
            "focus_management": True,
            "semantic_html": True
        },
        "ignore_rules": [
            # Rules to ignore during testing
        ]
    }


# Utility Functions
def create_test_file(content: str, suffix: str = ".txt") -> str:
    """Create a temporary test file with given content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name


def cleanup_test_file(file_path: str) -> None:
    """Clean up a test file."""
    try:
        os.unlink(file_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_test_file():
    """Temporary test file fixture."""
    file_path = None
    
    def _create_file(content: str, suffix: str = ".txt") -> str:
        nonlocal file_path
        file_path = create_test_file(content, suffix)
        return file_path
    
    yield _create_file
    
    if file_path:
        cleanup_test_file(file_path)


# Test Markers
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
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "accessibility: mark test as an accessibility test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke test"
    )


# Test Collection Hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        elif "accessibility" in str(item.fspath):
            item.add_marker(pytest.mark.accessibility)


# Async Test Support
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test Reporting Fixtures
@pytest.fixture(scope="session", autouse=True)
def test_session_setup():
    """Setup for test session."""
    logger.info("Starting CityPulse test session")
    
    # Create test reports directory
    os.makedirs("test-reports", exist_ok=True)
    
    yield
    
    logger.info("Completed CityPulse test session")


@pytest.fixture
def test_metrics():
    """Test metrics collection fixture."""
    metrics = {
        "start_time": datetime.utcnow(),
        "assertions": 0,
        "api_calls": 0,
        "database_operations": 0
    }
    
    yield metrics
    
    metrics["end_time"] = datetime.utcnow()
    metrics["duration"] = (metrics["end_time"] - metrics["start_time"]).total_seconds()
    
    logger.info(f"Test completed in {metrics['duration']:.2f}s with {metrics['assertions']} assertions")


# Environment-specific Fixtures
@pytest.fixture
def test_environment_variables():
    """Set test environment variables."""
    test_env = {
        "ENVIRONMENT": "test",
        "FIRESTORE_PROJECT_ID": "citypulse-test",
        "BIGQUERY_PROJECT_ID": "citypulse-test",
        "PUBSUB_PROJECT_ID": "citypulse-test",
        "STORAGE_BUCKET": "citypulse-test-media",
        "API_BASE_URL": "http://localhost:8000",
        "FRONTEND_BASE_URL": "http://localhost:3000"
    }
    
    # Set environment variables
    for key, value in test_env.items():
        os.environ[key] = value
    
    yield test_env
    
    # Clean up environment variables
    for key in test_env.keys():
        os.environ.pop(key, None)


# Mock Data Generators
class MockDataGenerator:
    """Generate mock data for testing."""
    
    @staticmethod
    def generate_events(count: int = 10) -> List[Dict[str, Any]]:
        """Generate mock event data."""
        events = []
        categories = ["infrastructure", "safety", "environment", "other"]
        priorities = ["low", "medium", "high", "critical"]
        statuses = ["pending", "in_progress", "resolved", "closed"]
        
        for i in range(count):
            events.append({
                "id": f"mock-event-{i}",
                "title": f"Mock Event {i}",
                "description": f"Description for mock event {i}",
                "category": categories[i % len(categories)],
                "priority": priorities[i % len(priorities)],
                "status": statuses[i % len(statuses)],
                "location": {
                    "latitude": 40.7128 + (i * 0.001),
                    "longitude": -74.0060 + (i * 0.001)
                },
                "created_at": datetime.utcnow() - timedelta(days=i),
                "updated_at": datetime.utcnow() - timedelta(hours=i)
            })
        
        return events
    
    @staticmethod
    def generate_users(count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock user data."""
        users = []
        roles = ["user", "moderator", "admin"]
        
        for i in range(count):
            users.append({
                "user_id": f"mock-user-{i}",
                "email": f"user{i}@example.com",
                "display_name": f"Mock User {i}",
                "roles": [roles[i % len(roles)]],
                "is_active": True,
                "created_at": datetime.utcnow() - timedelta(days=i * 10)
            })
        
        return users


@pytest.fixture
def mock_data_generator():
    """Mock data generator fixture."""
    return MockDataGenerator()
