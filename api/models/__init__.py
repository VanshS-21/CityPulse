"""API models for CityPulse REST API.

Note: Error models have been moved to shared_exceptions.py for consistency
across the entire CityPulse platform.
"""

import os

# Import shared error models for backward compatibility
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared_exceptions import ErrorResponse, ValidationException

__all__ = [
    "ErrorResponse",
    "ValidationException",
]
