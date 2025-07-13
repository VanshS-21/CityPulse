#!/usr/bin/env python3
"""
CityPulse Unified Test Runner

This is the single entry point for all CityPulse testing. It consolidates
unit tests, integration tests, E2E tests, and frontend tests into one
unified execution framework.
"""

import asyncio
import argparse
import json
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedTestRunner:
    """Unified test runner for all CityPulse test types."""
    
    def __init__(self, environment: str = "test"):
        self.environment = environment
        self.start_time = None
        self.end_time = None
        self.base_path = Path(__file__).parent.parent
        self.config = self._load_config()
        self.results = {
            "test_run_id": f"unified-{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "environment": environment,
            "test_suites": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0
            },
            "performance_metrics": {},
            "coverage_report": {}
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load environment configuration."""
        config_path = self.base_path / "config" / "environments.json"
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config["environments"][self.environment]
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    async def run_unit_tests(self) -> Dict[str, Any]:
        """Run all unit tests."""
        logger.info("🧪 Running Unit Tests...")
        
        suite_results = {
            "suite_name": "Unit Tests",
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "errors": 0, "total": 0}
        }
        
        try:
            # Run pytest for unit tests
            cmd = [
                sys.executable, "-m", "pytest",
                str(self.base_path / "tests" / "unit"),
                "-v", "--json-report", "--json-report-file=/tmp/unit-tests.json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Parse results
            if result.returncode == 0:
                suite_results["status"] = "passed"
                logger.info("✅ Unit tests completed successfully")
            else:
                suite_results["status"] = "failed"
                logger.warning("⚠️ Some unit tests failed")
            
            # Try to load detailed results
            try:
                with open("/tmp/unit-tests.json", 'r') as f:
                    detailed_results = json.load(f)
                    suite_results["summary"] = detailed_results.get("summary", {})
            except:
                pass
                
        except Exception as e:
            logger.error(f"❌ Unit tests failed: {e}")
            suite_results["status"] = "error"
            suite_results["error"] = str(e)
        
        suite_results["end_time"] = datetime.now().isoformat()
        return suite_results
    
    async def run_integration_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        logger.info("🔗 Running Integration Tests...")
        
        suite_results = {
            "suite_name": "Integration Tests",
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "errors": 0, "total": 0}
        }
        
        try:
            # Run pytest for integration tests
            cmd = [
                sys.executable, "-m", "pytest",
                str(self.base_path / "tests" / "integration"),
                "-v", "--json-report", "--json-report-file=/tmp/integration-tests.json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                suite_results["status"] = "passed"
                logger.info("✅ Integration tests completed successfully")
            else:
                suite_results["status"] = "failed"
                logger.warning("⚠️ Some integration tests failed")
            
            # Try to load detailed results
            try:
                with open("/tmp/integration-tests.json", 'r') as f:
                    detailed_results = json.load(f)
                    suite_results["summary"] = detailed_results.get("summary", {})
            except:
                pass
                
        except Exception as e:
            logger.error(f"❌ Integration tests failed: {e}")
            suite_results["status"] = "error"
            suite_results["error"] = str(e)
        
        suite_results["end_time"] = datetime.now().isoformat()
        return suite_results
    
    async def run_e2e_tests(self) -> Dict[str, Any]:
        """Run all end-to-end tests."""
        logger.info("🌐 Running End-to-End Tests...")
        
        suite_results = {
            "suite_name": "End-to-End Tests",
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "errors": 0, "total": 0}
        }
        
        try:
            # Run pytest for E2E tests
            cmd = [
                sys.executable, "-m", "pytest",
                str(self.base_path / "tests" / "e2e"),
                "-v", "--json-report", "--json-report-file=/tmp/e2e-tests.json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                suite_results["status"] = "passed"
                logger.info("✅ E2E tests completed successfully")
            else:
                suite_results["status"] = "failed"
                logger.warning("⚠️ Some E2E tests failed")
            
            # Try to load detailed results
            try:
                with open("/tmp/e2e-tests.json", 'r') as f:
                    detailed_results = json.load(f)
                    suite_results["summary"] = detailed_results.get("summary", {})
            except:
                pass
                
        except Exception as e:
            logger.error(f"❌ E2E tests failed: {e}")
            suite_results["status"] = "error"
            suite_results["error"] = str(e)
        
        suite_results["end_time"] = datetime.now().isoformat()
        return suite_results
    
    async def run_frontend_tests(self) -> Dict[str, Any]:
        """Run all frontend tests."""
        logger.info("⚛️ Running Frontend Tests...")
        
        suite_results = {
            "suite_name": "Frontend Tests",
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "errors": 0, "total": 0}
        }
        
        try:
            # Run Jest tests
            cmd = ["npm", "test", "--", "--json", "--outputFile=/tmp/frontend-tests.json"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=self.base_path.parent)
            
            if result.returncode == 0:
                suite_results["status"] = "passed"
                logger.info("✅ Frontend tests completed successfully")
            else:
                suite_results["status"] = "failed"
                logger.warning("⚠️ Some frontend tests failed")
            
            # Try to load detailed results
            try:
                with open("/tmp/frontend-tests.json", 'r') as f:
                    detailed_results = json.load(f)
                    if "testResults" in detailed_results:
                        total = len(detailed_results["testResults"])
                        passed = sum(1 for test in detailed_results["testResults"] if test.get("status") == "passed")
                        suite_results["summary"] = {
                            "total": total,
                            "passed": passed,
                            "failed": total - passed,
                            "errors": 0
                        }
            except:
                pass
                
        except Exception as e:
            logger.error(f"❌ Frontend tests failed: {e}")
            suite_results["status"] = "error"
            suite_results["error"] = str(e)
        
        suite_results["end_time"] = datetime.now().isoformat()
        return suite_results
    
    async def run_all_tests(self, test_types: List[str] = None) -> Dict[str, Any]:
        """Run all specified test types."""
        if test_types is None:
            test_types = ["unit", "integration", "e2e", "frontend"]
        
        logger.info(f"🚀 Starting CityPulse Unified Test Suite...")
        logger.info(f"   Environment: {self.environment}")
        logger.info(f"   Test Types: {', '.join(test_types)}")
        
        self.start_time = time.time()
        self.results["start_time"] = datetime.now().isoformat()
        
        # Run test suites
        if "unit" in test_types:
            unit_results = await self.run_unit_tests()
            self.results["test_suites"]["unit"] = unit_results
            self._update_summary(unit_results)
        
        if "integration" in test_types:
            integration_results = await self.run_integration_tests()
            self.results["test_suites"]["integration"] = integration_results
            self._update_summary(integration_results)
        
        if "e2e" in test_types:
            e2e_results = await self.run_e2e_tests()
            self.results["test_suites"]["e2e"] = e2e_results
            self._update_summary(e2e_results)
        
        if "frontend" in test_types:
            frontend_results = await self.run_frontend_tests()
            self.results["test_suites"]["frontend"] = frontend_results
            self._update_summary(frontend_results)
        
        # Calculate final metrics
        self.end_time = time.time()
        self.results["end_time"] = datetime.now().isoformat()
        self.results["total_duration"] = self.end_time - self.start_time
        
        # Generate summary
        self._generate_summary()
        
        return self.results
    
    def _update_summary(self, suite_results: Dict[str, Any]):
        """Update overall summary with suite results."""
        summary = suite_results.get("summary", {})
        self.results["summary"]["total_tests"] += summary.get("total", 0)
        self.results["summary"]["passed"] += summary.get("passed", 0)
        self.results["summary"]["failed"] += summary.get("failed", 0)
        self.results["summary"]["errors"] += summary.get("errors", 0)
        self.results["summary"]["skipped"] += summary.get("skipped", 0)
    
    def _generate_summary(self):
        """Generate final test summary."""
        total = self.results["summary"]["total_tests"]
        passed = self.results["summary"]["passed"]
        failed = self.results["summary"]["failed"]
        errors = self.results["summary"]["errors"]
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        logger.info(f"✅ Unified Test Suite Complete!")
        logger.info(f"   Total Tests: {total}")
        logger.info(f"   Passed: {passed}")
        logger.info(f"   Failed: {failed}")
        logger.info(f"   Errors: {errors}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   Duration: {self.results['total_duration']:.2f} seconds")
    
    def save_results(self, output_path: Optional[str] = None) -> str:
        """Save test results to file."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_path = f"reports/unified-reports/unified-test-{timestamp}.json"
        
        output_file = self.base_path / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"📊 Test results saved to: {output_file}")
        return str(output_file)


async def main():
    """Main entry point for the unified test runner."""
    parser = argparse.ArgumentParser(description="CityPulse Unified Test Runner")
    parser.add_argument("--environment", default="test", help="Test environment")
    parser.add_argument("--types", nargs="+", choices=["unit", "integration", "e2e", "frontend"], 
                       default=["unit", "integration", "e2e", "frontend"], help="Test types to run")
    parser.add_argument("--output", help="Output file path for results")
    
    args = parser.parse_args()
    
    runner = UnifiedTestRunner(args.environment)
    
    try:
        results = await runner.run_all_tests(args.types)
        output_file = runner.save_results(args.output)
        
        # Exit with appropriate code
        if results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
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
