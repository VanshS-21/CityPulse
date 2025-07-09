"""
Validation utilities for CityPulse API.

This module provides additional validation functions and custom validators
beyond what Pydantic provides out of the box.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import validator


class ValidationError(Exception):
    """Custom validation error with detailed field information."""

    def __init__(self, errors: List[Dict[str, Any]]):
        self.errors = errors
        super().__init__("Validation failed")


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format (international format)."""
    pattern = r"^\+?[1-9]\d{1,14}$"
    return re.match(pattern, phone.replace(" ", "").replace("-", "")) is not None


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate geographic coordinates."""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID format."""
    pattern = (
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )
    return re.match(pattern, uuid_string.lower()) is not None


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r"^https?:\/\/(?:[-\w.])+(?:\:[0-9]+)?(?:\/(?:[\w\/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$"
    return re.match(pattern, url) is not None


def validate_event_category(category: str) -> bool:
    """Validate event category against allowed values."""
    allowed_categories = [
        "infrastructure",
        "safety",
        "environment",
        "traffic",
        "utilities",
        "public_services",
        "health",
        "education",
        "other",
    ]
    return category.lower() in allowed_categories


def validate_event_severity(severity: str) -> bool:
    """Validate event severity against allowed values."""
    allowed_severities = ["low", "medium", "high", "critical"]
    return severity.lower() in allowed_severities


def validate_event_status(status: str) -> bool:
    """Validate event status against allowed values."""
    allowed_statuses = ["pending", "in_progress", "resolved", "closed", "cancelled"]
    return status.lower() in allowed_statuses


def validate_user_role(role: str) -> bool:
    """Validate user role against allowed values."""
    allowed_roles = ["citizen", "authority", "admin"]
    return role.lower() in allowed_roles


def validate_feedback_type(feedback_type: str) -> bool:
    """Validate feedback type against allowed values."""
    allowed_types = ["bug", "feature_request", "general", "ai_feedback"]
    return feedback_type.lower() in allowed_types


def validate_date_range(
    start_date: Optional[datetime], end_date: Optional[datetime]
) -> bool:
    """Validate that end_date is after start_date."""
    if start_date and end_date:
        return end_date > start_date
    return True


def validate_pagination_params(page: int, limit: int) -> List[str]:
    """Validate pagination parameters and return list of errors."""
    errors = []

    if page < 1:
        errors.append("Page must be greater than 0")

    if limit < 1:
        errors.append("Limit must be greater than 0")

    if limit > 100:
        errors.append("Limit cannot exceed 100")

    return errors


def validate_location_data(location: Dict[str, Any]) -> List[str]:
    """Validate location data structure and values."""
    errors = []

    if not isinstance(location, dict):
        errors.append("Location must be an object")
        return errors

    latitude = location.get("latitude")
    longitude = location.get("longitude")

    if latitude is None:
        errors.append("Location latitude is required")
    elif not isinstance(latitude, (int, float)):
        errors.append("Location latitude must be a number")
    elif not -90 <= latitude <= 90:
        errors.append("Location latitude must be between -90 and 90")

    if longitude is None:
        errors.append("Location longitude is required")
    elif not isinstance(longitude, (int, float)):
        errors.append("Location longitude must be a number")
    elif not -180 <= longitude <= 180:
        errors.append("Location longitude must be between -180 and 180")

    # Optional address validation
    address = location.get("address")
    if address and not isinstance(address, str):
        errors.append("Location address must be a string")

    return errors


def validate_media_urls(urls: List[str]) -> List[str]:
    """Validate media URLs."""
    errors = []

    if not isinstance(urls, list):
        errors.append("Media URLs must be a list")
        return errors

    for i, url in enumerate(urls):
        if not isinstance(url, str):
            errors.append(f"Media URL at index {i} must be a string")
        elif not validate_url(url):
            errors.append(f"Invalid URL format at index {i}")

    return errors


def sanitize_text_input(text: str, max_length: int = 1000) -> str:
    """Sanitize text input by removing potentially harmful content."""
    if not text:
        return ""

    # Remove HTML tags (basic sanitization)
    text = re.sub(r"<[^>]+>", "", text)

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length].rstrip()

    return text


def validate_search_query(query: str) -> List[str]:
    """Validate search query parameters."""
    errors = []

    if not query:
        return errors

    if len(query) < 2:
        errors.append("Search query must be at least 2 characters long")

    if len(query) > 100:
        errors.append("Search query cannot exceed 100 characters")

    # Check for potentially harmful patterns
    harmful_patterns = [
        r"<script",
        r"javascript:",
        r"on\w+\s*=",
    ]

    for pattern in harmful_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            errors.append("Search query contains invalid characters")
            break

    return errors
