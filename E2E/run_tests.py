#!/usr/bin/env python3
"""
Test runner script for CityPulse E2E test suite.

This script provides convenient ways to run different test categories
and handles environment setup and validation.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from utils.environment_helpers import validate_required_environment_variables


def setup_environment():
    """Set up the test environment."""
    # Add the project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Validate required environment variables using consolidated helper
    validate_required_environment_variables()


def run_pytest(test_args):
    """Run pytest with the given arguments."""
    cmd = ["python", "-m", "pytest"] + test_args
    
    print(f"Running: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="CityPulse E2E Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --smoke                    # Run smoke tests
  python run_tests.py --pubsub                   # Run Pub/Sub tests
  python run_tests.py --bigquery                 # Run BigQuery tests
  python run_tests.py --dataflow                 # Run Dataflow tests
  python run_tests.py --e2e                      # Run end-to-end tests
  python run_tests.py --all                      # Run all tests
  python run_tests.py --performance              # Run performance tests
  python run_tests.py tests/test_pubsub_integration.py  # Run specific file
        """
    )
    
    # Test category options
    parser.add_argument("--smoke", action="store_true", 
                       help="Run smoke tests for quick validation")
    parser.add_argument("--pubsub", action="store_true",
                       help="Run Pub/Sub integration tests")
    parser.add_argument("--bigquery", action="store_true",
                       help="Run BigQuery table tests")
    parser.add_argument("--dataflow", action="store_true",
                       help="Run Dataflow pipeline tests")
    parser.add_argument("--e2e", action="store_true",
                       help="Run end-to-end workflow tests")
    parser.add_argument("--performance", action="store_true",
                       help="Run performance tests")
    parser.add_argument("--all", action="store_true",
                       help="Run all tests")
    
    # Output options
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Quiet output")
    parser.add_argument("--no-cleanup", action="store_true",
                       help="Skip resource cleanup (for debugging)")
    
    # Additional pytest arguments
    parser.add_argument("pytest_args", nargs="*",
                       help="Additional arguments to pass to pytest")
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Build pytest arguments
    pytest_args = []
    
    # Add verbosity
    if args.verbose:
        pytest_args.extend(["-v", "-s"])
    elif args.quiet:
        pytest_args.append("-q")
    
    # Add test selection based on markers
    if args.smoke:
        pytest_args.extend(["-m", "smoke"])
    elif args.pubsub:
        pytest_args.extend(["-m", "pubsub"])
    elif args.bigquery:
        pytest_args.extend(["-m", "bigquery"])
    elif args.dataflow:
        pytest_args.extend(["-m", "dataflow"])
    elif args.e2e:
        pytest_args.extend(["-m", "e2e"])
    elif args.performance:
        pytest_args.extend(["-m", "performance"])
    elif args.all:
        pass  # Run all tests
    elif args.pytest_args:
        # Use provided pytest arguments
        pytest_args.extend(args.pytest_args)
    else:
        # Default: run all tests
        print("No specific test category selected. Running all tests.")
        print("Use --help to see available options.")
    
    # Add any additional pytest arguments
    if args.pytest_args and not (args.smoke or args.pubsub or args.bigquery or args.dataflow or args.e2e or args.performance):
        pytest_args.extend(args.pytest_args)
    
    # Run the tests
    print(f"🚀 Starting CityPulse E2E Tests")
    print(f"Project: {os.getenv('GCP_PROJECT_ID')}")
    print(f"Region: {os.getenv('GCP_REGION')}")
    print(f"Temp Bucket: {os.getenv('GCP_TEMP_BUCKET')}")
    print()
    
    exit_code = run_pytest(pytest_args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
