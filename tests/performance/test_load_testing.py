"""
Performance and load testing for CityPulse application.
Tests system performance under various load conditions and identifies bottlenecks.
"""

import pytest
import asyncio
import time
import statistics
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Tuple
import requests
import json
import threading
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    response_times: List[float]
    success_count: int
    error_count: int
    total_requests: int
    start_time: datetime
    end_time: datetime
    throughput: float
    error_rate: float
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float


class LoadTestRunner:
    """Load test runner for performance testing."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize load test runner."""
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
    def run_load_test(
        self,
        endpoint: str,
        concurrent_users: int = 10,
        duration_seconds: int = 60,
        ramp_up_seconds: int = 10,
        method: str = "GET",
        payload: Dict = None,
        headers: Dict = None
    ) -> PerformanceMetrics:
        """Run load test against an endpoint."""
        logger.info(f"Starting load test: {concurrent_users} users, {duration_seconds}s duration")
        
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(seconds=duration_seconds)
        
        # Results collection
        response_times = []
        success_count = 0
        error_count = 0
        total_requests = 0
        
        # Thread synchronization
        results_lock = threading.Lock()
        
        def worker_thread(user_id: int, start_delay: float):
            """Worker thread for load testing."""
            nonlocal response_times, success_count, error_count, total_requests
            
            # Ramp-up delay
            time.sleep(start_delay)
            
            while datetime.utcnow() < end_time:
                request_start = time.time()
                
                try:
                    # Make request
                    if method.upper() == "GET":
                        response = self.session.get(
                            f"{self.base_url}{endpoint}",
                            headers=headers,
                            timeout=30
                        )
                    elif method.upper() == "POST":
                        response = self.session.post(
                            f"{self.base_url}{endpoint}",
                            json=payload,
                            headers=headers,
                            timeout=30
                        )
                    elif method.upper() == "PUT":
                        response = self.session.put(
                            f"{self.base_url}{endpoint}",
                            json=payload,
                            headers=headers,
                            timeout=30
                        )
                    else:
                        raise ValueError(f"Unsupported method: {method}")
                    
                    request_end = time.time()
                    response_time = (request_end - request_start) * 1000  # Convert to ms
                    
                    # Record results
                    with results_lock:
                        response_times.append(response_time)
                        total_requests += 1
                        
                        if response.status_code < 400:
                            success_count += 1
                        else:
                            error_count += 1
                            logger.warning(f"Request failed: {response.status_code}")
                
                except Exception as e:
                    request_end = time.time()
                    response_time = (request_end - request_start) * 1000
                    
                    with results_lock:
                        response_times.append(response_time)
                        total_requests += 1
                        error_count += 1
                        logger.error(f"Request error: {e}")
                
                # Small delay between requests
                time.sleep(0.1)
        
        # Start worker threads with ramp-up
        threads = []
        for user_id in range(concurrent_users):
            start_delay = (user_id / concurrent_users) * ramp_up_seconds
            thread = threading.Thread(target=worker_thread, args=(user_id, start_delay))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        actual_end_time = datetime.utcnow()
        actual_duration = (actual_end_time - start_time).total_seconds()
        
        # Calculate metrics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = p95_response_time = p99_response_time = 0
            min_response_time = max_response_time = 0
        
        throughput = total_requests / actual_duration if actual_duration > 0 else 0
        error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0
        
        metrics = PerformanceMetrics(
            response_times=response_times,
            success_count=success_count,
            error_count=error_count,
            total_requests=total_requests,
            start_time=start_time,
            end_time=actual_end_time,
            throughput=throughput,
            error_rate=error_rate,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time
        )
        
        logger.info(f"Load test completed: {total_requests} requests, {throughput:.2f} req/s, {error_rate:.2f}% errors")
        
        return metrics


class TestAPIPerformance:
    """Performance tests for API endpoints."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.load_tester = LoadTestRunner()
        self.auth_headers = {"Authorization": "Bearer test-token"}
    
    @pytest.mark.performance
    def test_events_endpoint_load(self):
        """Test events endpoint under load."""
        metrics = self.load_tester.run_load_test(
            endpoint="/api/v1/events",
            concurrent_users=20,
            duration_seconds=60,
            ramp_up_seconds=10,
            headers=self.auth_headers
        )
        
        # Performance assertions
        assert metrics.error_rate < 5.0, f"Error rate too high: {metrics.error_rate}%"
        assert metrics.avg_response_time < 2000, f"Average response time too high: {metrics.avg_response_time}ms"
        assert metrics.p95_response_time < 5000, f"95th percentile response time too high: {metrics.p95_response_time}ms"
        assert metrics.throughput > 10, f"Throughput too low: {metrics.throughput} req/s"
    
    @pytest.mark.performance
    def test_create_event_performance(self):
        """Test event creation performance."""
        event_payload = {
            "title": "Performance Test Event",
            "description": "Event created during performance testing",
            "category": "infrastructure",
            "priority": "medium",
            "location": {"lat": 40.7128, "lng": -74.0060}
        }
        
        metrics = self.load_tester.run_load_test(
            endpoint="/api/v1/events",
            concurrent_users=10,
            duration_seconds=30,
            ramp_up_seconds=5,
            method="POST",
            payload=event_payload,
            headers=self.auth_headers
        )
        
        # Performance assertions for write operations
        assert metrics.error_rate < 2.0, f"Error rate too high for writes: {metrics.error_rate}%"
        assert metrics.avg_response_time < 3000, f"Average response time too high for writes: {metrics.avg_response_time}ms"
        assert metrics.throughput > 5, f"Write throughput too low: {metrics.throughput} req/s"
    
    @pytest.mark.performance
    def test_analytics_endpoint_performance(self):
        """Test analytics endpoint performance."""
        metrics = self.load_tester.run_load_test(
            endpoint="/api/v1/analytics/trends?date_range=week",
            concurrent_users=15,
            duration_seconds=45,
            ramp_up_seconds=8,
            headers=self.auth_headers
        )
        
        # Analytics queries may be slower but should still be reasonable
        assert metrics.error_rate < 3.0, f"Error rate too high for analytics: {metrics.error_rate}%"
        assert metrics.avg_response_time < 5000, f"Average response time too high for analytics: {metrics.avg_response_time}ms"
        assert metrics.p99_response_time < 10000, f"99th percentile too high for analytics: {metrics.p99_response_time}ms"
    
    @pytest.mark.performance
    def test_concurrent_read_write_performance(self):
        """Test performance under mixed read/write load."""
        # Start read load test in background
        read_thread = threading.Thread(
            target=lambda: self.load_tester.run_load_test(
                endpoint="/api/v1/events",
                concurrent_users=15,
                duration_seconds=60,
                headers=self.auth_headers
            )
        )
        
        # Start write load test
        write_payload = {
            "title": "Concurrent Test Event",
            "description": "Event for concurrent testing",
            "category": "other",
            "priority": "low",
            "location": {"lat": 40.7128, "lng": -74.0060}
        }
        
        read_thread.start()
        
        write_metrics = self.load_tester.run_load_test(
            endpoint="/api/v1/events",
            concurrent_users=5,
            duration_seconds=60,
            method="POST",
            payload=write_payload,
            headers=self.auth_headers
        )
        
        read_thread.join()
        
        # Under mixed load, performance should degrade gracefully
        assert write_metrics.error_rate < 10.0, f"Write error rate too high under mixed load: {write_metrics.error_rate}%"
        assert write_metrics.avg_response_time < 5000, f"Write response time too high under mixed load: {write_metrics.avg_response_time}ms"


class TestDatabasePerformance:
    """Performance tests for database operations."""
    
    @pytest.mark.performance
    def test_firestore_read_performance(self):
        """Test Firestore read performance."""
        # This would test actual Firestore operations
        # For now, we'll simulate the test structure
        
        start_time = time.time()
        
        # Simulate multiple concurrent reads
        def simulate_firestore_read():
            # Simulate read operation
            time.sleep(0.05)  # 50ms simulated read time
            return {"id": "test", "data": "value"}
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(simulate_firestore_read) for _ in range(100)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 10.0, f"Firestore read operations took too long: {duration}s"
        assert len(results) == 100, "Not all read operations completed"
    
    @pytest.mark.performance
    def test_bigquery_query_performance(self):
        """Test BigQuery query performance."""
        # Simulate BigQuery query performance test
        
        start_time = time.time()
        
        # Simulate analytics query
        def simulate_bigquery_query():
            # Simulate query execution time
            time.sleep(0.2)  # 200ms simulated query time
            return [{"category": "infrastructure", "count": 50}]
        
        # Test concurrent queries
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(simulate_bigquery_query) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # BigQuery queries can be slower but should handle concurrency
        assert duration < 15.0, f"BigQuery queries took too long: {duration}s"
        assert len(results) == 10, "Not all queries completed"


class TestFrontendPerformance:
    """Performance tests for frontend components."""
    
    @pytest.mark.performance
    async def test_page_load_performance(self):
        """Test frontend page load performance."""
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            
            # Measure page load time
            start_time = time.time()
            await page.goto("http://localhost:3000")
            await page.wait_for_load_state("networkidle")
            end_time = time.time()
            
            load_time = (end_time - start_time) * 1000  # Convert to ms
            
            # Performance assertions
            assert load_time < 3000, f"Page load time too high: {load_time}ms"
            
            # Check for performance metrics
            performance_metrics = await page.evaluate("""
                () => {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    return {
                        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                        firstPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-paint')?.startTime,
                        firstContentfulPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint')?.startTime
                    };
                }
            """)
            
            # Web Vitals assertions
            if performance_metrics["firstContentfulPaint"]:
                assert performance_metrics["firstContentfulPaint"] < 2000, "First Contentful Paint too slow"
            
            await browser.close()
    
    @pytest.mark.performance
    async def test_dashboard_rendering_performance(self):
        """Test dashboard rendering performance with large datasets."""
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            
            # Navigate to dashboard
            await page.goto("http://localhost:3000/dashboard")
            
            # Measure rendering time for charts
            start_time = time.time()
            await page.wait_for_selector('[data-testid="analytics-charts"]')
            end_time = time.time()
            
            render_time = (end_time - start_time) * 1000
            
            # Dashboard should render quickly even with data
            assert render_time < 5000, f"Dashboard rendering too slow: {render_time}ms"
            
            # Test scroll performance
            scroll_start = time.time()
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(100)
            scroll_end = time.time()
            
            scroll_time = (scroll_end - scroll_start) * 1000
            assert scroll_time < 1000, f"Scroll performance too slow: {scroll_time}ms"
            
            await browser.close()


class TestScalabilityLimits:
    """Tests to identify scalability limits."""
    
    @pytest.mark.performance
    def test_user_scalability_limits(self):
        """Test system behavior under increasing user load."""
        user_counts = [10, 25, 50, 100, 200]
        results = []
        
        for user_count in user_counts:
            logger.info(f"Testing with {user_count} concurrent users")
            
            metrics = LoadTestRunner().run_load_test(
                endpoint="/api/v1/events",
                concurrent_users=user_count,
                duration_seconds=30,
                ramp_up_seconds=5
            )
            
            results.append({
                "users": user_count,
                "throughput": metrics.throughput,
                "avg_response_time": metrics.avg_response_time,
                "error_rate": metrics.error_rate
            })
            
            # Stop if error rate becomes too high
            if metrics.error_rate > 20:
                logger.warning(f"High error rate at {user_count} users: {metrics.error_rate}%")
                break
        
        # Analyze scalability
        for i, result in enumerate(results):
            logger.info(f"Users: {result['users']}, Throughput: {result['throughput']:.2f} req/s, "
                       f"Avg Response: {result['avg_response_time']:.2f}ms, Errors: {result['error_rate']:.2f}%")
            
            # Ensure reasonable performance up to a certain point
            if result['users'] <= 50:
                assert result['error_rate'] < 5.0, f"Error rate too high at {result['users']} users"
                assert result['avg_response_time'] < 3000, f"Response time too high at {result['users']} users"
    
    @pytest.mark.performance
    def test_data_volume_scalability(self):
        """Test system behavior with increasing data volumes."""
        # This would test with different data volumes
        # For now, we'll simulate the test structure
        
        data_sizes = [100, 500, 1000, 5000]  # Number of records
        
        for size in data_sizes:
            logger.info(f"Testing with {size} data records")
            
            # Simulate query with large dataset
            start_time = time.time()
            
            # Simulate processing time based on data size
            processing_time = size * 0.001  # 1ms per record
            time.sleep(processing_time)
            
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            
            # Performance should scale reasonably with data size
            expected_max_time = size * 2  # 2ms per record maximum
            assert duration < expected_max_time, f"Processing time too high for {size} records: {duration}ms"
            
            logger.info(f"Processed {size} records in {duration:.2f}ms")


# Performance test utilities
def generate_performance_report(metrics: PerformanceMetrics, test_name: str) -> Dict[str, Any]:
    """Generate performance test report."""
    return {
        "test_name": test_name,
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "total_requests": metrics.total_requests,
            "success_count": metrics.success_count,
            "error_count": metrics.error_count,
            "error_rate": metrics.error_rate,
            "throughput": metrics.throughput,
            "response_times": {
                "average": metrics.avg_response_time,
                "p95": metrics.p95_response_time,
                "p99": metrics.p99_response_time,
                "min": metrics.min_response_time,
                "max": metrics.max_response_time
            },
            "duration": (metrics.end_time - metrics.start_time).total_seconds()
        }
    }


@pytest.fixture
def performance_thresholds():
    """Performance test thresholds."""
    return {
        "api_response_time_p95": 2000,  # 95th percentile < 2 seconds
        "api_response_time_p99": 5000,  # 99th percentile < 5 seconds
        "api_error_rate": 5.0,  # < 5% error rate
        "api_throughput_min": 10,  # > 10 requests/second
        "page_load_time": 3000,  # < 3 seconds
        "dashboard_render_time": 5000,  # < 5 seconds
        "database_query_time": 1000  # < 1 second for simple queries
    }
