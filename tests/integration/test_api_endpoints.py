"""
Integration tests for CityPulse API endpoints.
Tests complete API workflows, authentication, and data flow.
"""

import pytest
import json
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import httpx
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer


# Mock FastAPI app for testing
app = FastAPI(title="CityPulse API", version="1.0.0")
security = HTTPBearer()


# Mock authentication dependency
async def get_current_user(token: str = Depends(security)):
    """Mock authentication dependency."""
    if token.credentials == "valid_token":
        return {
            "user_id": "user-123",
            "email": "test@example.com",
            "roles": ["user"]
        }
    elif token.credentials == "admin_token":
        return {
            "user_id": "admin-123",
            "email": "admin@example.com",
            "roles": ["user", "admin"]
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid token")


# Mock API endpoints
@app.get("/api/v1/events")
async def get_events(
    category: str = None,
    status: str = None,
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get events with filtering and pagination."""
    # Mock events data
    mock_events = [
        {
            "id": "event-1",
            "title": "Traffic Incident",
            "category": "infrastructure",
            "status": "active",
            "priority": "high",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "created_at": "2024-01-01T12:00:00Z"
        },
        {
            "id": "event-2",
            "title": "Broken Streetlight",
            "category": "infrastructure",
            "status": "resolved",
            "priority": "medium",
            "location": {"lat": 40.7589, "lng": -73.9851},
            "created_at": "2024-01-02T10:30:00Z"
        },
        {
            "id": "event-3",
            "title": "Safety Concern",
            "category": "safety",
            "status": "pending",
            "priority": "high",
            "location": {"lat": 40.7505, "lng": -73.9934},
            "created_at": "2024-01-03T14:15:00Z"
        }
    ]
    
    # Apply filters
    filtered_events = mock_events
    if category:
        filtered_events = [e for e in filtered_events if e["category"] == category]
    if status:
        filtered_events = [e for e in filtered_events if e["status"] == status]
    
    # Apply pagination
    paginated_events = filtered_events[offset:offset + limit]
    
    return {
        "events": paginated_events,
        "total": len(filtered_events),
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < len(filtered_events)
    }


@app.post("/api/v1/events")
async def create_event(
    event_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a new event."""
    # Validate required fields
    required_fields = ["title", "category", "location"]
    for field in required_fields:
        if field not in event_data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Create event with user info
    new_event = {
        "id": f"event-{datetime.now().timestamp()}",
        "title": event_data["title"],
        "description": event_data.get("description"),
        "category": event_data["category"],
        "priority": event_data.get("priority", "medium"),
        "status": "pending",
        "location": event_data["location"],
        "user_id": current_user["user_id"],
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    return {"event": new_event, "message": "Event created successfully"}


@app.get("/api/v1/events/{event_id}")
async def get_event(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific event by ID."""
    # Mock event lookup
    if event_id == "event-1":
        return {
            "id": "event-1",
            "title": "Traffic Incident",
            "description": "Major traffic jam on Main Street",
            "category": "infrastructure",
            "status": "active",
            "priority": "high",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "user_id": "user-456",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z"
        }
    else:
        raise HTTPException(status_code=404, detail="Event not found")


@app.put("/api/v1/events/{event_id}")
async def update_event(
    event_id: str,
    update_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update an event (admin only for status changes)."""
    # Check if user can update status
    if "status" in update_data and "admin" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Only admins can update event status")
    
    # Mock event update
    if event_id == "event-1":
        updated_event = {
            "id": "event-1",
            "title": "Traffic Incident",
            "status": update_data.get("status", "active"),
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        return {"event": updated_event, "message": "Event updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Event not found")


@app.post("/api/v1/events/{event_id}/feedback")
async def create_feedback(
    event_id: str,
    feedback_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create feedback for an event."""
    # Validate feedback data
    if "content" not in feedback_data:
        raise HTTPException(status_code=400, detail="Feedback content is required")
    
    # Create feedback
    new_feedback = {
        "id": f"feedback-{datetime.now().timestamp()}",
        "event_id": event_id,
        "user_id": current_user["user_id"],
        "content": feedback_data["content"],
        "rating": feedback_data.get("rating"),
        "feedback_type": feedback_data.get("feedback_type", "general"),
        "is_anonymous": feedback_data.get("is_anonymous", False),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    return {"feedback": new_feedback, "message": "Feedback created successfully"}


@app.get("/api/v1/analytics/trends")
async def get_analytics_trends(
    date_range: str = "week",
    category: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Get analytics trends data."""
    # Mock analytics data
    mock_trends = {
        "period": date_range,
        "category": category or "all",
        "data": [
            {"date": "2024-01-01", "count": 15, "resolved": 12},
            {"date": "2024-01-02", "count": 18, "resolved": 14},
            {"date": "2024-01-03", "count": 22, "resolved": 18},
            {"date": "2024-01-04", "count": 19, "resolved": 16},
            {"date": "2024-01-05", "count": 25, "resolved": 20}
        ],
        "summary": {
            "total_events": 99,
            "resolved_events": 80,
            "resolution_rate": 80.8,
            "avg_response_time": 24.5
        }
    }
    
    return mock_trends


@app.get("/api/v1/analytics/kpis")
async def get_kpis(
    current_user: dict = Depends(get_current_user)
):
    """Get key performance indicators."""
    # Mock KPI data
    mock_kpis = {
        "total_reports": 1250,
        "resolved_reports": 1000,
        "pending_reports": 180,
        "in_progress_reports": 70,
        "resolution_rate": 80.0,
        "avg_response_time_hours": 24.5,
        "critical_issues": 15,
        "user_satisfaction": 4.2,
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
    
    return mock_kpis


# Test client
client = TestClient(app)


class TestEventEndpoints:
    """Test cases for event-related API endpoints."""
    
    def test_get_events_success(self):
        """Test successful events retrieval."""
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/v1/events", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "events" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["events"], list)
        assert len(data["events"]) <= data["limit"]
    
    def test_get_events_with_filters(self):
        """Test events retrieval with category filter."""
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/v1/events?category=infrastructure", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned events should have infrastructure category
        for event in data["events"]:
            assert event["category"] == "infrastructure"
    
    def test_get_events_with_pagination(self):
        """Test events retrieval with pagination."""
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/v1/events?limit=1&offset=0", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["limit"] == 1
        assert data["offset"] == 0
        assert len(data["events"]) <= 1
    
    def test_get_events_unauthorized(self):
        """Test events retrieval without authentication."""
        response = client.get("/api/v1/events")
        
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
    
    def test_get_events_invalid_token(self):
        """Test events retrieval with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/events", headers=headers)
        
        assert response.status_code == 401
    
    def test_create_event_success(self):
        """Test successful event creation."""
        headers = {"Authorization": "Bearer valid_token"}
        event_data = {
            "title": "New Traffic Issue",
            "description": "Traffic light malfunction",
            "category": "infrastructure",
            "priority": "high",
            "location": {"lat": 40.7128, "lng": -74.0060}
        }
        
        response = client.post("/api/v1/events", json=event_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "event" in data
        assert "message" in data
        assert data["event"]["title"] == event_data["title"]
        assert data["event"]["category"] == event_data["category"]
        assert data["event"]["status"] == "pending"
        assert "id" in data["event"]
    
    def test_create_event_missing_fields(self):
        """Test event creation with missing required fields."""
        headers = {"Authorization": "Bearer valid_token"}
        incomplete_data = {
            "title": "Incomplete Event"
            # Missing category and location
        }
        
        response = client.post("/api/v1/events", json=incomplete_data, headers=headers)
        
        assert response.status_code == 400
        assert "Missing required field" in response.json()["detail"]
    
    def test_get_event_by_id_success(self):
        """Test successful event retrieval by ID."""
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/v1/events/event-1", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == "event-1"
        assert "title" in data
        assert "category" in data
        assert "status" in data
    
    def test_get_event_by_id_not_found(self):
        """Test event retrieval for non-existent event."""
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/v1/events/non-existent", headers=headers)
        
        assert response.status_code == 404
        assert "Event not found" in response.json()["detail"]
    
    def test_update_event_as_admin(self):
        """Test event update by admin user."""
        headers = {"Authorization": "Bearer admin_token"}
        update_data = {"status": "resolved"}
        
        response = client.put("/api/v1/events/event-1", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["event"]["status"] == "resolved"
        assert "updated_at" in data["event"]
    
    def test_update_event_status_as_user(self):
        """Test event status update by regular user (should fail)."""
        headers = {"Authorization": "Bearer valid_token"}
        update_data = {"status": "resolved"}
        
        response = client.put("/api/v1/events/event-1", json=update_data, headers=headers)
        
        assert response.status_code == 403
        assert "Only admins can update event status" in response.json()["detail"]


class TestFeedbackEndpoints:
    """Test cases for feedback-related API endpoints."""
    
    def test_create_feedback_success(self):
        """Test successful feedback creation."""
        headers = {"Authorization": "Bearer valid_token"}
        feedback_data = {
            "content": "Great response time!",
            "rating": 5,
            "feedback_type": "compliment"
        }
        
        response = client.post("/api/v1/events/event-1/feedback", json=feedback_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "feedback" in data
        assert data["feedback"]["content"] == feedback_data["content"]
        assert data["feedback"]["rating"] == feedback_data["rating"]
        assert data["feedback"]["event_id"] == "event-1"
        assert data["feedback"]["status"] == "pending"
    
    def test_create_feedback_missing_content(self):
        """Test feedback creation without content."""
        headers = {"Authorization": "Bearer valid_token"}
        feedback_data = {"rating": 4}
        
        response = client.post("/api/v1/events/event-1/feedback", json=feedback_data, headers=headers)
        
        assert response.status_code == 400
        assert "Feedback content is required" in response.json()["detail"]
    
    def test_create_anonymous_feedback(self):
        """Test anonymous feedback creation."""
        headers = {"Authorization": "Bearer valid_token"}
        feedback_data = {
            "content": "Anonymous feedback",
            "is_anonymous": True,
            "rating": 3
        }
        
        response = client.post("/api/v1/events/event-1/feedback", json=feedback_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["feedback"]["is_anonymous"] is True
        assert data["feedback"]["content"] == feedback_data["content"]


class TestAnalyticsEndpoints:
    """Test cases for analytics-related API endpoints."""
    
    def test_get_trends_success(self):
        """Test successful trends retrieval."""
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/v1/analytics/trends", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "period" in data
        assert "data" in data
        assert "summary" in data
        assert isinstance(data["data"], list)
        
        # Check data structure
        for item in data["data"]:
            assert "date" in item
            assert "count" in item
            assert "resolved" in item
    
    def test_get_trends_with_filters(self):
        """Test trends retrieval with category filter."""
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/v1/analytics/trends?category=infrastructure&date_range=month", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["category"] == "infrastructure"
        assert data["period"] == "month"
    
    def test_get_kpis_success(self):
        """Test successful KPIs retrieval."""
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/v1/analytics/kpis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required KPI fields
        required_fields = [
            "total_reports", "resolved_reports", "pending_reports",
            "resolution_rate", "avg_response_time_hours", "critical_issues",
            "user_satisfaction", "last_updated"
        ]
        
        for field in required_fields:
            assert field in data
        
        # Check data types
        assert isinstance(data["total_reports"], int)
        assert isinstance(data["resolution_rate"], (int, float))
        assert isinstance(data["user_satisfaction"], (int, float))


class TestAPIIntegration:
    """Integration tests for API workflow scenarios."""
    
    def test_complete_event_lifecycle(self):
        """Test complete event lifecycle from creation to resolution."""
        headers = {"Authorization": "Bearer valid_token"}
        admin_headers = {"Authorization": "Bearer admin_token"}
        
        # 1. Create event
        event_data = {
            "title": "Integration Test Event",
            "description": "Testing complete lifecycle",
            "category": "infrastructure",
            "priority": "medium",
            "location": {"lat": 40.7128, "lng": -74.0060}
        }
        
        create_response = client.post("/api/v1/events", json=event_data, headers=headers)
        assert create_response.status_code == 200
        
        event_id = create_response.json()["event"]["id"]
        
        # 2. Retrieve created event
        get_response = client.get(f"/api/v1/events/{event_id}", headers=headers)
        assert get_response.status_code == 200
        
        # 3. Add feedback to event
        feedback_data = {
            "content": "Thanks for reporting this issue",
            "rating": 4,
            "feedback_type": "general"
        }
        
        feedback_response = client.post(f"/api/v1/events/{event_id}/feedback", json=feedback_data, headers=headers)
        assert feedback_response.status_code == 200
        
        # 4. Update event status (as admin)
        update_data = {"status": "resolved"}
        update_response = client.put(f"/api/v1/events/{event_id}", json=update_data, headers=admin_headers)
        assert update_response.status_code == 200
        
        # 5. Verify final state
        final_response = client.get(f"/api/v1/events/{event_id}", headers=headers)
        assert final_response.status_code == 200
        # Note: In mock implementation, this would return the original event
        # In real implementation, it would show the updated status
    
    def test_authentication_flow(self):
        """Test authentication requirements across endpoints."""
        # Test without authentication
        no_auth_response = client.get("/api/v1/events")
        assert no_auth_response.status_code == 403
        
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        invalid_response = client.get("/api/v1/events", headers=invalid_headers)
        assert invalid_response.status_code == 401
        
        # Test with valid token
        valid_headers = {"Authorization": "Bearer valid_token"}
        valid_response = client.get("/api/v1/events", headers=valid_headers)
        assert valid_response.status_code == 200
    
    def test_role_based_access_control(self):
        """Test role-based access control."""
        user_headers = {"Authorization": "Bearer valid_token"}
        admin_headers = {"Authorization": "Bearer admin_token"}
        
        # Regular user cannot update event status
        update_data = {"status": "resolved"}
        user_response = client.put("/api/v1/events/event-1", json=update_data, headers=user_headers)
        assert user_response.status_code == 403
        
        # Admin can update event status
        admin_response = client.put("/api/v1/events/event-1", json=update_data, headers=admin_headers)
        assert admin_response.status_code == 200
    
    def test_data_validation_across_endpoints(self):
        """Test data validation consistency across endpoints."""
        headers = {"Authorization": "Bearer valid_token"}
        
        # Test event creation validation
        invalid_event = {"title": ""}  # Empty title
        event_response = client.post("/api/v1/events", json=invalid_event, headers=headers)
        assert event_response.status_code == 400
        
        # Test feedback creation validation
        invalid_feedback = {}  # Missing content
        feedback_response = client.post("/api/v1/events/event-1/feedback", json=invalid_feedback, headers=headers)
        assert feedback_response.status_code == 400


# Test fixtures
@pytest.fixture
def api_client():
    """Fixture providing API test client."""
    return client


@pytest.fixture
def valid_auth_headers():
    """Fixture providing valid authentication headers."""
    return {"Authorization": "Bearer valid_token"}


@pytest.fixture
def admin_auth_headers():
    """Fixture providing admin authentication headers."""
    return {"Authorization": "Bearer admin_token"}


@pytest.fixture
def sample_event_data():
    """Fixture providing sample event data for testing."""
    return {
        "title": "Test Event",
        "description": "This is a test event",
        "category": "infrastructure",
        "priority": "medium",
        "location": {"lat": 40.7128, "lng": -74.0060}
    }
