"""
Base API Test Framework for CityPulse E2E Testing

This module provides the foundation for comprehensive API testing with:
- Authentication handling
- Request/response validation
- Error handling and retry logic
- Test data management
- Performance monitoring
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import httpx
import pytest
from pathlib import Path

class APITestBase:
    """Base class for all API tests with common functionality."""
    
    def __init__(self, environment: str = "test"):
        self.environment = environment
        self.config = self._load_config()
        self.client = None
        self.auth_token = None
        self.test_data = self._load_test_data()
        self.performance_metrics = []
        
    def _load_config(self) -> Dict[str, Any]:
        """Load environment configuration."""
        config_path = Path(__file__).parent.parent.parent / "config" / "environments.json"
        with open(config_path) as f:
            configs = json.load(f)
        return configs.get(self.environment, configs["test"])
    
    def _load_test_data(self) -> Dict[str, Any]:
        """Load test data fixtures."""
        data_path = Path(__file__).parent.parent.parent / "config" / "test-data.json"
        with open(data_path) as f:
            return json.load(f)
    
    async def setup_client(self):
        """Initialize HTTP client with proper configuration."""
        self.client = httpx.AsyncClient(
            base_url=self.config["backend"]["baseUrl"],
            timeout=httpx.Timeout(self.config["timeouts"]["api"] / 1000),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "CityPulse-E2E-Tests/1.0"
            }
        )
    
    async def teardown_client(self):
        """Clean up HTTP client."""
        if self.client:
            await self.client.aclose()
    
    async def authenticate_user(self, user_type: str = "citizen") -> str:
        """Authenticate a test user and return auth token."""
        user_data = self.config["auth"]["testUsers"][user_type]
        
        auth_payload = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = await self.make_request(
            "POST",
            "/auth/login",
            data=auth_payload,
            authenticated=False
        )
        
        if response.status_code == 200:
            self.auth_token = response.json()["token"]
            return self.auth_token
        else:
            raise Exception(f"Authentication failed: {response.text}")
    
    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        authenticated: bool = True,
        retry_count: int = None
    ) -> httpx.Response:
        """Make an HTTP request with proper error handling and metrics."""
        
        if retry_count is None:
            retry_count = self.config["retries"]["api"]
        
        # Prepare headers
        request_headers = headers or {}
        if authenticated and self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        # Prepare URL
        url = f"{self.config['backend']['apiPrefix']}{endpoint}"
        
        # Performance tracking
        start_time = time.time()
        
        for attempt in range(retry_count + 1):
            try:
                response = await self.client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers
                )
                
                # Record performance metrics
                end_time = time.time()
                self.performance_metrics.append({
                    "endpoint": endpoint,
                    "method": method,
                    "duration": end_time - start_time,
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat(),
                    "attempt": attempt + 1
                })
                
                return response
                
            except httpx.RequestError as e:
                if attempt == retry_count:
                    raise Exception(f"Request failed after {retry_count + 1} attempts: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("Unexpected error in make_request")
    
    def validate_response_structure(
        self,
        response: httpx.Response,
        expected_fields: List[str],
        response_type: str = "object"
    ) -> bool:
        """Validate response structure and required fields."""
        
        if response.status_code >= 400:
            return False
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            return False
        
        if response_type == "object":
            if not isinstance(data, dict):
                return False
            
            for field in expected_fields:
                if field not in data:
                    return False
                    
        elif response_type == "array":
            if not isinstance(data, list):
                return False
            
            if data and expected_fields:
                # Check first item for expected fields
                first_item = data[0]
                for field in expected_fields:
                    if field not in first_item:
                        return False
        
        return True
    
    def validate_error_response(
        self,
        response: httpx.Response,
        expected_status: int,
        expected_error_fields: List[str] = None
    ) -> bool:
        """Validate error response structure."""
        
        if response.status_code != expected_status:
            return False
        
        if expected_error_fields is None:
            expected_error_fields = ["error", "message"]
        
        try:
            data = response.json()
            for field in expected_error_fields:
                if field not in data:
                    return False
            return True
        except json.JSONDecodeError:
            return False
    
    async def create_test_event(
        self,
        event_data: Optional[Dict[str, Any]] = None,
        user_type: str = "citizen"
    ) -> Dict[str, Any]:
        """Create a test event for testing purposes."""
        
        if not self.auth_token:
            await self.authenticate_user(user_type)
        
        if event_data is None:
            event_data = self.test_data["events"]["validEvent"].copy()
        
        response = await self.make_request(
            "POST",
            "/events",
            data=event_data
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create test event: {response.text}")
    
    async def cleanup_test_event(self, event_id: str):
        """Clean up a test event."""
        try:
            await self.make_request("DELETE", f"/events/{event_id}")
        except Exception:
            pass  # Ignore cleanup errors
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate performance metrics report."""
        if not self.performance_metrics:
            return {"message": "No performance data collected"}
        
        # Calculate statistics
        durations = [m["duration"] for m in self.performance_metrics]
        
        report = {
            "total_requests": len(self.performance_metrics),
            "average_response_time": sum(durations) / len(durations),
            "min_response_time": min(durations),
            "max_response_time": max(durations),
            "success_rate": len([m for m in self.performance_metrics if m["status_code"] < 400]) / len(self.performance_metrics),
            "endpoints_tested": list(set(m["endpoint"] for m in self.performance_metrics)),
            "test_duration": (
                datetime.fromisoformat(self.performance_metrics[-1]["timestamp"]) -
                datetime.fromisoformat(self.performance_metrics[0]["timestamp"])
            ).total_seconds() if len(self.performance_metrics) > 1 else 0
        }
        
        return report
    
    async def wait_for_condition(
        self,
        condition_func,
        timeout: int = 30,
        interval: int = 1,
        error_message: str = "Condition not met within timeout"
    ) -> bool:
        """Wait for a condition to be met with timeout."""
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await condition_func():
                return True
            await asyncio.sleep(interval)
        
        raise TimeoutError(error_message)

class EventsAPITest(APITestBase):
    """Specialized test class for Events API."""
    
    async def test_create_event_success(self):
        """Test successful event creation."""
        await self.setup_client()
        await self.authenticate_user("citizen")
        
        event_data = self.test_data["events"]["validEvent"]
        response = await self.make_request("POST", "/events", data=event_data)
        
        assert response.status_code == 201
        assert self.validate_response_structure(
            response,
            ["id", "title", "description", "category", "status", "created_at"]
        )
        
        # Cleanup
        event_id = response.json()["id"]
        await self.cleanup_test_event(event_id)
        await self.teardown_client()
    
    async def test_create_event_validation_error(self):
        """Test event creation with invalid data."""
        await self.setup_client()
        await self.authenticate_user("citizen")
        
        invalid_event = self.test_data["events"]["invalidEvent"]
        response = await self.make_request("POST", "/events", data=invalid_event)
        
        assert response.status_code == 400
        assert self.validate_error_response(response, 400)
        
        await self.teardown_client()
    
    async def test_get_events_pagination(self):
        """Test events listing with pagination."""
        await self.setup_client()
        await self.authenticate_user("citizen")
        
        # Test pagination parameters
        response = await self.make_request(
            "GET",
            "/events",
            params={"limit": 10, "offset": 0}
        )
        
        assert response.status_code == 200
        assert self.validate_response_structure(
            response,
            ["items", "total", "limit", "offset"]
        )
        
        await self.teardown_client()

class UsersAPITest(APITestBase):
    """Specialized test class for Users API."""
    
    async def test_user_profile_operations(self):
        """Test user profile CRUD operations."""
        await self.setup_client()
        await self.authenticate_user("citizen")
        
        # Get current profile
        response = await self.make_request("GET", "/users/profile")
        assert response.status_code == 200
        
        # Update profile
        update_data = {
            "displayName": "Updated Test User",
            "profile": {
                "firstName": "Updated",
                "lastName": "User"
            }
        }
        
        response = await self.make_request("PUT", "/users/profile", data=update_data)
        assert response.status_code == 200
        
        await self.teardown_client()

# Pytest fixtures for easy test setup
@pytest.fixture
async def api_test():
    """Fixture for basic API test setup."""
    test = APITestBase()
    await test.setup_client()
    yield test
    await test.teardown_client()

@pytest.fixture
async def authenticated_api_test():
    """Fixture for authenticated API test setup."""
    test = APITestBase()
    await test.setup_client()
    await test.authenticate_user("citizen")
    yield test
    await test.teardown_client()

@pytest.fixture
async def events_api_test():
    """Fixture for Events API testing."""
    test = EventsAPITest()
    yield test

@pytest.fixture
async def users_api_test():
    """Fixture for Users API testing."""
    test = UsersAPITest()
    yield test

# Export main classes for use in other modules
__all__ = [
    "APITestBase",
    "EventsAPITest",
    "UsersAPITest",
    "api_test",
    "authenticated_api_test",
    "events_api_test",
    "users_api_test"
]
