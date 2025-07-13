"""
Real FastAPI Client for CityPulse E2E Testing

This module provides a real API client that connects to the actual running
FastAPI backend server, enabling true integration testing.
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealFastAPIClient:
    """Real API client for testing the actual FastAPI backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = None
        self.auth_token = None
        self.session_data = {}
        self.request_history = []
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self):
        """Establish connection to the FastAPI backend."""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(30.0),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "CityPulse-E2E-Real-Tests/2.0"
            }
        )
        
        # Verify backend is running
        try:
            response = await self.client.get("/health")
            if response.status_code == 200:
                logger.info(f"✅ Connected to FastAPI backend at {self.base_url}")
                return True
            else:
                logger.error(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to connect to backend: {e}")
            return False
    
    async def disconnect(self):
        """Close connection to the FastAPI backend."""
        if self.client:
            await self.client.aclose()
            logger.info("🔌 Disconnected from FastAPI backend")
    
    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_required: bool = True
    ) -> httpx.Response:
        """Make a real HTTP request to the FastAPI backend."""
        
        # Prepare headers
        request_headers = headers or {}
        if auth_required and self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        # Prepare URL - backend already has /v1 prefix in routes
        url = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        
        # Record request start time
        start_time = time.time()
        
        try:
            # Make the actual HTTP request
            response = await self.client.request(
                method=method.upper(),
                url=url,
                json=data,
                params=params,
                headers=request_headers
            )
            
            # Record request completion
            end_time = time.time()
            duration = end_time - start_time
            
            # Log request details
            self.request_history.append({
                "method": method.upper(),
                "url": url,
                "status_code": response.status_code,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "request_data": data,
                "response_size": len(response.content) if response.content else 0
            })
            
            logger.info(
                f"{method.upper()} {url} -> {response.status_code} "
                f"({duration:.3f}s, {len(response.content) if response.content else 0} bytes)"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Request failed: {method.upper()} {url} - {e}")
            raise
    
    async def authenticate_real_user(self, email: str, password: str) -> bool:
        """Authenticate with real Firebase Auth through the backend."""
        try:
            auth_data = {
                "email": email,
                "password": password
            }
            
            response = await self.make_request(
                "POST",
                "/v1/auth/login",
                data=auth_data,
                auth_required=False
            )
            
            if response.status_code == 200:
                auth_result = response.json()
                self.auth_token = auth_result.get("access_token") or auth_result.get("token")
                self.session_data = auth_result
                logger.info(f"✅ Authenticated user: {email}")
                return True
            else:
                logger.error(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    async def test_events_api(self) -> Dict[str, Any]:
        """Test the real Events API endpoints."""
        results = {
            "test_name": "Real Events API Test",
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
        
        # Test 1: Get all events
        try:
            response = await self.make_request("GET", "/v1/events")
            test_result = {
                "name": "GET /events",
                "status": "passed" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response_time": self.request_history[-1]["duration"],
                "details": f"Retrieved events list"
            }
            
            if response.status_code == 200:
                events_data = response.json()
                test_result["details"] = f"Retrieved {len(events_data.get('events', []))} events"
                results["summary"]["passed"] += 1
            else:
                test_result["details"] = f"Failed: {response.text}"
                results["summary"]["failed"] += 1
                
            results["tests"].append(test_result)
            results["summary"]["total"] += 1
            
        except Exception as e:
            results["tests"].append({
                "name": "GET /events",
                "status": "error",
                "details": f"Exception: {e}"
            })
            results["summary"]["failed"] += 1
            results["summary"]["total"] += 1
        
        # Test 2: Create new event (if authenticated)
        if self.auth_token:
            try:
                new_event = {
                    "title": "E2E Test Event",
                    "description": "Test event created by E2E testing framework",
                    "category": "infrastructure",
                    "subcategory": "road_maintenance",
                    "priority": "medium",
                    "location": {
                        "latitude": 40.7128,
                        "longitude": -74.0060,
                        "address": "123 Test Street, New York, NY 10001"
                    },
                    "tags": ["test", "e2e", "automated"]
                }
                
                response = await self.make_request("POST", "/v1/events", data=new_event)
                test_result = {
                    "name": "POST /events",
                    "status": "passed" if response.status_code in [200, 201] else "failed",
                    "status_code": response.status_code,
                    "response_time": self.request_history[-1]["duration"],
                    "details": "Created test event"
                }
                
                if response.status_code in [200, 201]:
                    created_event = response.json()
                    test_result["details"] = f"Created event with ID: {created_event.get('id', 'unknown')}"
                    results["summary"]["passed"] += 1
                    
                    # Store event ID for cleanup
                    self.session_data["created_event_id"] = created_event.get("id")
                else:
                    test_result["details"] = f"Failed: {response.text}"
                    results["summary"]["failed"] += 1
                    
                results["tests"].append(test_result)
                results["summary"]["total"] += 1
                
            except Exception as e:
                results["tests"].append({
                    "name": "POST /events",
                    "status": "error",
                    "details": f"Exception: {e}"
                })
                results["summary"]["failed"] += 1
                results["summary"]["total"] += 1
        
        return results
    
    async def test_users_api(self) -> Dict[str, Any]:
        """Test the real Users API endpoints."""
        results = {
            "test_name": "Real Users API Test",
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
        
        # Test 1: Get user profile (requires authentication)
        if self.auth_token:
            try:
                response = await self.make_request("GET", "/v1/users/profile")
                test_result = {
                    "name": "GET /users/profile",
                    "status": "passed" if response.status_code == 200 else "failed",
                    "status_code": response.status_code,
                    "response_time": self.request_history[-1]["duration"],
                    "details": "Retrieved user profile"
                }
                
                if response.status_code == 200:
                    profile_data = response.json()
                    test_result["details"] = f"Retrieved profile for user: {profile_data.get('email', 'unknown')}"
                    results["summary"]["passed"] += 1
                else:
                    test_result["details"] = f"Failed: {response.text}"
                    results["summary"]["failed"] += 1
                    
                results["tests"].append(test_result)
                results["summary"]["total"] += 1
                
            except Exception as e:
                results["tests"].append({
                    "name": "GET /users/profile",
                    "status": "error",
                    "details": f"Exception: {e}"
                })
                results["summary"]["failed"] += 1
                results["summary"]["total"] += 1
        else:
            results["tests"].append({
                "name": "GET /users/profile",
                "status": "skipped",
                "details": "No authentication token available"
            })
            results["summary"]["total"] += 1
        
        return results
    
    async def test_analytics_api(self) -> Dict[str, Any]:
        """Test the real Analytics API endpoints."""
        results = {
            "test_name": "Real Analytics API Test",
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
        
        # Test 1: Get KPIs
        try:
            response = await self.make_request("GET", "/v1/analytics/kpis")
            test_result = {
                "name": "GET /analytics/kpis",
                "status": "passed" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response_time": self.request_history[-1]["duration"],
                "details": "Retrieved KPIs"
            }
            
            if response.status_code == 200:
                kpis_data = response.json()
                test_result["details"] = f"Retrieved {len(kpis_data)} KPI metrics"
                results["summary"]["passed"] += 1
            else:
                test_result["details"] = f"Failed: {response.text}"
                results["summary"]["failed"] += 1
                
            results["tests"].append(test_result)
            results["summary"]["total"] += 1
            
        except Exception as e:
            results["tests"].append({
                "name": "GET /analytics/kpis",
                "status": "error",
                "details": f"Exception: {e}"
            })
            results["summary"]["failed"] += 1
            results["summary"]["total"] += 1
        
        return results
    
    async def cleanup_test_data(self):
        """Clean up any test data created during testing."""
        if "created_event_id" in self.session_data and self.auth_token:
            try:
                event_id = self.session_data["created_event_id"]
                response = await self.make_request("DELETE", f"/v1/events/{event_id}")
                if response.status_code in [200, 204, 404]:  # 404 is OK if already deleted
                    logger.info(f"✅ Cleaned up test event: {event_id}")
                else:
                    logger.warning(f"⚠️ Failed to cleanup test event: {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Cleanup error: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from the test session."""
        if not self.request_history:
            return {"message": "No requests made"}
        
        durations = [req["duration"] for req in self.request_history]
        status_codes = [req["status_code"] for req in self.request_history]
        
        return {
            "total_requests": len(self.request_history),
            "average_response_time": sum(durations) / len(durations),
            "min_response_time": min(durations),
            "max_response_time": max(durations),
            "success_rate": len([sc for sc in status_codes if sc < 400]) / len(status_codes),
            "status_code_distribution": {
                str(sc): status_codes.count(sc) for sc in set(status_codes)
            },
            "total_test_duration": (
                datetime.fromisoformat(self.request_history[-1]["timestamp"]) -
                datetime.fromisoformat(self.request_history[0]["timestamp"])
            ).total_seconds() if len(self.request_history) > 1 else 0
        }


# Export the main class
__all__ = ["RealFastAPIClient"]
