"""
Test helper functions and utilities.
Provides common testing utilities and assertion helpers.
"""

import time
import json
import asyncio
from typing import Any, Dict, List, Callable, Optional, Union
from datetime import datetime, timedelta
import pytest

# Import shared models
import sys
sys.path.append('server')

from shared_models import EventCore, UserProfile, Feedback


def assert_valid_response(response, expected_status: int = 200, expected_keys: List[str] = None):
    """
    Assert that an API response is valid.
    
    Args:
        response: The response object to validate
        expected_status: Expected HTTP status code
        expected_keys: List of keys that should be present in response JSON
    """
    assert response.status_code == expected_status, f"Expected status {expected_status}, got {response.status_code}"
    
    if expected_keys:
        response_data = response.json()
        for key in expected_keys:
            assert key in response_data, f"Expected key '{key}' not found in response"


def assert_valid_event(event: EventCore, required_fields: List[str] = None):
    """
    Assert that an event object is valid.

    Args:
        event: The event object to validate
        required_fields: List of fields that must be present and non-empty
    """
    assert isinstance(event, EventCore), "Object must be an EventCore instance"
    assert event.title is not None and event.title.strip(), "Event must have a non-empty title"
    assert event.category is not None, "Event must have a category"
    assert event.location is not None, "Event must have a location"
    assert event.severity is not None, "Event must have a severity"
    assert event.source is not None, "Event must have a source"
    assert event.status is not None, "Event must have a status"

    if required_fields:
        for field in required_fields:
            value = getattr(event, field, None)
            assert value is not None, f"Event field '{field}' must not be None"
            if isinstance(value, str):
                assert value.strip(), f"Event field '{field}' must not be empty"


def assert_valid_user(user: UserProfile, required_fields: List[str] = None):
    """
    Assert that a user object is valid.

    Args:
        user: The user object to validate
        required_fields: List of fields that must be present and non-empty
    """
    assert isinstance(user, UserProfile), "Object must be a UserProfile instance"
    assert user.user_id is not None, "User must have a user_id"
    assert user.email is not None and user.email.strip(), "User must have a non-empty email"
    assert "@" in user.email, "User email must be valid"
    assert user.role is not None, "User must have a role"

    if required_fields:
        for field in required_fields:
            value = getattr(user, field, None)
            assert value is not None, f"User field '{field}' must not be None"


def assert_valid_feedback(feedback: Feedback, required_fields: List[str] = None):
    """
    Assert that a feedback object is valid.

    Args:
        feedback: The feedback object to validate
        required_fields: List of fields that must be present and non-empty
    """
    assert isinstance(feedback, Feedback), "Object must be a Feedback instance"
    assert feedback.user_id is not None, "Feedback must have a user_id"
    assert feedback.type is not None, "Feedback must have a type"
    assert feedback.title is not None and feedback.title.strip(), "Feedback must have a non-empty title"
    assert feedback.content is not None and feedback.content.strip(), "Feedback must have non-empty content"

    if required_fields:
        for field in required_fields:
            value = getattr(feedback, field, None)
            assert value is not None, f"Feedback field '{field}' must not be None"


def wait_for_condition(
    condition: Callable[[], bool], 
    timeout: float = 10.0, 
    interval: float = 0.1,
    error_message: str = "Condition not met within timeout"
):
    """
    Wait for a condition to become true within a timeout period.
    
    Args:
        condition: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        interval: Time between checks in seconds
        error_message: Error message if timeout is reached
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition():
            return True
        time.sleep(interval)
    
    raise TimeoutError(error_message)


async def async_wait_for_condition(
    condition: Callable[[], bool], 
    timeout: float = 10.0, 
    interval: float = 0.1,
    error_message: str = "Condition not met within timeout"
):
    """
    Async version of wait_for_condition.
    
    Args:
        condition: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        interval: Time between checks in seconds
        error_message: Error message if timeout is reached
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition():
            return True
        await asyncio.sleep(interval)
    
    raise TimeoutError(error_message)


def cleanup_test_data(mock_services, collections: List[str] = None):
    """
    Clean up test data from mock services.
    
    Args:
        mock_services: Mock service container
        collections: List of collections to clean up (None for all)
    """
    if hasattr(mock_services, 'firestore'):
        if collections:
            for collection in collections:
                if collection in mock_services.firestore.documents:
                    mock_services.firestore.documents[collection].clear()
        else:
            mock_services.firestore.reset()
    
    if hasattr(mock_services, 'bigquery'):
        if collections:
            for collection in collections:
                if collection in mock_services.bigquery.tables:
                    mock_services.bigquery.tables[collection].clear()
        else:
            mock_services.bigquery.reset()


def create_test_event(**kwargs) -> EventCore:
    """
    Create a test event with default values.
    
    Args:
        **kwargs: Override default values
        
    Returns:
        EventCore: Test event object
    """
    from .factories import EventFactory
    return EventFactory.create(**kwargs)


def create_test_user(**kwargs) -> UserProfile:
    """
    Create a test user with default values.
    
    Args:
        **kwargs: Override default values
        
    Returns:
        UserProfile: Test user object
    """
    from .factories import UserProfileFactory
    return UserProfileFactory.create(**kwargs)


def create_test_feedback(**kwargs) -> Feedback:
    """
    Create test feedback with default values.
    
    Args:
        **kwargs: Override default values
        
    Returns:
        Feedback: Test feedback object
    """
    from .factories import FeedbackFactory
    return FeedbackFactory.create(**kwargs)


def assert_datetime_recent(dt: datetime, max_age_seconds: int = 60):
    """
    Assert that a datetime is recent (within specified seconds).
    
    Args:
        dt: Datetime to check
        max_age_seconds: Maximum age in seconds
    """
    now = datetime.utcnow()
    age = (now - dt).total_seconds()
    assert age <= max_age_seconds, f"Datetime {dt} is {age} seconds old, expected <= {max_age_seconds}"


def assert_coordinates_valid(latitude: float, longitude: float):
    """
    Assert that coordinates are valid.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    """
    assert -90 <= latitude <= 90, f"Invalid latitude: {latitude}"
    assert -180 <= longitude <= 180, f"Invalid longitude: {longitude}"


def assert_json_structure(data: Dict[str, Any], expected_structure: Dict[str, type]):
    """
    Assert that a JSON object has the expected structure.
    
    Args:
        data: JSON data to validate
        expected_structure: Dictionary mapping field names to expected types
    """
    for field, expected_type in expected_structure.items():
        assert field in data, f"Missing field: {field}"
        
        if expected_type is not None:
            actual_value = data[field]
            if expected_type == "optional":
                continue  # Optional field, any type is fine
            elif isinstance(expected_type, list):
                # Multiple allowed types
                assert any(isinstance(actual_value, t) for t in expected_type), \
                    f"Field {field} has type {type(actual_value)}, expected one of {expected_type}"
            else:
                assert isinstance(actual_value, expected_type), \
                    f"Field {field} has type {type(actual_value)}, expected {expected_type}"


def mock_api_response(status_code: int = 200, data: Dict[str, Any] = None, headers: Dict[str, str] = None):
    """
    Create a mock API response object.
    
    Args:
        status_code: HTTP status code
        data: Response data
        headers: Response headers
        
    Returns:
        Mock response object
    """
    class MockResponse:
        def __init__(self, status_code, data, headers):
            self.status_code = status_code
            self._data = data or {}
            self.headers = headers or {}
        
        def json(self):
            return self._data
        
        def text(self):
            return json.dumps(self._data)
    
    return MockResponse(status_code, data, headers)


def generate_test_correlation_id() -> str:
    """Generate a test correlation ID."""
    import uuid
    return f"test-{uuid.uuid4()}"


def assert_correlation_id_format(correlation_id: str):
    """Assert that a correlation ID has the correct format."""
    import uuid
    
    assert isinstance(correlation_id, str), "Correlation ID must be a string"
    assert len(correlation_id) > 0, "Correlation ID must not be empty"
    
    # Try to parse as UUID (common format)
    try:
        uuid.UUID(correlation_id)
    except ValueError:
        # If not a UUID, check if it's a test correlation ID
        assert correlation_id.startswith("test-"), \
            f"Correlation ID '{correlation_id}' is not a valid UUID or test ID"


def measure_execution_time(func: Callable, *args, **kwargs) -> tuple:
    """
    Measure the execution time of a function.
    
    Args:
        func: Function to measure
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Tuple of (result, execution_time_seconds)
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    
    return result, execution_time


async def measure_async_execution_time(func: Callable, *args, **kwargs) -> tuple:
    """
    Measure the execution time of an async function.
    
    Args:
        func: Async function to measure
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Tuple of (result, execution_time_seconds)
    """
    start_time = time.time()
    result = await func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    
    return result, execution_time


def assert_performance_threshold(execution_time: float, max_time: float, operation_name: str = "Operation"):
    """
    Assert that an operation completed within a performance threshold.
    
    Args:
        execution_time: Actual execution time in seconds
        max_time: Maximum allowed time in seconds
        operation_name: Name of the operation for error messages
    """
    assert execution_time <= max_time, \
        f"{operation_name} took {execution_time:.3f}s, expected <= {max_time}s"


def create_test_scenario(scenario_name: str, **kwargs) -> Dict[str, Any]:
    """
    Create a predefined test scenario.
    
    Args:
        scenario_name: Name of the scenario to create
        **kwargs: Additional parameters for scenario creation
        
    Returns:
        Dictionary containing scenario data
    """
    from .factories import TestDataSets
    
    scenarios = {
        'complete_event': TestDataSets.create_complete_event_scenario,
        'multi_user': TestDataSets.create_multi_user_scenario,
        'severity_test': TestDataSets.create_severity_test_data,
        'time_series': TestDataSets.create_time_series_data
    }
    
    if scenario_name not in scenarios:
        raise ValueError(f"Unknown scenario: {scenario_name}. Available: {list(scenarios.keys())}")
    
    return scenarios[scenario_name](**kwargs)


def validate_test_environment():
    """Validate that the test environment is properly configured."""
    import os
    
    required_env_vars = ['GOOGLE_CLOUD_PROJECT']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        pytest.skip(f"Missing required environment variables: {missing_vars}")


def skip_if_external_services_unavailable():
    """Skip test if external services are not available."""
    # This would check if external services are available
    # For now, it's a placeholder
    pass
