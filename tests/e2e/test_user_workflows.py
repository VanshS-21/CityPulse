"""
End-to-End tests for CityPulse user workflows.
Tests complete user journeys from frontend to backend with real-world scenarios.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import json
import time

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from fastapi.testclient import TestClient


class TestCitizenReportingWorkflow:
    """E2E tests for citizen reporting workflow."""
    
    @pytest.fixture
    async def browser_setup(self):
        """Setup browser for E2E testing."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            yield page
            
            await context.close()
            await browser.close()
    
    async def test_complete_report_submission_workflow(self, browser_setup):
        """Test complete citizen report submission from start to finish."""
        page = browser_setup
        
        # 1. Navigate to CityPulse homepage
        await page.goto("http://localhost:3000")
        
        # Wait for page to load
        await page.wait_for_selector('[data-testid="homepage-title"]')
        
        # Verify homepage loaded
        title = await page.text_content('[data-testid="homepage-title"]')
        assert "CityPulse" in title
        
        # 2. Click "Report Issue" button
        await page.click('[data-testid="report-issue-button"]')
        
        # Wait for report form to appear
        await page.wait_for_selector('[data-testid="report-form"]')
        
        # 3. Fill out report form
        await page.fill('[data-testid="report-title"]', "Broken Streetlight on Main Street")
        await page.fill('[data-testid="report-description"]', "The streetlight at the intersection of Main Street and Oak Avenue has been out for 3 days, creating a safety hazard for pedestrians.")
        
        # Select category
        await page.select_option('[data-testid="report-category"]', "infrastructure")
        
        # Select priority
        await page.select_option('[data-testid="report-priority"]', "medium")
        
        # 4. Set location (mock geolocation)
        await page.evaluate("""
            navigator.geolocation.getCurrentPosition = function(success) {
                success({
                    coords: {
                        latitude: 40.7128,
                        longitude: -74.0060
                    }
                });
            };
        """)
        
        # Click "Use Current Location" button
        await page.click('[data-testid="use-current-location"]')
        
        # Wait for location to be set
        await page.wait_for_function("""
            document.querySelector('[data-testid="location-display"]').textContent.includes('40.7128')
        """)
        
        # 5. Upload image (optional)
        # Mock file input
        await page.set_input_files('[data-testid="image-upload"]', 'tests/fixtures/sample-image.jpg')
        
        # Wait for image preview
        await page.wait_for_selector('[data-testid="image-preview"]')
        
        # 6. Submit report
        await page.click('[data-testid="submit-report"]')
        
        # Wait for success message
        await page.wait_for_selector('[data-testid="success-message"]')
        
        # Verify success message
        success_text = await page.text_content('[data-testid="success-message"]')
        assert "Report submitted successfully" in success_text
        
        # 7. Verify report appears in user's reports list
        await page.click('[data-testid="my-reports-link"]')
        
        # Wait for reports list
        await page.wait_for_selector('[data-testid="reports-list"]')
        
        # Check if new report appears
        report_titles = await page.eval_on_selector_all(
            '[data-testid="report-item-title"]',
            'elements => elements.map(el => el.textContent)'
        )
        
        assert any("Broken Streetlight on Main Street" in title for title in report_titles)
    
    async def test_anonymous_report_submission(self, browser_setup):
        """Test anonymous report submission workflow."""
        page = browser_setup
        
        # Navigate to report form
        await page.goto("http://localhost:3000/report")
        
        # Wait for form to load
        await page.wait_for_selector('[data-testid="report-form"]')
        
        # Check "Submit Anonymously" checkbox
        await page.check('[data-testid="anonymous-checkbox"]')
        
        # Fill required fields
        await page.fill('[data-testid="report-title"]', "Anonymous Safety Concern")
        await page.fill('[data-testid="report-description"]', "There is a safety issue that needs attention.")
        await page.select_option('[data-testid="report-category"]', "safety")
        
        # Set location manually
        await page.fill('[data-testid="location-lat"]', "40.7589")
        await page.fill('[data-testid="location-lng"]', "-73.9851")
        
        # Submit report
        await page.click('[data-testid="submit-report"]')
        
        # Wait for success message
        await page.wait_for_selector('[data-testid="success-message"]')
        
        # Verify anonymous submission
        success_text = await page.text_content('[data-testid="success-message"]')
        assert "anonymous" in success_text.lower()
    
    async def test_report_form_validation(self, browser_setup):
        """Test report form validation and error handling."""
        page = browser_setup
        
        # Navigate to report form
        await page.goto("http://localhost:3000/report")
        await page.wait_for_selector('[data-testid="report-form"]')
        
        # Try to submit empty form
        await page.click('[data-testid="submit-report"]')
        
        # Check for validation errors
        await page.wait_for_selector('[data-testid="validation-error"]')
        
        error_text = await page.text_content('[data-testid="validation-error"]')
        assert "required" in error_text.lower()
        
        # Fill title but leave description empty
        await page.fill('[data-testid="report-title"]', "Test Title")
        await page.click('[data-testid="submit-report"]')
        
        # Should still show validation error for description
        await page.wait_for_selector('[data-testid="validation-error"]')
        
        # Fill all required fields
        await page.fill('[data-testid="report-description"]', "Test description with sufficient detail.")
        await page.select_option('[data-testid="report-category"]', "other")
        
        # Set location
        await page.fill('[data-testid="location-lat"]', "40.7128")
        await page.fill('[data-testid="location-lng"]', "-74.0060")
        
        # Submit should now work
        await page.click('[data-testid="submit-report"]')
        await page.wait_for_selector('[data-testid="success-message"]')


class TestAdminWorkflow:
    """E2E tests for admin workflow."""
    
    @pytest.fixture
    async def admin_browser_setup(self):
        """Setup browser with admin authentication."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Mock admin authentication
            await page.add_init_script("""
                localStorage.setItem('auth_token', 'admin_token_123');
                localStorage.setItem('user_role', 'admin');
            """)
            
            yield page
            
            await context.close()
            await browser.close()
    
    async def test_admin_dashboard_access(self, admin_browser_setup):
        """Test admin dashboard access and functionality."""
        page = admin_browser_setup
        
        # Navigate to admin dashboard
        await page.goto("http://localhost:3000/admin")
        
        # Wait for dashboard to load
        await page.wait_for_selector('[data-testid="admin-dashboard"]')
        
        # Verify admin-specific elements are visible
        assert await page.is_visible('[data-testid="admin-stats"]')
        assert await page.is_visible('[data-testid="pending-reports"]')
        assert await page.is_visible('[data-testid="user-management"]')
        
        # Check KPI cards
        kpi_cards = await page.query_selector_all('[data-testid="kpi-card"]')
        assert len(kpi_cards) >= 4  # Total reports, resolved, pending, etc.
    
    async def test_report_status_update_workflow(self, admin_browser_setup):
        """Test admin updating report status."""
        page = admin_browser_setup
        
        # Navigate to reports management
        await page.goto("http://localhost:3000/admin/reports")
        
        # Wait for reports list
        await page.wait_for_selector('[data-testid="reports-table"]')
        
        # Find first pending report
        await page.click('[data-testid="report-row"]:first-child [data-testid="view-report"]')
        
        # Wait for report details modal
        await page.wait_for_selector('[data-testid="report-details-modal"]')
        
        # Update status to "In Progress"
        await page.select_option('[data-testid="status-select"]', "in_progress")
        
        # Add admin notes
        await page.fill('[data-testid="admin-notes"]', "Assigned to maintenance team. Expected resolution within 48 hours.")
        
        # Save changes
        await page.click('[data-testid="save-changes"]')
        
        # Wait for success notification
        await page.wait_for_selector('[data-testid="update-success"]')
        
        # Verify status updated in table
        await page.wait_for_function("""
            document.querySelector('[data-testid="report-row"]:first-child [data-testid="status-badge"]')
                .textContent.includes('In Progress')
        """)
    
    async def test_user_management_workflow(self, admin_browser_setup):
        """Test admin user management functionality."""
        page = admin_browser_setup
        
        # Navigate to user management
        await page.goto("http://localhost:3000/admin/users")
        
        # Wait for users table
        await page.wait_for_selector('[data-testid="users-table"]')
        
        # Search for specific user
        await page.fill('[data-testid="user-search"]', "test@example.com")
        await page.press('[data-testid="user-search"]', "Enter")
        
        # Wait for search results
        await page.wait_for_timeout(1000)
        
        # Click on user to view details
        await page.click('[data-testid="user-row"]:first-child [data-testid="view-user"]')
        
        # Wait for user details modal
        await page.wait_for_selector('[data-testid="user-details-modal"]')
        
        # Verify user information is displayed
        assert await page.is_visible('[data-testid="user-email"]')
        assert await page.is_visible('[data-testid="user-reports-count"]')
        assert await page.is_visible('[data-testid="user-join-date"]')


class TestPublicDashboardWorkflow:
    """E2E tests for public dashboard and analytics."""
    
    @pytest.fixture
    async def public_browser_setup(self):
        """Setup browser for public access."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            yield page
            
            await context.close()
            await browser.close()
    
    async def test_public_dashboard_access(self, public_browser_setup):
        """Test public dashboard access and data visualization."""
        page = public_browser_setup
        
        # Navigate to public dashboard
        await page.goto("http://localhost:3000/dashboard")
        
        # Wait for dashboard to load
        await page.wait_for_selector('[data-testid="public-dashboard"]')
        
        # Verify key components are visible
        assert await page.is_visible('[data-testid="metrics-overview"]')
        assert await page.is_visible('[data-testid="category-chart"]')
        assert await page.is_visible('[data-testid="trends-chart"]')
        assert await page.is_visible('[data-testid="map-view"]')
        
        # Test filter functionality
        await page.select_option('[data-testid="category-filter"]', "infrastructure")
        
        # Wait for charts to update
        await page.wait_for_timeout(2000)
        
        # Verify filter applied (charts should show only infrastructure data)
        filter_indicator = await page.text_content('[data-testid="active-filters"]')
        assert "infrastructure" in filter_indicator.lower()
    
    async def test_map_interaction(self, public_browser_setup):
        """Test interactive map functionality."""
        page = public_browser_setup
        
        # Navigate to dashboard
        await page.goto("http://localhost:3000/dashboard")
        
        # Wait for map to load
        await page.wait_for_selector('[data-testid="map-container"]')
        
        # Click on map marker
        await page.click('[data-testid="map-marker"]:first-child')
        
        # Wait for popup to appear
        await page.wait_for_selector('[data-testid="map-popup"]')
        
        # Verify popup contains event information
        popup_content = await page.text_content('[data-testid="map-popup"]')
        assert len(popup_content) > 0
        
        # Test map controls
        await page.click('[data-testid="zoom-in"]')
        await page.wait_for_timeout(500)
        
        await page.click('[data-testid="zoom-out"]')
        await page.wait_for_timeout(500)
        
        # Change map view
        await page.select_option('[data-testid="map-type-select"]', "satellite")
        await page.wait_for_timeout(1000)
    
    async def test_analytics_charts_interaction(self, public_browser_setup):
        """Test analytics charts interaction and data filtering."""
        page = public_browser_setup
        
        # Navigate to analytics page
        await page.goto("http://localhost:3000/analytics")
        
        # Wait for charts to load
        await page.wait_for_selector('[data-testid="analytics-charts"]')
        
        # Test date range filter
        await page.select_option('[data-testid="date-range-select"]', "month")
        
        # Wait for charts to update
        await page.wait_for_timeout(2000)
        
        # Verify charts updated
        chart_title = await page.text_content('[data-testid="chart-title"]')
        assert "month" in chart_title.lower() or "30 days" in chart_title.lower()
        
        # Test chart hover interactions
        await page.hover('[data-testid="chart-bar"]:first-child')
        
        # Wait for tooltip
        await page.wait_for_selector('[data-testid="chart-tooltip"]')
        
        # Verify tooltip shows data
        tooltip_text = await page.text_content('[data-testid="chart-tooltip"]')
        assert len(tooltip_text) > 0


class TestMobileResponsiveness:
    """E2E tests for mobile responsiveness."""
    
    @pytest.fixture
    async def mobile_browser_setup(self):
        """Setup mobile browser viewport."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 375, 'height': 667},  # iPhone SE size
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
            )
            page = await context.new_page()
            
            yield page
            
            await context.close()
            await browser.close()
    
    async def test_mobile_navigation(self, mobile_browser_setup):
        """Test mobile navigation and responsive design."""
        page = mobile_browser_setup
        
        # Navigate to homepage
        await page.goto("http://localhost:3000")
        
        # Wait for page to load
        await page.wait_for_selector('[data-testid="mobile-header"]')
        
        # Test mobile menu
        await page.click('[data-testid="mobile-menu-button"]')
        
        # Wait for menu to open
        await page.wait_for_selector('[data-testid="mobile-menu"]')
        
        # Verify menu items are visible
        assert await page.is_visible('[data-testid="menu-dashboard"]')
        assert await page.is_visible('[data-testid="menu-report"]')
        assert await page.is_visible('[data-testid="menu-analytics"]')
        
        # Test menu navigation
        await page.click('[data-testid="menu-report"]')
        
        # Wait for report page to load
        await page.wait_for_selector('[data-testid="mobile-report-form"]')
    
    async def test_mobile_report_form(self, mobile_browser_setup):
        """Test mobile report form usability."""
        page = mobile_browser_setup
        
        # Navigate to report form
        await page.goto("http://localhost:3000/report")
        
        # Wait for mobile form
        await page.wait_for_selector('[data-testid="mobile-report-form"]')
        
        # Test form fields are properly sized for mobile
        title_input = await page.query_selector('[data-testid="report-title"]')
        title_box = await title_input.bounding_box()
        
        # Verify input is wide enough for mobile (at least 90% of viewport)
        assert title_box['width'] >= 300  # Minimum usable width on mobile
        
        # Test mobile-specific interactions
        await page.fill('[data-testid="report-title"]', "Mobile Test Report")
        
        # Test textarea expansion on mobile
        await page.fill('[data-testid="report-description"]', "This is a test report submitted from a mobile device. The form should be easy to use and properly sized for mobile screens.")
        
        # Test mobile location picker
        await page.click('[data-testid="location-picker-mobile"]')
        
        # Wait for mobile location modal
        await page.wait_for_selector('[data-testid="mobile-location-modal"]')
        
        # Verify modal is properly sized
        modal = await page.query_selector('[data-testid="mobile-location-modal"]')
        modal_box = await modal.bounding_box()
        
        # Modal should take most of the screen on mobile
        assert modal_box['width'] >= 350
        assert modal_box['height'] >= 400


# Test fixtures and utilities
@pytest.fixture
def sample_report_data():
    """Fixture providing sample report data for E2E tests."""
    return {
        "title": "E2E Test Report",
        "description": "This is a test report created during E2E testing to verify the complete workflow.",
        "category": "infrastructure",
        "priority": "medium",
        "location": {
            "lat": 40.7128,
            "lng": -74.0060,
            "address": "123 Main Street, New York, NY"
        },
        "anonymous": False
    }


@pytest.fixture
def mock_api_responses():
    """Fixture providing mock API responses for E2E tests."""
    return {
        "submit_report": {
            "success": True,
            "report_id": "e2e-test-report-123",
            "message": "Report submitted successfully"
        },
        "get_reports": {
            "reports": [
                {
                    "id": "report-1",
                    "title": "Test Report 1",
                    "status": "pending",
                    "category": "infrastructure",
                    "created_at": "2024-01-01T12:00:00Z"
                }
            ],
            "total": 1,
            "page": 1
        },
        "get_analytics": {
            "total_reports": 150,
            "resolved_reports": 120,
            "resolution_rate": 80.0,
            "categories": {
                "infrastructure": 60,
                "safety": 40,
                "environment": 30,
                "other": 20
            }
        }
    }


class TestCrossComponentIntegration:
    """E2E tests for cross-component functionality."""
    
    async def test_real_time_updates(self, browser_setup):
        """Test real-time updates across components."""
        page = browser_setup
        
        # Open dashboard in one tab
        await page.goto("http://localhost:3000/dashboard")
        await page.wait_for_selector('[data-testid="metrics-overview"]')
        
        # Get initial metrics
        initial_total = await page.text_content('[data-testid="total-reports"]')
        
        # Open new tab for report submission
        new_page = await page.context.new_page()
        await new_page.goto("http://localhost:3000/report")
        
        # Submit a new report
        await new_page.fill('[data-testid="report-title"]', "Real-time Test Report")
        await new_page.fill('[data-testid="report-description"]', "Testing real-time updates")
        await new_page.select_option('[data-testid="report-category"]', "infrastructure")
        await new_page.fill('[data-testid="location-lat"]', "40.7128")
        await new_page.fill('[data-testid="location-lng"]', "-74.0060")
        
        await new_page.click('[data-testid="submit-report"]')
        await new_page.wait_for_selector('[data-testid="success-message"]')
        
        # Switch back to dashboard and verify metrics updated
        await page.bring_to_front()
        
        # Wait for real-time update (WebSocket or polling)
        await page.wait_for_function(f"""
            document.querySelector('[data-testid="total-reports"]').textContent !== '{initial_total}'
        """, timeout=10000)
        
        # Verify the count increased
        updated_total = await page.text_content('[data-testid="total-reports"]')
        assert int(updated_total) > int(initial_total)
        
        await new_page.close()
    
    async def test_search_and_filter_integration(self, browser_setup):
        """Test search and filter functionality across components."""
        page = browser_setup
        
        # Navigate to reports page
        await page.goto("http://localhost:3000/reports")
        
        # Wait for reports to load
        await page.wait_for_selector('[data-testid="reports-list"]')
        
        # Test category filter
        await page.select_option('[data-testid="category-filter"]', "infrastructure")
        
        # Wait for filter to apply
        await page.wait_for_timeout(1000)
        
        # Verify all visible reports are infrastructure category
        report_categories = await page.eval_on_selector_all(
            '[data-testid="report-category"]',
            'elements => elements.map(el => el.textContent)'
        )
        
        for category in report_categories:
            assert "infrastructure" in category.lower()
        
        # Test search functionality
        await page.fill('[data-testid="search-input"]', "streetlight")
        await page.press('[data-testid="search-input"]', "Enter")
        
        # Wait for search results
        await page.wait_for_timeout(1000)
        
        # Verify search results contain the search term
        report_titles = await page.eval_on_selector_all(
            '[data-testid="report-title"]',
            'elements => elements.map(el => el.textContent)'
        )
        
        for title in report_titles:
            assert "streetlight" in title.lower()
        
        # Test combined filter and search
        await page.select_option('[data-testid="status-filter"]', "pending")
        
        # Wait for combined filter to apply
        await page.wait_for_timeout(1000)
        
        # Verify results match both search and filter criteria
        report_statuses = await page.eval_on_selector_all(
            '[data-testid="report-status"]',
            'elements => elements.map(el => el.textContent)'
        )
        
        for status in report_statuses:
            assert "pending" in status.lower()
