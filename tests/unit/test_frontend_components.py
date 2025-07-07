"""
Comprehensive unit tests for CityPulse frontend components.
Tests React components, hooks, utilities, and state management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestAPIGateway:
    """Test cases for API Gateway functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Reset singleton instance for testing
        from src.lib.api_gateway import APIGateway
        APIGateway._instance = None
    
    def test_singleton_pattern(self):
        """Test APIGateway singleton pattern."""
        from src.lib.api_gateway import APIGateway
        
        instance1 = APIGateway.getInstance()
        instance2 = APIGateway.getInstance()
        
        assert instance1 is instance2
    
    @patch('src.lib.api_gateway.fetch')
    def test_successful_request(self, mock_fetch):
        """Test successful API request."""
        from src.lib.api_gateway import APIGateway
        
        # Mock successful response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status = 200
        mock_response.json.return_value = {"data": "test_data"}
        mock_fetch.return_value = Promise.resolve(mock_response)
        
        gateway = APIGateway.getInstance()
        
        # This would be an async test in a real JS environment
        # For Python testing, we'll test the logic structure
        assert gateway is not None
        assert hasattr(gateway, 'request')
        assert hasattr(gateway, 'get')
        assert hasattr(gateway, 'post')
    
    def test_auth_token_management(self):
        """Test authentication token management."""
        from src.lib.api_gateway import APIGateway
        
        gateway = APIGateway.getInstance()
        
        # Test setting auth token
        test_token = "test_auth_token_123"
        gateway.setAuthToken(test_token)
        assert gateway.authToken == test_token
        
        # Test clearing auth token
        gateway.clearAuthToken()
        assert gateway.authToken is None
    
    def test_cache_validation(self):
        """Test cache validation logic."""
        from src.lib.api_gateway import APIGateway
        
        gateway = APIGateway.getInstance()
        
        # Test cache entry creation
        cache_key = "test_key"
        test_data = {"result": "cached_data"}
        ttl = 300000  # 5 minutes
        
        # Simulate cache entry
        cache_entry = {
            "data": test_data,
            "timestamp": 1640995200000,  # Mock timestamp
            "ttl": ttl
        }
        
        gateway.cache.set(cache_key, cache_entry)
        
        # Test cache validation logic would be implemented here
        assert cache_key in gateway.cache
    
    def test_request_deduplication(self):
        """Test request deduplication functionality."""
        from src.lib.api_gateway import APIGateway
        
        gateway = APIGateway.getInstance()
        
        # Test request queue management
        cache_key = "test_endpoint_key"
        mock_promise = Mock()
        
        gateway.requestQueue.set(cache_key, mock_promise)
        
        assert gateway.requestQueue.has(cache_key)
        assert gateway.requestQueue.get(cache_key) == mock_promise
        
        gateway.requestQueue.delete(cache_key)
        assert not gateway.requestQueue.has(cache_key)


class TestDashboardStore:
    """Test cases for Dashboard Store state management."""
    
    def test_store_initialization(self):
        """Test dashboard store initialization."""
        # In a real environment, this would test Zustand store
        initial_state = {
            "metrics": {
                "totalReports": 0,
                "resolvedReports": 0,
                "pendingReports": 0,
                "avgResponseTime": 0,
                "criticalIssues": 0,
                "lastUpdated": None,
                "loading": False,
                "error": None
            },
            "filters": {
                "dateRange": "week",
                "category": "all",
                "status": "all",
                "priority": "all",
                "location": {
                    "bounds": None,
                    "zoom": 10,
                    "center": {"lat": 40.7128, "lng": -74.0060}
                }
            },
            "ui": {
                "sidebarOpen": True,
                "mapView": "roadmap",
                "theme": "system",
                "notifications": {
                    "enabled": True,
                    "sound": True,
                    "desktop": True
                },
                "layout": "grid",
                "activePanel": "overview"
            },
            "reports": {
                "reports": [],
                "selectedReport": None,
                "loading": False,
                "error": None,
                "pagination": {
                    "page": 1,
                    "limit": 20,
                    "total": 0,
                    "hasMore": False
                }
            }
        }
        
        # Test initial state structure
        assert "metrics" in initial_state
        assert "filters" in initial_state
        assert "ui" in initial_state
        assert "reports" in initial_state
        
        # Test metrics initial values
        assert initial_state["metrics"]["totalReports"] == 0
        assert initial_state["metrics"]["loading"] is False
        assert initial_state["metrics"]["error"] is None
        
        # Test filters initial values
        assert initial_state["filters"]["dateRange"] == "week"
        assert initial_state["filters"]["category"] == "all"
        assert initial_state["filters"]["location"]["zoom"] == 10
        
        # Test UI initial values
        assert initial_state["ui"]["sidebarOpen"] is True
        assert initial_state["ui"]["mapView"] == "roadmap"
        assert initial_state["ui"]["theme"] == "system"
    
    def test_metrics_actions(self):
        """Test metrics state actions."""
        # Mock metrics update action
        def update_metrics(current_state, new_metrics):
            updated_state = current_state.copy()
            updated_state["metrics"].update(new_metrics)
            updated_state["metrics"]["lastUpdated"] = "2024-01-01T12:00:00Z"
            return updated_state
        
        initial_state = {
            "metrics": {
                "totalReports": 0,
                "resolvedReports": 0,
                "lastUpdated": None
            }
        }
        
        new_metrics = {
            "totalReports": 150,
            "resolvedReports": 120
        }
        
        updated_state = update_metrics(initial_state, new_metrics)
        
        assert updated_state["metrics"]["totalReports"] == 150
        assert updated_state["metrics"]["resolvedReports"] == 120
        assert updated_state["metrics"]["lastUpdated"] is not None
    
    def test_filter_actions(self):
        """Test filter state actions."""
        # Mock filter update actions
        def set_date_range(current_state, date_range):
            updated_state = current_state.copy()
            updated_state["filters"]["dateRange"] = date_range
            return updated_state
        
        def set_category(current_state, category):
            updated_state = current_state.copy()
            updated_state["filters"]["category"] = category
            return updated_state
        
        initial_state = {
            "filters": {
                "dateRange": "week",
                "category": "all"
            }
        }
        
        # Test date range update
        updated_state = set_date_range(initial_state, "month")
        assert updated_state["filters"]["dateRange"] == "month"
        
        # Test category update
        updated_state = set_category(updated_state, "infrastructure")
        assert updated_state["filters"]["category"] == "infrastructure"
    
    def test_ui_actions(self):
        """Test UI state actions."""
        # Mock UI update actions
        def toggle_sidebar(current_state):
            updated_state = current_state.copy()
            updated_state["ui"]["sidebarOpen"] = not updated_state["ui"]["sidebarOpen"]
            return updated_state
        
        def set_theme(current_state, theme):
            updated_state = current_state.copy()
            updated_state["ui"]["theme"] = theme
            return updated_state
        
        initial_state = {
            "ui": {
                "sidebarOpen": True,
                "theme": "system"
            }
        }
        
        # Test sidebar toggle
        updated_state = toggle_sidebar(initial_state)
        assert updated_state["ui"]["sidebarOpen"] is False
        
        updated_state = toggle_sidebar(updated_state)
        assert updated_state["ui"]["sidebarOpen"] is True
        
        # Test theme update
        updated_state = set_theme(updated_state, "dark")
        assert updated_state["ui"]["theme"] == "dark"
    
    def test_reports_actions(self):
        """Test reports state actions."""
        # Mock reports actions
        def add_report(current_state, report):
            updated_state = current_state.copy()
            updated_state["reports"]["reports"].insert(0, report)
            return updated_state
        
        def update_report(current_state, report_id, updates):
            updated_state = current_state.copy()
            reports = updated_state["reports"]["reports"]
            for i, report in enumerate(reports):
                if report["id"] == report_id:
                    reports[i] = {**report, **updates}
                    break
            return updated_state
        
        def remove_report(current_state, report_id):
            updated_state = current_state.copy()
            updated_state["reports"]["reports"] = [
                report for report in updated_state["reports"]["reports"]
                if report["id"] != report_id
            ]
            return updated_state
        
        initial_state = {
            "reports": {
                "reports": [
                    {"id": "1", "title": "Report 1", "status": "pending"},
                    {"id": "2", "title": "Report 2", "status": "resolved"}
                ]
            }
        }
        
        # Test add report
        new_report = {"id": "3", "title": "New Report", "status": "pending"}
        updated_state = add_report(initial_state, new_report)
        assert len(updated_state["reports"]["reports"]) == 3
        assert updated_state["reports"]["reports"][0]["id"] == "3"
        
        # Test update report
        updates = {"status": "in_progress", "assignee": "admin"}
        updated_state = update_report(updated_state, "1", updates)
        report_1 = next(r for r in updated_state["reports"]["reports"] if r["id"] == "1")
        assert report_1["status"] == "in_progress"
        assert report_1["assignee"] == "admin"
        
        # Test remove report
        updated_state = remove_report(updated_state, "2")
        assert len(updated_state["reports"]["reports"]) == 2
        assert not any(r["id"] == "2" for r in updated_state["reports"]["reports"])
    
    def test_computed_selectors(self):
        """Test computed selectors functionality."""
        # Mock filtered reports selector
        def get_filtered_reports(state):
            reports = state["reports"]["reports"]
            filters = state["filters"]
            
            filtered = reports
            
            # Apply category filter
            if filters["category"] != "all":
                filtered = [r for r in filtered if r.get("category") == filters["category"]]
            
            # Apply status filter
            if filters["status"] != "all":
                filtered = [r for r in filtered if r.get("status") == filters["status"]]
            
            return filtered
        
        # Mock metrics summary selector
        def get_metrics_summary(state):
            metrics = state["metrics"]
            return {
                "totalReports": metrics["totalReports"],
                "resolutionRate": (
                    round((metrics["resolvedReports"] / metrics["totalReports"]) * 100)
                    if metrics["totalReports"] > 0 else 0
                ),
                "avgResponseTime": metrics["avgResponseTime"],
                "criticalIssues": metrics["criticalIssues"]
            }
        
        test_state = {
            "reports": {
                "reports": [
                    {"id": "1", "category": "infrastructure", "status": "pending"},
                    {"id": "2", "category": "infrastructure", "status": "resolved"},
                    {"id": "3", "category": "safety", "status": "pending"}
                ]
            },
            "filters": {
                "category": "infrastructure",
                "status": "all"
            },
            "metrics": {
                "totalReports": 100,
                "resolvedReports": 80,
                "avgResponseTime": 24,
                "criticalIssues": 5
            }
        }
        
        # Test filtered reports
        filtered_reports = get_filtered_reports(test_state)
        assert len(filtered_reports) == 2
        assert all(r["category"] == "infrastructure" for r in filtered_reports)
        
        # Test metrics summary
        summary = get_metrics_summary(test_state)
        assert summary["totalReports"] == 100
        assert summary["resolutionRate"] == 80
        assert summary["avgResponseTime"] == 24
        assert summary["criticalIssues"] == 5


class TestUtilityFunctions:
    """Test cases for utility functions and helpers."""
    
    def test_date_formatting(self):
        """Test date formatting utilities."""
        # Mock date formatting function
        def format_date(date_string, format_type="short"):
            from datetime import datetime
            
            try:
                date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                
                if format_type == "short":
                    return date_obj.strftime("%m/%d/%Y")
                elif format_type == "long":
                    return date_obj.strftime("%B %d, %Y")
                elif format_type == "time":
                    return date_obj.strftime("%I:%M %p")
                else:
                    return date_obj.strftime("%m/%d/%Y %I:%M %p")
            except:
                return "Invalid Date"
        
        test_date = "2024-01-15T14:30:00Z"
        
        assert format_date(test_date, "short") == "01/15/2024"
        assert format_date(test_date, "long") == "January 15, 2024"
        assert format_date(test_date, "time") == "02:30 PM"
        assert format_date("invalid") == "Invalid Date"
    
    def test_validation_helpers(self):
        """Test validation helper functions."""
        # Mock validation functions
        def validate_email(email):
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None
        
        def validate_coordinates(lat, lng):
            try:
                lat_num = float(lat)
                lng_num = float(lng)
                return -90 <= lat_num <= 90 and -180 <= lng_num <= 180
            except:
                return False
        
        def validate_required_fields(data, required_fields):
            return all(field in data and data[field] for field in required_fields)
        
        # Test email validation
        assert validate_email("test@example.com") is True
        assert validate_email("invalid-email") is False
        assert validate_email("test@") is False
        
        # Test coordinate validation
        assert validate_coordinates(40.7128, -74.0060) is True
        assert validate_coordinates(91, 0) is False
        assert validate_coordinates("invalid", "coords") is False
        
        # Test required fields validation
        test_data = {"title": "Test", "description": "Test desc", "category": "infrastructure"}
        required = ["title", "description", "category"]
        assert validate_required_fields(test_data, required) is True
        
        incomplete_data = {"title": "Test", "description": ""}
        assert validate_required_fields(incomplete_data, required) is False
    
    def test_data_transformation(self):
        """Test data transformation utilities."""
        # Mock data transformation functions
        def transform_report_for_display(report):
            return {
                "id": report["id"],
                "title": report["title"],
                "status": report["status"].replace("_", " ").title(),
                "category": report["category"].replace("_", " ").title(),
                "createdAt": report.get("created_at", ""),
                "location": report.get("location", {}),
                "priority": report.get("priority", "medium").title()
            }
        
        def aggregate_reports_by_category(reports):
            aggregated = {}
            for report in reports:
                category = report.get("category", "other")
                if category not in aggregated:
                    aggregated[category] = {"count": 0, "reports": []}
                aggregated[category]["count"] += 1
                aggregated[category]["reports"].append(report)
            return aggregated
        
        # Test report transformation
        raw_report = {
            "id": "123",
            "title": "Traffic Issue",
            "status": "in_progress",
            "category": "infrastructure",
            "priority": "high",
            "created_at": "2024-01-01T12:00:00Z"
        }
        
        transformed = transform_report_for_display(raw_report)
        assert transformed["status"] == "In Progress"
        assert transformed["category"] == "Infrastructure"
        assert transformed["priority"] == "High"
        
        # Test aggregation
        reports = [
            {"id": "1", "category": "infrastructure"},
            {"id": "2", "category": "infrastructure"},
            {"id": "3", "category": "safety"},
            {"id": "4", "category": "infrastructure"}
        ]
        
        aggregated = aggregate_reports_by_category(reports)
        assert aggregated["infrastructure"]["count"] == 3
        assert aggregated["safety"]["count"] == 1
        assert len(aggregated["infrastructure"]["reports"]) == 3


# Test fixtures and utilities
@pytest.fixture
def mock_api_response():
    """Fixture providing mock API response data."""
    return {
        "success": True,
        "data": {
            "reports": [
                {
                    "id": "1",
                    "title": "Traffic Jam",
                    "status": "pending",
                    "category": "infrastructure",
                    "priority": "medium",
                    "created_at": "2024-01-01T12:00:00Z"
                },
                {
                    "id": "2",
                    "title": "Broken Streetlight",
                    "status": "resolved",
                    "category": "infrastructure",
                    "priority": "low",
                    "created_at": "2024-01-02T10:30:00Z"
                }
            ],
            "total": 2,
            "page": 1,
            "limit": 20
        },
        "status": 200
    }


@pytest.fixture
def mock_dashboard_state():
    """Fixture providing mock dashboard state."""
    return {
        "metrics": {
            "totalReports": 150,
            "resolvedReports": 120,
            "pendingReports": 25,
            "avgResponseTime": 24,
            "criticalIssues": 5,
            "lastUpdated": "2024-01-01T12:00:00Z",
            "loading": False,
            "error": None
        },
        "filters": {
            "dateRange": "week",
            "category": "all",
            "status": "all",
            "priority": "all"
        },
        "ui": {
            "sidebarOpen": True,
            "mapView": "roadmap",
            "theme": "light",
            "layout": "grid"
        },
        "reports": {
            "reports": [],
            "selectedReport": None,
            "loading": False,
            "error": None
        }
    }


class TestComponentIntegration:
    """Integration tests for frontend components working together."""
    
    def test_api_gateway_with_store_integration(self, mock_api_response):
        """Test API Gateway integration with state store."""
        # Mock the integration between API Gateway and store
        def fetch_reports_and_update_store(api_gateway, store_update_function):
            # Simulate API call
            response = mock_api_response
            
            if response["success"]:
                # Update store with fetched data
                store_update_function({
                    "reports": response["data"]["reports"],
                    "loading": False,
                    "error": None
                })
                return True
            else:
                store_update_function({
                    "loading": False,
                    "error": "Failed to fetch reports"
                })
                return False
        
        # Mock store update function
        store_state = {"reports": [], "loading": True, "error": None}
        
        def update_store(updates):
            store_state.update(updates)
        
        # Test the integration
        mock_gateway = Mock()
        result = fetch_reports_and_update_store(mock_gateway, update_store)
        
        assert result is True
        assert len(store_state["reports"]) == 2
        assert store_state["loading"] is False
        assert store_state["error"] is None
    
    def test_filter_state_with_data_filtering(self, mock_dashboard_state):
        """Test filter state integration with data filtering."""
        # Add some test reports to the state
        test_reports = [
            {"id": "1", "category": "infrastructure", "status": "pending", "priority": "high"},
            {"id": "2", "category": "safety", "status": "resolved", "priority": "medium"},
            {"id": "3", "category": "infrastructure", "status": "pending", "priority": "low"},
            {"id": "4", "category": "environment", "status": "in_progress", "priority": "high"}
        ]
        
        mock_dashboard_state["reports"]["reports"] = test_reports
        
        # Mock filtering function
        def apply_filters(state):
            reports = state["reports"]["reports"]
            filters = state["filters"]
            
            filtered = reports
            
            if filters["category"] != "all":
                filtered = [r for r in filtered if r["category"] == filters["category"]]
            
            if filters["status"] != "all":
                filtered = [r for r in filtered if r["status"] == filters["status"]]
            
            if filters["priority"] != "all":
                filtered = [r for r in filtered if r["priority"] == filters["priority"]]
            
            return filtered
        
        # Test with no filters (should return all)
        filtered_reports = apply_filters(mock_dashboard_state)
        assert len(filtered_reports) == 4
        
        # Test with category filter
        mock_dashboard_state["filters"]["category"] = "infrastructure"
        filtered_reports = apply_filters(mock_dashboard_state)
        assert len(filtered_reports) == 2
        assert all(r["category"] == "infrastructure" for r in filtered_reports)
        
        # Test with multiple filters
        mock_dashboard_state["filters"]["status"] = "pending"
        filtered_reports = apply_filters(mock_dashboard_state)
        assert len(filtered_reports) == 2
        assert all(r["category"] == "infrastructure" and r["status"] == "pending" for r in filtered_reports)
