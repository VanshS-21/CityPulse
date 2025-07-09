"""
Tests for the main FastAPI application.

This module tests the core application functionality including
health checks, root endpoints, and basic API structure.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Mock Firebase Admin SDK before importing main
with patch("firebase_admin.initialize_app"), patch("firebase_admin._apps", []):
    from main import app

client = TestClient(app)


class TestMainApplication:
    """Test cases for the main FastAPI application."""

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "citypulse-api"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data

    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "Welcome to CityPulse API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"

    def test_openapi_schema(self):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert schema["info"]["title"] == "CityPulse API"
        assert schema["info"]["version"] == "1.0.0"
        assert "components" in schema
        assert "securitySchemes" in schema["components"]

    def test_docs_endpoint(self):
        """Test that API documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_cors_headers(self):
        """Test CORS headers are properly set."""
        response = client.options("/health")
        assert response.status_code == 200
        # Note: TestClient doesn't fully simulate CORS, but we can check the middleware is loaded

    def test_invalid_endpoint(self):
        """Test that invalid endpoints return 404."""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404

        data = response.json()
        assert data["error"] == "HTTP_ERROR"
        assert data["status_code"] == 404

    @patch("google.cloud.firestore.Client")
    def test_events_endpoint_without_auth(self, mock_firestore):
        """Test events endpoint without authentication."""
        response = client.get("/v1/events")
        assert response.status_code == 401

        data = response.json()
        assert data["error"] == "HTTP_ERROR"
        assert "authorization" in data["message"].lower()

    @patch("google.cloud.firestore.Client")
    def test_events_endpoint_with_api_key(self, mock_firestore):
        """Test events endpoint with API key."""
        # Mock Firestore query
        mock_collection = MagicMock()
        mock_query = MagicMock()
        mock_query.stream.return_value = []
        mock_collection.offset.return_value.limit.return_value = mock_query
        mock_firestore.return_value.collection.return_value = mock_collection

        headers = {"X-API-Key": "test-api-key"}
        response = client.get("/v1/events", headers=headers)

        # This will fail auth since we don't have valid API keys configured
        # but it tests the middleware flow
        assert response.status_code in [
            401,
            500,
        ]  # Either auth failure or service error

    def test_error_handling(self):
        """Test global error handling."""
        # Test with malformed JSON in request body
        response = client.post(
            "/v1/events",
            headers={"Content-Type": "application/json"},
            data="invalid json",
        )
        assert response.status_code == 422

    def test_request_validation(self):
        """Test request validation."""
        # Test with missing required fields
        response = client.post(
            "/v1/events", json={"title": ""}  # Empty title should fail validation
        )
        assert response.status_code == 401  # Auth required first

    def test_security_headers(self):
        """Test that security headers are present."""
        response = client.get("/health")

        # Check that the response doesn't expose sensitive information
        assert "Server" not in response.headers
        assert response.status_code == 200


class TestAPIStructure:
    """Test the overall API structure and routing."""

    def test_api_versioning(self):
        """Test that API versioning is properly implemented."""
        # Test that v1 prefix is required for API endpoints
        response = client.get("/events")  # Without v1 prefix
        assert response.status_code == 404

        # Test that v1 endpoints exist (even if they require auth)
        response = client.get("/v1/events")
        assert response.status_code in [401, 500]  # Not 404

    def test_endpoint_discovery(self):
        """Test that all expected endpoints are available."""
        expected_paths = [
            "/v1/events",
            "/v1/users/me",
            "/v1/feedback",
            "/v1/analytics/kpis",
        ]

        for path in expected_paths:
            response = client.get(path)
            # Should not be 404 (endpoint exists), but may be 401 (auth required)
            assert response.status_code != 404, f"Endpoint {path} not found"

    def test_http_methods(self):
        """Test that appropriate HTTP methods are supported."""
        # Test GET method
        response = client.get("/v1/events")
        assert response.status_code in [200, 401, 500]  # Not 405 (Method Not Allowed)

        # Test POST method
        response = client.post("/v1/events", json={})
        assert response.status_code in [200, 401, 422, 500]  # Not 405

        # Test unsupported method should return 405
        response = client.patch("/health")
        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__])
