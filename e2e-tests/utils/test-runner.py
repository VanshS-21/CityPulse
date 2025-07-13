#!/usr/bin/env python3
"""
CityPulse E2E Test Runner

Comprehensive test execution framework that:
- Runs different test suites based on current development phase
- Provides detailed reporting and metrics
- Handles test environment setup and cleanup
- Supports parallel execution and filtering
"""

import asyncio
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import subprocess
import concurrent.futures

class E2ETestRunner:
    """Main test runner for CityPulse E2E tests."""
    
    def __init__(self, environment: str = "test"):
        self.environment = environment
        self.config = self._load_config()
        self.start_time = None
        self.end_time = None
        self.results = {
            "environment": environment,
            "start_time": None,
            "end_time": None,
            "duration": 0,
            "suites": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0
            },
            "performance_metrics": {},
            "coverage_report": {}
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load test configuration."""
        config_path = Path(__file__).parent.parent / "config" / "environments.json"
        with open(config_path) as f:
            configs = json.load(f)
        return configs.get(self.environment, configs["test"])
    
    async def run_api_tests(self, filters: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run API integration tests."""
        print("🔧 Running API Integration Tests...")
        
        test_command = [
            "python", "-m", "pytest",
            "features/",
            "-v",
            "-m", "api",
            "--json-report",
            "--json-report-file=reports/api-tests.json"
        ]
        
        if filters:
            test_command.extend(["-k", " or ".join(filters)])
        
        result = await self._run_subprocess(test_command)
        
        # Parse results
        try:
            with open("reports/api-tests.json") as f:
                test_results = json.load(f)
            
            suite_result = {
                "name": "API Integration Tests",
                "status": "passed" if result.returncode == 0 else "failed",
                "tests": test_results.get("tests", []),
                "summary": test_results.get("summary", {}),
                "duration": test_results.get("duration", 0)
            }
        except Exception as e:
            suite_result = {
                "name": "API Integration Tests",
                "status": "error",
                "error": str(e),
                "duration": 0
            }
        
        self.results["suites"]["api_tests"] = suite_result
        return suite_result
    
    async def run_pipeline_tests(self, filters: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run data pipeline E2E tests."""
        print("🚰 Running Data Pipeline Tests...")
        
        test_command = [
            "python", "-m", "pytest",
            "features/",
            "-v",
            "-m", "pipeline",
            "--json-report",
            "--json-report-file=reports/pipeline-tests.json"
        ]
        
        if filters:
            test_command.extend(["-k", " or ".join(filters)])
        
        result = await self._run_subprocess(test_command)
        
        try:
            with open("reports/pipeline-tests.json") as f:
                test_results = json.load(f)
            
            suite_result = {
                "name": "Data Pipeline Tests",
                "status": "passed" if result.returncode == 0 else "failed",
                "tests": test_results.get("tests", []),
                "summary": test_results.get("summary", {}),
                "duration": test_results.get("duration", 0)
            }
        except Exception as e:
            suite_result = {
                "name": "Data Pipeline Tests",
                "status": "error",
                "error": str(e),
                "duration": 0
            }
        
        self.results["suites"]["pipeline_tests"] = suite_result
        return suite_result
    
    async def run_frontend_tests(self, filters: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run frontend integration tests."""
        print("🌐 Running Frontend Integration Tests...")
        
        # Since frontend is minimal, run basic tests only
        test_command = [
            "npm", "run", "test:e2e:frontend"
        ]
        
        result = await self._run_subprocess(test_command)
        
        suite_result = {
            "name": "Frontend Integration Tests",
            "status": "passed" if result.returncode == 0 else "failed",
            "tests": [],
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "duration": 0,
            "note": "Minimal frontend testing - full implementation pending"
        }
        
        self.results["suites"]["frontend_tests"] = suite_result
        return suite_result
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance and load tests."""
        print("⚡ Running Performance Tests...")
        
        # API performance tests
        api_perf_command = [
            "python", "-m", "pytest",
            "e2e-tests/performance/api-load-tests/",
            "-v",
            "--json-report",
            "--json-report-file=e2e-tests/reports/performance-tests.json"
        ]
        
        result = await self._run_subprocess(api_perf_command)
        
        suite_result = {
            "name": "Performance Tests",
            "status": "passed" if result.returncode == 0 else "failed",
            "tests": [],
            "summary": {},
            "duration": 0,
            "metrics": {
                "api_response_times": {},
                "throughput": {},
                "error_rates": {}
            }
        }
        
        self.results["suites"]["performance_tests"] = suite_result
        return suite_result
    
    async def run_security_tests(self) -> Dict[str, Any]:
        """Run security validation tests."""
        print("🔒 Running Security Tests...")
        
        security_command = [
            "python", "-m", "pytest",
            "e2e-tests/security/",
            "-v",
            "--json-report",
            "--json-report-file=e2e-tests/reports/security-tests.json"
        ]
        
        result = await self._run_subprocess(security_command)
        
        suite_result = {
            "name": "Security Tests",
            "status": "passed" if result.returncode == 0 else "failed",
            "tests": [],
            "summary": {},
            "duration": 0
        }
        
        self.results["suites"]["security_tests"] = suite_result
        return suite_result
    
    async def _run_subprocess(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run subprocess command asynchronously."""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return subprocess.CompletedProcess(
            args=command,
            returncode=process.returncode,
            stdout=stdout.decode(),
            stderr=stderr.decode()
        )
    
    def calculate_summary(self):
        """Calculate overall test summary."""
        summary = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0
        }
        
        for suite_name, suite_result in self.results["suites"].items():
            if "summary" in suite_result:
                suite_summary = suite_result["summary"]
                summary["total_tests"] += suite_summary.get("total", 0)
                summary["passed"] += suite_summary.get("passed", 0)
                summary["failed"] += suite_summary.get("failed", 0)
                summary["skipped"] += suite_summary.get("skipped", 0)
            
            if suite_result.get("status") == "error":
                summary["errors"] += 1
        
        self.results["summary"] = summary
    
    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        self.calculate_summary()
        
        # Create reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed JSON report
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        json_report_path = reports_dir / f"e2e-test-report-{timestamp}.json"
        
        with open(json_report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate HTML report
        html_report = self._generate_html_report()
        html_report_path = reports_dir / f"e2e-test-report-{timestamp}.html"
        
        with open(html_report_path, 'w') as f:
            f.write(html_report)
        
        return str(html_report_path)
    
    def _generate_html_report(self) -> str:
        """Generate HTML test report."""
        summary = self.results["summary"]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CityPulse E2E Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .metric {{ background: #e8f4f8; padding: 15px; border-radius: 5px; text-align: center; }}
                .suite {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .error {{ color: orange; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>CityPulse E2E Test Report</h1>
                <p>Environment: {self.environment}</p>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Duration: {self.results['duration']:.2f} seconds</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h3>Total Tests</h3>
                    <p>{summary['total_tests']}</p>
                </div>
                <div class="metric">
                    <h3>Passed</h3>
                    <p class="passed">{summary['passed']}</p>
                </div>
                <div class="metric">
                    <h3>Failed</h3>
                    <p class="failed">{summary['failed']}</p>
                </div>
                <div class="metric">
                    <h3>Errors</h3>
                    <p class="error">{summary['errors']}</p>
                </div>
            </div>
            
            <h2>Test Suites</h2>
        """
        
        for suite_name, suite_result in self.results["suites"].items():
            status_class = suite_result.get("status", "unknown")
            html += f"""
            <div class="suite">
                <h3 class="{status_class}">{suite_result.get('name', suite_name)}</h3>
                <p>Status: <span class="{status_class}">{suite_result.get('status', 'unknown').upper()}</span></p>
                <p>Duration: {suite_result.get('duration', 0):.2f} seconds</p>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    async def run_full_suite(
        self,
        include_suites: Optional[List[str]] = None,
        exclude_suites: Optional[List[str]] = None,
        filters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run the complete E2E test suite."""
        
        self.start_time = time.time()
        self.results["start_time"] = datetime.now().isoformat()
        
        print("🚀 Starting CityPulse E2E Test Suite...")
        print(f"   Environment: {self.environment}")
        print(f"   Timestamp: {self.results['start_time']}")
        
        # Define available test suites
        available_suites = {
            "api": self.run_api_tests,
            "pipeline": self.run_pipeline_tests,
            "frontend": self.run_frontend_tests,
            "performance": self.run_performance_tests,
            "security": self.run_security_tests
        }
        
        # Determine which suites to run
        if include_suites:
            suites_to_run = {k: v for k, v in available_suites.items() if k in include_suites}
        else:
            suites_to_run = available_suites.copy()
        
        if exclude_suites:
            for suite in exclude_suites:
                suites_to_run.pop(suite, None)
        
        # Run test suites
        for suite_name, suite_func in suites_to_run.items():
            try:
                if suite_name in ["api", "pipeline"] and filters:
                    await suite_func(filters)
                else:
                    await suite_func()
            except Exception as e:
                print(f"❌ Error running {suite_name} tests: {e}")
                self.results["suites"][f"{suite_name}_tests"] = {
                    "name": f"{suite_name.title()} Tests",
                    "status": "error",
                    "error": str(e),
                    "duration": 0
                }
        
        self.end_time = time.time()
        self.results["end_time"] = datetime.now().isoformat()
        self.results["duration"] = self.end_time - self.start_time
        
        # Generate report
        report_path = self.generate_report()
        
        print(f"\n✅ E2E Test Suite Complete!")
        print(f"   Duration: {self.results['duration']:.2f} seconds")
        print(f"   Report: {report_path}")
        
        return self.results

def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="CityPulse E2E Test Runner")
    parser.add_argument("--environment", "-e", default="test", help="Test environment")
    parser.add_argument("--include", "-i", nargs="+", help="Include specific test suites")
    parser.add_argument("--exclude", "-x", nargs="+", help="Exclude specific test suites")
    parser.add_argument("--filter", "-f", nargs="+", help="Test name filters")
    
    args = parser.parse_args()
    
    runner = E2ETestRunner(args.environment)
    
    try:
        results = asyncio.run(runner.run_full_suite(
            include_suites=args.include,
            exclude_suites=args.exclude,
            filters=args.filter
        ))
        
        # Exit with appropriate code
        if results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
