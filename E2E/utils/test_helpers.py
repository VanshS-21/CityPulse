"""
Common test utilities and helper functions for CityPulse E2E tests.

This module provides reusable utilities for test setup, validation,
and common operations across different test modules.
"""

import time
import json
import logging
import subprocess
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class TestTimer:
    """Context manager for timing test operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Starting {self.operation_name}...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if exc_type is None:
            logger.info(f"Completed {self.operation_name} in {duration:.2f} seconds")
        else:
            logger.error(f"Failed {self.operation_name} after {duration:.2f} seconds")
    
    @property
    def duration(self) -> float:
        """Get the duration of the timed operation."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


def retry_with_backoff(
    func: Callable,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Any:
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Function to retry
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay between attempts
        backoff_factor: Factor to multiply delay by each attempt
        exceptions: Tuple of exceptions to catch and retry on
        
    Returns:
        Result of the function call
        
    Raises:
        Last exception if all attempts fail
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_attempts - 1:
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay:.1f} seconds..."
                )
                time.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(f"All {max_attempts} attempts failed")
    
    raise last_exception


def wait_for_condition(
    condition_func: Callable[[], bool],
    timeout: int = 300,
    check_interval: int = 10,
    description: str = "condition"
) -> bool:
    """
    Wait for a condition to become true.
    
    Args:
        condition_func: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        description: Description of what we're waiting for
        
    Returns:
        True if condition was met, False if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            if condition_func():
                logger.info(f"Condition met: {description}")
                return True
        except Exception as e:
            logger.warning(f"Error checking condition '{description}': {e}")
        
        time.sleep(check_interval)
    
    logger.warning(f"Timeout waiting for condition: {description}")
    return False


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, str]) -> List[str]:
    """
    Validate data against a simple schema.
    
    Args:
        data: Data to validate
        schema: Schema dictionary with field_name -> expected_type
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    for field_name, expected_type in schema.items():
        if field_name not in data:
            errors.append(f"Missing required field: {field_name}")
            continue
        
        value = data[field_name]
        
        # Type checking
        if expected_type == "string" and not isinstance(value, str):
            errors.append(f"Field {field_name} should be string, got {type(value).__name__}")
        elif expected_type == "integer" and not isinstance(value, int):
            errors.append(f"Field {field_name} should be integer, got {type(value).__name__}")
        elif expected_type == "float" and not isinstance(value, (int, float)):
            errors.append(f"Field {field_name} should be float, got {type(value).__name__}")
        elif expected_type == "boolean" and not isinstance(value, bool):
            errors.append(f"Field {field_name} should be boolean, got {type(value).__name__}")
        elif expected_type == "array" and not isinstance(value, list):
            errors.append(f"Field {field_name} should be array, got {type(value).__name__}")
        elif expected_type == "object" and not isinstance(value, dict):
            errors.append(f"Field {field_name} should be object, got {type(value).__name__}")
        elif expected_type == "timestamp":
            # Validate timestamp format
            if isinstance(value, str):
                try:
                    datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    errors.append(f"Field {field_name} is not a valid ISO timestamp")
            else:
                errors.append(f"Field {field_name} should be timestamp string, got {type(value).__name__}")
    
    return errors


def run_gcloud_command(command: List[str], timeout: int = 300) -> Dict[str, Any]:
    """
    Run a gcloud command and return the result.
    
    Args:
        command: List of command parts
        timeout: Command timeout in seconds
        
    Returns:
        Dictionary with 'success', 'stdout', 'stderr', 'returncode'
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }


def get_dataflow_job_status(project_id: str, region: str, job_id: str) -> Optional[str]:
    """
    Get the status of a Dataflow job.
    
    Args:
        project_id: GCP project ID
        region: GCP region
        job_id: Dataflow job ID
        
    Returns:
        Job status string or None if error
    """
    command = [
        "gcloud", "dataflow", "jobs", "describe", job_id,
        "--project", project_id,
        "--region", region,
        "--format", "value(currentState)"
    ]
    
    result = run_gcloud_command(command)
    
    if result["success"]:
        return result["stdout"].strip()
    else:
        logger.error(f"Error getting job status: {result['stderr']}")
        return None


def format_test_results(results: Dict[str, Any]) -> str:
    """
    Format test results for logging.
    
    Args:
        results: Dictionary of test results
        
    Returns:
        Formatted string
    """
    lines = ["Test Results:"]
    lines.append("=" * 50)
    
    for test_name, result in results.items():
        status = "PASS" if result.get("success", False) else "FAIL"
        duration = result.get("duration", 0)
        lines.append(f"{test_name:<30} {status:<6} ({duration:.2f}s)")
        
        if not result.get("success", False) and "error" in result:
            lines.append(f"  Error: {result['error']}")
    
    lines.append("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r.get("success", False))
    lines.append(f"Total: {total_tests}, Passed: {passed_tests}, Failed: {total_tests - passed_tests}")
    
    return "\n".join(lines)


@contextmanager
def test_resource_cleanup(*helpers):
    """
    Context manager for automatic cleanup of test resources.
    
    Args:
        *helpers: Helper objects with cleanup() methods
    """
    try:
        yield
    finally:
        for helper in helpers:
            try:
                if hasattr(helper, 'cleanup'):
                    helper.cleanup()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")


def create_test_event_with_timestamp(base_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a test event with current timestamp.
    
    Args:
        base_event: Base event data
        
    Returns:
        Event with updated timestamp
    """
    event = base_event.copy()
    current_time = datetime.now(timezone.utc).isoformat()
    
    # Update timestamp fields
    timestamp_fields = ["timestamp", "created_at", "updated_at", "start_time"]
    for field in timestamp_fields:
        if field in event:
            event[field] = current_time
    
    return event


def compare_data_structures(expected: Any, actual: Any, path: str = "") -> List[str]:
    """
    Compare two data structures and return differences.
    
    Args:
        expected: Expected data structure
        actual: Actual data structure
        path: Current path in the structure (for error reporting)
        
    Returns:
        List of difference descriptions
    """
    differences = []
    
    if type(expected) != type(actual):
        differences.append(f"Type mismatch at {path}: expected {type(expected).__name__}, got {type(actual).__name__}")
        return differences
    
    if isinstance(expected, dict):
        for key in expected:
            new_path = f"{path}.{key}" if path else key
            if key not in actual:
                differences.append(f"Missing key at {new_path}")
            else:
                differences.extend(compare_data_structures(expected[key], actual[key], new_path))
        
        for key in actual:
            if key not in expected:
                new_path = f"{path}.{key}" if path else key
                differences.append(f"Unexpected key at {new_path}")
    
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            differences.append(f"Length mismatch at {path}: expected {len(expected)}, got {len(actual)}")
        else:
            for i, (exp_item, act_item) in enumerate(zip(expected, actual)):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                differences.extend(compare_data_structures(exp_item, act_item, new_path))
    
    elif expected != actual:
        differences.append(f"Value mismatch at {path}: expected {expected}, got {actual}")
    
    return differences
