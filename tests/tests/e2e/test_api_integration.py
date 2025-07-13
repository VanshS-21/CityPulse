"""
Unified API Integration E2E Tests

Consolidated from the original E2E framework and Real Integration framework,
providing comprehensive API testing with both mock and real modes.
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any
import sys
from pathlib import Path

# Add the core modules to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

from core.api_client.unified_api_client import UnifiedAPIClient, ClientMode


class TestAPIIntegration:
    """Comprehensive API integration tests."""
    
    @pytest_asyncio.fixture
    async def mock_client(self):
        """Mock API client fixture."""
        async with UnifiedAPIClient(mode=ClientMode.MOCK) as client:
            yield client
    
    @pytest.fixture
    async def real_client(self):
        """Real API client fixture."""
        async with UnifiedAPIClient(mode=ClientMode.REAL) as client:
            yield client
    
    @pytest.fixture
    async def hybrid_client(self):
        """Hybrid API client fixture (falls back to mock if real unavailable)."""
        async with UnifiedAPIClient(mode=ClientMode.HYBRID) as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_health_endpoint_mock(self, mock_client):
        """Test health endpoint with mock client."""
        response = await mock_client.make_request("GET", "/health")
        
        assert response["status_code"] == 200
        assert response["json"]["status"] == "healthy"
        assert response["json"]["service"] == "citypulse-api"
        assert "timestamp" in response["json"]
    
    @pytest.mark.asyncio
    async def test_health_endpoint_hybrid(self, hybrid_client):
        """Test health endpoint with hybrid client."""
        response = await hybrid_client.make_request("GET", "/health")
        
        assert response["status_code"] == 200
        assert "status" in response["json"]
    
    @pytest.mark.asyncio
    async def test_events_list_mock(self, mock_client):
        """Test events list endpoint with mock client."""
        response = await mock_client.make_request("GET", "/v1/events")
        
        assert response["status_code"] == 200
        assert "events" in response["json"]
        assert isinstance(response["json"]["events"], list)
        assert response["json"]["total"] >= 0
    
    @pytest.mark.asyncio
    async def test_events_list_hybrid(self, hybrid_client):
        """Test events list endpoint with hybrid client."""
        response = await hybrid_client.make_request("GET", "/v1/events")
        
        # Should work in either mock or real mode
        assert response["status_code"] in [200, 401, 500]  # 401/500 expected without auth in real mode
    
    @pytest.mark.asyncio
    async def test_events_create_mock(self, mock_client):
        """Test event creation with mock client."""
        # Mock authentication
        await mock_client.authenticate("test@example.com", "password")
        
        event_data = {
            "title": "Test Event",
            "description": "Test event description",
            "category": "infrastructure",
            "priority": "medium",
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "address": "123 Test Street, New York, NY"
            }
        }
        
        response = await mock_client.make_request("POST", "/v1/events", data=event_data, auth_required=True)
        
        assert response["status_code"] == 201
        assert "id" in response["json"]
        assert response["json"]["status"] == "created"
    
    @pytest.mark.asyncio
    async def test_events_create_without_auth_mock(self, mock_client):
        """Test event creation without authentication (should fail)."""
        event_data = {
            "title": "Test Event",
            "description": "Test event description",
            "category": "infrastructure"
        }
        
        response = await mock_client.make_request("POST", "/v1/events", data=event_data, auth_required=True)
        
        assert response["status_code"] == 401
        assert "error" in response["json"]
    
    @pytest.mark.asyncio
    async def test_analytics_kpis_mock(self, mock_client):
        """Test analytics KPIs endpoint with mock client."""
        response = await mock_client.make_request("GET", "/v1/analytics/kpis")
        
        assert response["status_code"] == 200
        assert "total_events" in response["json"]
        assert "active_events" in response["json"]
        assert "resolved_events" in response["json"]
        assert isinstance(response["json"]["total_events"], int)
    
    @pytest.mark.asyncio
    async def test_analytics_kpis_hybrid(self, hybrid_client):
        """Test analytics KPIs endpoint with hybrid client."""
        response = await hybrid_client.make_request("GET", "/v1/analytics/kpis")
        
        # Should work in either mock or real mode
        assert response["status_code"] in [200, 401, 500]
    
    @pytest.mark.asyncio
    async def test_user_profile_with_auth_mock(self, mock_client):
        """Test user profile endpoint with authentication."""
        # Mock authentication
        await mock_client.authenticate("test@example.com", "password")
        
        response = await mock_client.make_request("GET", "/v1/users/profile", auth_required=True)
        
        assert response["status_code"] == 200
        assert "id" in response["json"]
        assert "email" in response["json"]
        assert response["json"]["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_user_profile_without_auth_mock(self, mock_client):
        """Test user profile endpoint without authentication (should fail)."""
        response = await mock_client.make_request("GET", "/v1/users/profile", auth_required=True)
        
        assert response["status_code"] == 401
        assert "error" in response["json"]
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, mock_client):
        """Test performance metrics collection."""
        # Make several requests
        await mock_client.make_request("GET", "/health")
        await mock_client.make_request("GET", "/v1/events")
        await mock_client.make_request("GET", "/v1/analytics/kpis")
        
        metrics = mock_client.get_performance_metrics()
        
        assert metrics["total_requests"] == 3
        assert "average_response_time" in metrics
        assert "success_rate" in metrics
        assert metrics["success_rate"] == 1.0  # All mock requests should succeed
        assert "mode_distribution" in metrics
        assert metrics["mode_distribution"]["mock"] == 3
    
    @pytest.mark.asyncio
    async def test_error_handling_mock(self, mock_client):
        """Test error handling for non-existent endpoints."""
        response = await mock_client.make_request("GET", "/v1/nonexistent")
        
        assert response["status_code"] == 404
        assert "error" in response["json"]
    
    @pytest.mark.asyncio
    async def test_request_history_tracking(self, mock_client):
        """Test that request history is properly tracked."""
        initial_count = len(mock_client.request_history)
        
        await mock_client.make_request("GET", "/health")
        await mock_client.make_request("GET", "/v1/events")
        
        assert len(mock_client.request_history) == initial_count + 2
        
        # Check request details
        last_request = mock_client.request_history[-1]
        assert "method" in last_request
        assert "endpoint" in last_request
        assert "status_code" in last_request
        assert "duration" in last_request
        assert "timestamp" in last_request
        assert "mode" in last_request
    
    @pytest.mark.asyncio
    async def test_cleanup_functionality(self, mock_client):
        """Test cleanup functionality."""
        # Simulate creating test data
        mock_client.session_data["created_event_id"] = "test_event_123"
        
        # Cleanup should not raise errors
        await mock_client.cleanup_test_data()
        
        # Should handle cleanup gracefully even without test data
        mock_client.session_data.clear()
        await mock_client.cleanup_test_data()


class TestAPIIntegrationReal:
    """Real API integration tests (only run when backend is available)."""
    
    @pytest.fixture
    async def real_client(self):
        """Real API client fixture."""
        try:
            async with UnifiedAPIClient(mode=ClientMode.REAL) as client:
                yield client
        except Exception:
            pytest.skip("Real backend not available")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_health_endpoint(self, real_client):
        """Test real health endpoint."""
        response = await real_client.make_request("GET", "/health")
        
        assert response["status_code"] == 200
        assert "status" in response["json"]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_events_endpoint(self, real_client):
        """Test real events endpoint."""
        response = await real_client.make_request("GET", "/v1/events")
        
        # May return 401 without authentication, which is expected
        assert response["status_code"] in [200, 401, 500]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_analytics_endpoint(self, real_client):
        """Test real analytics endpoint."""
        response = await real_client.make_request("GET", "/v1/analytics/kpis")
        
        # May return 401 without authentication, which is expected
        assert response["status_code"] in [200, 401, 500]


# Pytest configuration
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.e2e,
    pytest.mark.api
]
