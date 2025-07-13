"""
Unified API Client for CityPulse Testing

This module provides a unified API client that can operate in both mock and real modes,
consolidating the functionality from the original E2E framework and Real Integration framework.
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClientMode(Enum):
    """API client operation modes."""
    MOCK = "mock"
    REAL = "real"
    HYBRID = "hybrid"


class UnifiedAPIClient:
    """Unified API client supporting both mock and real API testing."""
    
    def __init__(self, 
                 mode: ClientMode = ClientMode.MOCK,
                 base_url: str = "http://localhost:8000",
                 timeout: float = 30.0):
        self.mode = mode
        self.base_url = base_url
        self.timeout = timeout
        self.client = None
        self.auth_token = None
        self.session_data = {}
        self.request_history = []
        self.mock_responses = self._load_mock_responses()
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    def _load_mock_responses(self) -> Dict[str, Any]:
        """Load mock responses for testing."""
        return {
            "GET /health": {
                "status_code": 200,
                "response": {
                    "status": "healthy",
                    "service": "citypulse-api",
                    "version": "1.0.0",
                    "timestamp": datetime.now().isoformat()
                }
            },
            "GET /v1/events": {
                "status_code": 200,
                "response": {
                    "events": [
                        {
                            "id": "evt_mock_001",
                            "title": "Mock Traffic Event",
                            "category": "traffic",
                            "status": "open",
                            "created_at": datetime.now().isoformat()
                        }
                    ],
                    "total": 1,
                    "page": 1,
                    "limit": 10
                }
            },
            "POST /v1/events": {
                "status_code": 201,
                "response": {
                    "id": "evt_mock_new",
                    "title": "New Mock Event",
                    "status": "created",
                    "created_at": datetime.now().isoformat()
                }
            },
            "GET /v1/analytics/kpis": {
                "status_code": 200,
                "response": {
                    "total_events": 150,
                    "active_events": 25,
                    "resolved_events": 125,
                    "average_resolution_time": 2.5
                }
            },
            "GET /v1/users/profile": {
                "status_code": 200,
                "response": {
                    "id": "user_mock_001",
                    "email": "test@example.com",
                    "role": "citizen",
                    "created_at": datetime.now().isoformat()
                }
            }
        }
    
    async def connect(self) -> bool:
        """Establish connection based on mode."""
        if self.mode == ClientMode.MOCK:
            logger.info(f"✅ Mock API client initialized")
            return True
        
        elif self.mode in [ClientMode.REAL, ClientMode.HYBRID]:
            try:
                self.client = httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=httpx.Timeout(self.timeout),
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "CityPulse-Unified-Tests/1.0"
                    }
                )
                
                # Test real connection
                response = await self.client.get("/health")
                if response.status_code == 200:
                    logger.info(f"✅ Connected to real API at {self.base_url}")
                    return True
                else:
                    if self.mode == ClientMode.HYBRID:
                        logger.warning(f"⚠️ Real API unavailable, falling back to mock mode")
                        self.mode = ClientMode.MOCK
                        return True
                    else:
                        logger.error(f"❌ Real API connection failed: {response.status_code}")
                        return False
                        
            except Exception as e:
                if self.mode == ClientMode.HYBRID:
                    logger.warning(f"⚠️ Real API connection failed, falling back to mock mode: {e}")
                    self.mode = ClientMode.MOCK
                    return True
                else:
                    logger.error(f"❌ Failed to connect to real API: {e}")
                    return False
        
        return False
    
    async def disconnect(self):
        """Close connection."""
        if self.client:
            await self.client.aclose()
            logger.info("🔌 Disconnected from API")
    
    async def make_request(self,
                          method: str,
                          endpoint: str,
                          data: Optional[Dict[str, Any]] = None,
                          params: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, str]] = None,
                          auth_required: bool = False) -> Dict[str, Any]:
        """Make API request (mock or real based on mode)."""
        
        start_time = time.time()
        
        if self.mode == ClientMode.MOCK:
            return await self._make_mock_request(method, endpoint, data, params, headers, auth_required)
        else:
            return await self._make_real_request(method, endpoint, data, params, headers, auth_required)
    
    async def _make_mock_request(self,
                                method: str,
                                endpoint: str,
                                data: Optional[Dict[str, Any]] = None,
                                params: Optional[Dict[str, Any]] = None,
                                headers: Optional[Dict[str, str]] = None,
                                auth_required: bool = False) -> Dict[str, Any]:
        """Make mock API request."""
        
        start_time = time.time()
        
        # Simulate network delay
        await asyncio.sleep(0.01)
        
        # Build request key
        request_key = f"{method.upper()} {endpoint}"
        
        # Get mock response
        mock_response = self.mock_responses.get(request_key, {
            "status_code": 404,
            "response": {"error": "Mock endpoint not found"}
        })
        
        # Simulate authentication check
        if auth_required and not self.auth_token:
            mock_response = {
                "status_code": 401,
                "response": {"error": "Authentication required"}
            }
        
        # Record request
        duration = time.time() - start_time
        self.request_history.append({
            "method": method.upper(),
            "endpoint": endpoint,
            "status_code": mock_response["status_code"],
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "mode": "mock"
        })
        
        logger.info(f"MOCK {method.upper()} {endpoint} -> {mock_response['status_code']} ({duration:.3f}s)")
        
        return {
            "status_code": mock_response["status_code"],
            "json": mock_response["response"],
            "headers": {"content-type": "application/json"},
            "elapsed": duration
        }
    
    async def _make_real_request(self,
                                method: str,
                                endpoint: str,
                                data: Optional[Dict[str, Any]] = None,
                                params: Optional[Dict[str, Any]] = None,
                                headers: Optional[Dict[str, str]] = None,
                                auth_required: bool = False) -> Dict[str, Any]:
        """Make real API request."""
        
        start_time = time.time()
        
        # Prepare headers
        request_headers = headers or {}
        if auth_required and self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            # Make real HTTP request
            response = await self.client.request(
                method=method.upper(),
                url=endpoint,
                json=data,
                params=params,
                headers=request_headers
            )
            
            duration = time.time() - start_time
            
            # Record request
            self.request_history.append({
                "method": method.upper(),
                "endpoint": endpoint,
                "status_code": response.status_code,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "mode": "real"
            })
            
            logger.info(f"REAL {method.upper()} {endpoint} -> {response.status_code} ({duration:.3f}s)")
            
            # Parse response
            try:
                response_json = response.json()
            except:
                response_json = {"raw_response": response.text}
            
            return {
                "status_code": response.status_code,
                "json": response_json,
                "headers": dict(response.headers),
                "elapsed": duration
            }
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ Real request failed: {method.upper()} {endpoint} - {e}")
            
            return {
                "status_code": 500,
                "json": {"error": f"Request failed: {str(e)}"},
                "headers": {},
                "elapsed": duration
            }
    
    async def authenticate(self, email: str, password: str) -> bool:
        """Authenticate user (mock or real)."""
        if self.mode == ClientMode.MOCK:
            # Mock authentication
            self.auth_token = "mock_token_12345"
            self.session_data = {
                "user_id": "mock_user_001",
                "email": email,
                "role": "citizen"
            }
            logger.info(f"✅ Mock authentication successful for {email}")
            return True
        else:
            # Real authentication
            try:
                response = await self.make_request(
                    "POST",
                    "/v1/auth/login",
                    data={"email": email, "password": password},
                    auth_required=False
                )
                
                if response["status_code"] == 200:
                    auth_data = response["json"]
                    self.auth_token = auth_data.get("access_token") or auth_data.get("token")
                    self.session_data = auth_data
                    logger.info(f"✅ Real authentication successful for {email}")
                    return True
                else:
                    logger.error(f"❌ Authentication failed: {response['status_code']}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Authentication error: {e}")
                return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from request history."""
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
            "mode_distribution": {
                mode: len([req for req in self.request_history if req["mode"] == mode])
                for mode in set(req["mode"] for req in self.request_history)
            }
        }
    
    async def cleanup_test_data(self):
        """Clean up any test data created during testing."""
        if "created_event_id" in self.session_data:
            try:
                event_id = self.session_data["created_event_id"]
                response = await self.make_request("DELETE", f"/v1/events/{event_id}", auth_required=True)
                if response["status_code"] in [200, 204, 404]:
                    logger.info(f"✅ Cleaned up test event: {event_id}")
                else:
                    logger.warning(f"⚠️ Failed to cleanup test event: {response['status_code']}")
            except Exception as e:
                logger.warning(f"⚠️ Cleanup error: {e}")


# Export the main class
__all__ = ["UnifiedAPIClient", "ClientMode"]
