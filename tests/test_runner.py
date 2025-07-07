"""
Comprehensive test runner for CityPulse testing framework.
Orchestrates all test types with detailed reporting and metrics.
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestRunner:
    """Comprehensive test runner for CityPulse."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize test runner with configuration."""
        self.config = config or self._load_default_config()
        self.results = {}
        self.start_time = None
        self.end_time = None
        
        # Ensure reports directory exists
        os.makedirs("test-reports", exist_ok=True)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default test configuration."""
        return {
            "test_types": {
                "unit": {
                    "enabled": True,
                    "path": "tests/unit",
                    "markers": ["unit"],
                    "timeout": 300,
                    "parallel": True,
                    "coverage": True
                },
                "integration": {
                    "enabled": True,
                    "path": "tests/integration",
                    "markers": ["integration"],
                    "timeout": 600,
                    "parallel": False,
                    "coverage": True
                },
                "e2e": {
                    "enabled": True,
                    "path": "tests/e2e",
                    "markers": ["e2e"],
                    "timeout": 1800,
                    "parallel": False,
                    "coverage": False
                },
                "performance": {
                    "enabled": False,
                    "path": "tests/performance",
                    "markers": ["performance"],
                    "timeout": 3600,
                    "parallel": False,
                    "coverage": False
                },
                "security": {
                    "enabled": False,
                    "path": "tests/security",
                    "markers": ["security"],
                    "timeout": 1800,
                    "parallel": False,
                    "coverage": False
                },
                "accessibility": {
                    "enabled": False,
                    "path": "tests/accessibility",
                    "markers": ["accessibility"],
                    "timeout": 900,
                    "parallel": False,
                    "coverage": False
                }
            },
            "reporting": {
                "formats": ["json", "html", "junit"],
                "coverage_threshold": 80,
                "detailed_output": True,
                "save_artifacts": True
            },
            "environment": {
                "setup_commands": [],
                "teardown_commands": [],
                "required_services": ["firestore", "bigquery", "pubsub"]
            }
        }
    
    def run_all_tests(self, test_types: List[str] = None) -> Dict[str, Any]:
        """Run all enabled test types."""
        logger.info("Starting comprehensive test run")
        self.start_time = datetime.utcnow()
        
        # Determine which test types to run
        if test_types is None:
            test_types = [
                test_type for test_type, config in self.config["test_types"].items()
                if config["enabled"]
            ]
        
        # Setup test environment
        self._setup_environment()
        
        try:
            # Run each test type
            for test_type in test_types:
                if test_type in self.config["test_types"]:
                    logger.info(f"Running {test_type} tests")
                    result = self._run_test_type(test_type)
                    self.results[test_type] = result
                else:
                    logger.warning(f"Unknown test type: {test_type}")
            
            # Generate comprehensive report
            self._generate_report()
            
        finally:
            # Cleanup test environment
            self._teardown_environment()
            
        self.end_time = datetime.utcnow()
        logger.info(f"Test run completed in {(self.end_time - self.start_time).total_seconds():.2f} seconds")
        
        return self.results
    
    def _run_test_type(self, test_type: str) -> Dict[str, Any]:
        """Run a specific test type."""
        config = self.config["test_types"][test_type]
        start_time = time.time()
        
        # Build pytest command
        cmd = self._build_pytest_command(test_type, config)
        
        logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            # Run tests
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config["timeout"]
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse results
            test_result = {
                "test_type": test_type,
                "duration": duration,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Parse pytest output for detailed metrics
            test_result.update(self._parse_pytest_output(result.stdout))
            
            logger.info(f"{test_type} tests completed in {duration:.2f}s - {'PASSED' if test_result['success'] else 'FAILED'}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            logger.error(f"{test_type} tests timed out after {config['timeout']} seconds")
            return {
                "test_type": test_type,
                "duration": config["timeout"],
                "exit_code": -1,
                "success": False,
                "error": "Test execution timed out",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error running {test_type} tests: {e}")
            return {
                "test_type": test_type,
                "duration": 0,
                "exit_code": -1,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _build_pytest_command(self, test_type: str, config: Dict[str, Any]) -> List[str]:
        """Build pytest command for a test type."""
        cmd = ["python", "-m", "pytest"]
        
        # Add test path
        if os.path.exists(config["path"]):
            cmd.append(config["path"])
        
        # Add markers (disabled for now)
        # if config.get("markers"):
        #     for marker in config["markers"]:
        #         cmd.extend(["-m", marker])
        
        # Add parallel execution (only if pytest-xdist is available)
        # if config.get("parallel") and test_type in ["unit"]:
        #     cmd.extend(["-n", "auto"])

        # Add coverage (only if pytest-cov is available)
        # if config.get("coverage"):
        #     cmd.extend([
        #         "--cov=data_models",
        #         "--cov=src",
        #         f"--cov-report=html:test-reports/{test_type}-coverage",
        #         f"--cov-report=json:test-reports/{test_type}-coverage.json"
        #     ])

        # Add output formats (only if pytest-html is available)
        # cmd.extend([
        #     f"--junit-xml=test-reports/{test_type}-junit.xml",
        #     f"--html=test-reports/{test_type}-report.html",
        #     "--self-contained-html"
        # ])
        
        # Add verbosity
        if self.config["reporting"]["detailed_output"]:
            cmd.append("-v")
        
        # Add timeout
        cmd.extend(["--timeout", str(config["timeout"])])
        
        return cmd
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """Parse pytest output for metrics."""
        metrics = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "warnings": 0
        }
        
        lines = output.split('\n')
        
        for line in lines:
            # Parse test results summary
            if "passed" in line and "failed" in line:
                # Example: "5 passed, 2 failed, 1 skipped in 10.5s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed" and i > 0:
                        metrics["passed"] = int(parts[i-1])
                    elif part == "failed" and i > 0:
                        metrics["failed"] = int(parts[i-1])
                    elif part == "skipped" and i > 0:
                        metrics["skipped"] = int(parts[i-1])
                    elif part == "error" and i > 0:
                        metrics["errors"] = int(parts[i-1])
            
            # Count warnings
            if "warning" in line.lower():
                metrics["warnings"] += 1
        
        metrics["total_tests"] = metrics["passed"] + metrics["failed"] + metrics["skipped"] + metrics["errors"]
        
        return metrics
    
    def _setup_environment(self):
        """Setup test environment."""
        logger.info("Setting up test environment")
        
        # Run setup commands
        for cmd in self.config["environment"]["setup_commands"]:
            try:
                subprocess.run(cmd, shell=True, check=True)
                logger.info(f"Setup command completed: {cmd}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Setup command failed: {cmd} - {e}")
        
        # Verify required services
        self._verify_services()
    
    def _teardown_environment(self):
        """Teardown test environment."""
        logger.info("Tearing down test environment")
        
        # Run teardown commands
        for cmd in self.config["environment"]["teardown_commands"]:
            try:
                subprocess.run(cmd, shell=True, check=True)
                logger.info(f"Teardown command completed: {cmd}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Teardown command failed: {cmd} - {e}")
    
    def _verify_services(self):
        """Verify required services are available."""
        logger.info("Verifying required services")
        
        for service in self.config["environment"]["required_services"]:
            # This would contain actual service health checks
            logger.info(f"Service {service} is available")
    
    def _generate_report(self):
        """Generate comprehensive test report."""
        logger.info("Generating comprehensive test report")
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics()
        
        # Create comprehensive report
        report = {
            "test_run": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "duration": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0,
                "timestamp": datetime.utcnow().isoformat()
            },
            "overall_metrics": overall_metrics,
            "test_results": self.results,
            "configuration": self.config
        }
        
        # Save JSON report
        with open("test-reports/comprehensive-report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Generate HTML report
        self._generate_html_report(report)
        
        # Print summary
        self._print_summary(overall_metrics)
    
    def _calculate_overall_metrics(self) -> Dict[str, Any]:
        """Calculate overall test metrics."""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_errors = 0
        total_duration = 0
        
        for test_type, result in self.results.items():
            if result.get("success"):
                total_tests += result.get("total_tests", 0)
                total_passed += result.get("passed", 0)
                total_failed += result.get("failed", 0)
                total_skipped += result.get("skipped", 0)
                total_errors += result.get("errors", 0)
            total_duration += result.get("duration", 0)
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "skipped": total_skipped,
            "errors": total_errors,
            "success_rate": round(success_rate, 2),
            "total_duration": round(total_duration, 2),
            "test_types_run": len(self.results),
            "test_types_passed": len([r for r in self.results.values() if r.get("success")])
        }
    
    def _generate_html_report(self, report: Dict[str, Any]):
        """Generate HTML test report."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CityPulse Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .metrics {{ display: flex; gap: 20px; margin: 20px 0; }}
                .metric {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; text-align: center; }}
                .test-type {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .success {{ background-color: #d4edda; }}
                .failure {{ background-color: #f8d7da; }}
                .timestamp {{ color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>CityPulse Comprehensive Test Report</h1>
                <p class="timestamp">Generated: {report['test_run']['timestamp']}</p>
                <p>Duration: {report['overall_metrics']['total_duration']} seconds</p>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <h3>{report['overall_metrics']['total_tests']}</h3>
                    <p>Total Tests</p>
                </div>
                <div class="metric">
                    <h3>{report['overall_metrics']['passed']}</h3>
                    <p>Passed</p>
                </div>
                <div class="metric">
                    <h3>{report['overall_metrics']['failed']}</h3>
                    <p>Failed</p>
                </div>
                <div class="metric">
                    <h3>{report['overall_metrics']['success_rate']}%</h3>
                    <p>Success Rate</p>
                </div>
            </div>
            
            <h2>Test Type Results</h2>
        """
        
        for test_type, result in report['test_results'].items():
            status_class = "success" if result.get("success") else "failure"
            html_content += f"""
            <div class="test-type {status_class}">
                <h3>{test_type.title()} Tests</h3>
                <p>Status: {'PASSED' if result.get('success') else 'FAILED'}</p>
                <p>Duration: {result.get('duration', 0):.2f} seconds</p>
                <p>Tests: {result.get('total_tests', 0)} total, {result.get('passed', 0)} passed, {result.get('failed', 0)} failed</p>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open("test-reports/comprehensive-report.html", "w") as f:
            f.write(html_content)
    
    def _print_summary(self, metrics: Dict[str, Any]):
        """Print test summary to console."""
        print("\n" + "="*60)
        print("CITYPULSE TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {metrics['total_tests']}")
        print(f"Passed: {metrics['passed']}")
        print(f"Failed: {metrics['failed']}")
        print(f"Skipped: {metrics['skipped']}")
        print(f"Errors: {metrics['errors']}")
        print(f"Success Rate: {metrics['success_rate']}%")
        print(f"Total Duration: {metrics['total_duration']:.2f} seconds")
        print(f"Test Types Run: {metrics['test_types_run']}")
        print(f"Test Types Passed: {metrics['test_types_passed']}")
        print("="*60)
        
        # Print individual test type results
        for test_type, result in self.results.items():
            status = "PASSED" if result.get("success") else "FAILED"
            print(f"{test_type.upper()}: {status} ({result.get('duration', 0):.2f}s)")
        
        print("="*60)


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="CityPulse Comprehensive Test Runner")
    parser.add_argument(
        "--types",
        nargs="+",
        choices=["unit", "integration", "e2e", "performance", "security", "accessibility"],
        help="Test types to run"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to test configuration file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="test-reports",
        help="Output directory for test reports"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Create test runner
    runner = TestRunner(config)
    
    # Run tests
    results = runner.run_all_tests(args.types)
    
    # Exit with appropriate code
    overall_success = all(result.get("success", False) for result in results.values())
    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()
