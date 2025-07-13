#!/usr/bin/env python3
"""
Real Integration Test Runner for CityPulse

This test runner executes comprehensive E2E tests against the actual running
CityPulse application stack, providing true integration validation.
"""

import asyncio
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.real_api_client.fastapi_client import RealFastAPIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RealIntegrationTestRunner:
    """Test runner for real CityPulse integration testing."""
    
    def __init__(self, backend_url: str = "http://localhost:8000", frontend_url: str = "http://localhost:3000"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.start_time = None
        self.end_time = None
        self.results = {
            "test_run_id": f"real-e2e-{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "backend_url": backend_url,
                "frontend_url": frontend_url,
                "test_type": "real_integration"
            },
            "test_suites": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0
            },
            "performance_metrics": {},
            "service_health": {}
        }
    
    async def check_service_health(self) -> Dict[str, bool]:
        """Check if required services are running and accessible."""
        health_status = {
            "backend_api": False,
            "frontend_api": False
        }
        
        # Check backend API
        try:
            async with RealFastAPIClient(self.backend_url) as client:
                connected = await client.connect()
                health_status["backend_api"] = connected
                if connected:
                    logger.info(f"✅ Backend API accessible at {self.backend_url}")
                else:
                    logger.error(f"❌ Backend API not accessible at {self.backend_url}")
        except Exception as e:
            logger.error(f"❌ Backend API health check failed: {e}")
        
        # Check frontend API (basic HTTP check)
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.frontend_url}/api/health", timeout=5.0)
                health_status["frontend_api"] = response.status_code == 200
                if response.status_code == 200:
                    logger.info(f"✅ Frontend API accessible at {self.frontend_url}")
                else:
                    logger.warning(f"⚠️ Frontend API returned {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Frontend API health check failed: {e}")
        
        self.results["service_health"] = health_status
        return health_status
    
    async def run_backend_api_tests(self) -> Dict[str, Any]:
        """Run comprehensive backend API tests."""
        logger.info("🔧 Running Backend API Integration Tests...")
        
        suite_results = {
            "suite_name": "Backend API Integration",
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "errors": 0, "total": 0},
            "performance": {}
        }
        
        try:
            async with RealFastAPIClient(self.backend_url) as client:
                # Test 1: Basic connectivity and health
                logger.info("Testing API connectivity...")
                connected = await client.connect()
                if not connected:
                    suite_results["tests"].append({
                        "name": "API Connectivity",
                        "status": "failed",
                        "details": "Could not connect to backend API"
                    })
                    suite_results["summary"]["failed"] += 1
                    suite_results["summary"]["total"] += 1
                    return suite_results
                
                suite_results["tests"].append({
                    "name": "API Connectivity",
                    "status": "passed",
                    "details": "Successfully connected to backend API"
                })
                suite_results["summary"]["passed"] += 1
                suite_results["summary"]["total"] += 1
                
                # Test 2: Events API (without authentication)
                logger.info("Testing Events API...")
                events_results = await client.test_events_api()
                for test in events_results["tests"]:
                    suite_results["tests"].append({
                        "name": f"Events API - {test['name']}",
                        "status": test["status"],
                        "details": test["details"],
                        "response_time": test.get("response_time", 0)
                    })
                    if test["status"] == "passed":
                        suite_results["summary"]["passed"] += 1
                    elif test["status"] == "failed":
                        suite_results["summary"]["failed"] += 1
                    else:
                        suite_results["summary"]["errors"] += 1
                    suite_results["summary"]["total"] += 1
                
                # Test 3: Analytics API
                logger.info("Testing Analytics API...")
                analytics_results = await client.test_analytics_api()
                for test in analytics_results["tests"]:
                    suite_results["tests"].append({
                        "name": f"Analytics API - {test['name']}",
                        "status": test["status"],
                        "details": test["details"],
                        "response_time": test.get("response_time", 0)
                    })
                    if test["status"] == "passed":
                        suite_results["summary"]["passed"] += 1
                    elif test["status"] == "failed":
                        suite_results["summary"]["failed"] += 1
                    else:
                        suite_results["summary"]["errors"] += 1
                    suite_results["summary"]["total"] += 1
                
                # Test 4: Authentication flow (if test credentials available)
                logger.info("Testing Authentication...")
                # For now, skip auth tests as we don't have test credentials
                suite_results["tests"].append({
                    "name": "Authentication Flow",
                    "status": "skipped",
                    "details": "No test credentials configured"
                })
                suite_results["summary"]["total"] += 1
                
                # Get performance metrics
                suite_results["performance"] = client.get_performance_metrics()
                
                # Cleanup any test data
                await client.cleanup_test_data()
                
        except Exception as e:
            logger.error(f"❌ Backend API tests failed: {e}")
            suite_results["tests"].append({
                "name": "Backend API Test Suite",
                "status": "error",
                "details": f"Test suite error: {str(e)}"
            })
            suite_results["summary"]["errors"] += 1
            suite_results["summary"]["total"] += 1
        
        suite_results["end_time"] = datetime.now().isoformat()
        return suite_results
    
    async def run_frontend_api_tests(self) -> Dict[str, Any]:
        """Run frontend API route tests."""
        logger.info("🌐 Running Frontend API Integration Tests...")
        
        suite_results = {
            "suite_name": "Frontend API Integration",
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "errors": 0, "total": 0},
            "performance": {}
        }
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test 1: Frontend health check
                try:
                    response = await client.get(f"{self.frontend_url}/api/health")
                    test_result = {
                        "name": "Frontend API Health",
                        "status": "passed" if response.status_code == 200 else "failed",
                        "details": f"Status: {response.status_code}",
                        "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
                    }
                    
                    if response.status_code == 200:
                        suite_results["summary"]["passed"] += 1
                    else:
                        suite_results["summary"]["failed"] += 1
                        
                except Exception as e:
                    test_result = {
                        "name": "Frontend API Health",
                        "status": "error",
                        "details": f"Error: {str(e)}"
                    }
                    suite_results["summary"]["errors"] += 1
                
                suite_results["tests"].append(test_result)
                suite_results["summary"]["total"] += 1
                
                # Test 2: Frontend API routes (events)
                try:
                    response = await client.get(f"{self.frontend_url}/api/v1/events")
                    test_result = {
                        "name": "Frontend Events API Route",
                        "status": "passed" if response.status_code in [200, 401] else "failed",
                        "details": f"Status: {response.status_code} (401 expected without auth)",
                        "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
                    }
                    
                    # 401 is expected for protected routes
                    if response.status_code in [200, 401]:
                        suite_results["summary"]["passed"] += 1
                    else:
                        suite_results["summary"]["failed"] += 1
                        
                except Exception as e:
                    test_result = {
                        "name": "Frontend Events API Route",
                        "status": "error",
                        "details": f"Error: {str(e)}"
                    }
                    suite_results["summary"]["errors"] += 1
                
                suite_results["tests"].append(test_result)
                suite_results["summary"]["total"] += 1
                
        except Exception as e:
            logger.error(f"❌ Frontend API tests failed: {e}")
            suite_results["tests"].append({
                "name": "Frontend API Test Suite",
                "status": "error",
                "details": f"Test suite error: {str(e)}"
            })
            suite_results["summary"]["errors"] += 1
            suite_results["summary"]["total"] += 1
        
        suite_results["end_time"] = datetime.now().isoformat()
        return suite_results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all real integration tests."""
        logger.info("🚀 Starting CityPulse Real Integration E2E Tests...")
        
        self.start_time = time.time()
        self.results["start_time"] = datetime.now().isoformat()
        
        # Check service health first
        logger.info("🔍 Checking service health...")
        health_status = await self.check_service_health()
        
        if not health_status["backend_api"]:
            logger.error("❌ Backend API is not accessible. Please start the backend service.")
            self.results["summary"]["errors"] += 1
            return self.results
        
        # Run backend API tests
        backend_results = await self.run_backend_api_tests()
        self.results["test_suites"]["backend_api"] = backend_results
        
        # Update summary
        self.results["summary"]["total"] += backend_results["summary"]["total"]
        self.results["summary"]["passed"] += backend_results["summary"]["passed"]
        self.results["summary"]["failed"] += backend_results["summary"]["failed"]
        self.results["summary"]["errors"] += backend_results["summary"]["errors"]
        
        # Run frontend API tests
        frontend_results = await self.run_frontend_api_tests()
        self.results["test_suites"]["frontend_api"] = frontend_results
        
        # Update summary
        self.results["summary"]["total"] += frontend_results["summary"]["total"]
        self.results["summary"]["passed"] += frontend_results["summary"]["passed"]
        self.results["summary"]["failed"] += frontend_results["summary"]["failed"]
        self.results["summary"]["errors"] += frontend_results["summary"]["errors"]
        
        # Calculate final metrics
        self.end_time = time.time()
        self.results["end_time"] = datetime.now().isoformat()
        self.results["total_duration"] = self.end_time - self.start_time
        
        # Generate summary
        total_tests = self.results["summary"]["total"]
        passed_tests = self.results["summary"]["passed"]
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"✅ Real Integration Tests Complete!")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {self.results['summary']['failed']}")
        logger.info(f"   Errors: {self.results['summary']['errors']}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   Duration: {self.results['total_duration']:.2f} seconds")
        
        return self.results
    
    def save_results(self, output_path: Optional[str] = None) -> str:
        """Save test results to file."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_path = f"reports/real-integration-test-{timestamp}.json"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"📊 Test results saved to: {output_file}")
        return str(output_file)


async def main():
    """Main entry point for the real integration test runner."""
    parser = argparse.ArgumentParser(description="CityPulse Real Integration E2E Test Runner")
    parser.add_argument("--backend-url", default="http://localhost:8000", help="Backend API URL")
    parser.add_argument("--frontend-url", default="http://localhost:3000", help="Frontend URL")
    parser.add_argument("--output", help="Output file path for results")
    parser.add_argument("--suite", choices=["backend", "frontend", "all"], default="all", help="Test suite to run")
    
    args = parser.parse_args()
    
    runner = RealIntegrationTestRunner(args.backend_url, args.frontend_url)
    
    try:
        if args.suite == "all":
            results = await runner.run_all_tests()
        elif args.suite == "backend":
            await runner.check_service_health()
            results = {"test_suites": {"backend_api": await runner.run_backend_api_tests()}}
        elif args.suite == "frontend":
            await runner.check_service_health()
            results = {"test_suites": {"frontend_api": await runner.run_frontend_api_tests()}}
        
        # Save results
        output_file = runner.save_results(args.output)
        
        # Exit with appropriate code
        if runner.results["summary"]["failed"] > 0 or runner.results["summary"]["errors"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("⚠️ Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Test runner error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
