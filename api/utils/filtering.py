"""
Filtering utilities for CityPulse API.

This module provides filtering support for list endpoints with
various filter types and operators.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from fastapi import Query
from pydantic import BaseModel, Field, validator


class FilterOperator(Enum):
    """Supported filter operators."""

    EQ = "eq"  # Equal
    NE = "ne"  # Not equal
    GT = "gt"  # Greater than
    GTE = "gte"  # Greater than or equal
    LT = "lt"  # Less than
    LTE = "lte"  # Less than or equal
    IN = "in"  # In list
    NOT_IN = "not_in"  # Not in list
    CONTAINS = "contains"  # String contains
    STARTS_WITH = "starts_with"  # String starts with
    ENDS_WITH = "ends_with"  # String ends with


class SortOrder(Enum):
    """Sort order options."""

    ASC = "asc"
    DESC = "desc"


class FilterParams(BaseModel):
    """Base filter parameters for events."""

    # Event-specific filters
    category: Optional[str] = Field(None, description="Filter by event category")
    status: Optional[str] = Field(None, description="Filter by event status")
    severity: Optional[str] = Field(None, description="Filter by event severity")
    source: Optional[str] = Field(None, description="Filter by event source")

    # Location filters
    latitude: Optional[float] = Field(
        None, description="Latitude for location-based filtering"
    )
    longitude: Optional[float] = Field(
        None, description="Longitude for location-based filtering"
    )
    radius: Optional[float] = Field(
        None, description="Radius in kilometers for location filtering"
    )
    ward: Optional[str] = Field(None, description="Filter by ward/district")

    # Time filters
    start_date: Optional[datetime] = Field(
        None, description="Filter events after this date"
    )
    end_date: Optional[datetime] = Field(
        None, description="Filter events before this date"
    )

    # Text search
    search: Optional[str] = Field(None, description="Search in title and description")

    # User filters
    user_id: Optional[str] = Field(None, description="Filter by user ID")

    # Sorting
    sort_by: Optional[str] = Field("created_at", description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.DESC, description="Sort order")

    @validator("radius")
    def validate_radius(cls, v, values):
        """Validate radius is provided with coordinates."""
        if v is not None:
            if values.get("latitude") is None or values.get("longitude") is None:
                raise ValueError("Latitude and longitude required when using radius")
            if v <= 0 or v > 1000:  # Max 1000km radius
                raise ValueError("Radius must be between 0 and 1000 kilometers")
        return v


def create_filter_params(
    category: Optional[str] = Query(None, description="Filter by event category"),
    status: Optional[str] = Query(None, description="Filter by event status"),
    severity: Optional[str] = Query(None, description="Filter by event severity"),
    source: Optional[str] = Query(None, description="Filter by event source"),
    latitude: Optional[float] = Query(
        None, description="Latitude for location filtering"
    ),
    longitude: Optional[float] = Query(
        None, description="Longitude for location filtering"
    ),
    radius: Optional[float] = Query(None, description="Radius in kilometers"),
    ward: Optional[str] = Query(None, description="Filter by ward/district"),
    start_date: Optional[datetime] = Query(
        None, description="Filter events after this date"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Filter events before this date"
    ),
    search: Optional[str] = Query(None, description="Search in title and description"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort order"),
) -> FilterParams:
    """FastAPI dependency for filter parameters."""
    return FilterParams(
        category=category,
        status=status,
        severity=severity,
        source=source,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        ward=ward,
        start_date=start_date,
        end_date=end_date,
        search=search,
        user_id=user_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )


def apply_filters(
    query_data: List[Dict[str, Any]], filters: FilterParams
) -> List[Dict[str, Any]]:
    """
    Apply filters to a list of data.

    Args:
        query_data: List of data to filter
        filters: Filter parameters

    Returns:
        Filtered list of data
    """
    filtered_data = query_data.copy()

    # Apply category filter
    if filters.category:
        filtered_data = [
            item
            for item in filtered_data
            if item.get("category", "").lower() == filters.category.lower()
        ]

    # Apply status filter
    if filters.status:
        filtered_data = [
            item
            for item in filtered_data
            if item.get("status", "").lower() == filters.status.lower()
        ]

    # Apply severity filter
    if filters.severity:
        filtered_data = [
            item
            for item in filtered_data
            if item.get("severity", "").lower() == filters.severity.lower()
        ]

    # Apply source filter
    if filters.source:
        filtered_data = [
            item
            for item in filtered_data
            if item.get("source", "").lower() == filters.source.lower()
        ]

    # Apply user filter
    if filters.user_id:
        filtered_data = [
            item for item in filtered_data if item.get("user_id") == filters.user_id
        ]

    # Apply text search
    if filters.search:
        search_term = filters.search.lower()
        filtered_data = [
            item
            for item in filtered_data
            if search_term in item.get("title", "").lower()
            or search_term in item.get("description", "").lower()
        ]

    # Apply date filters
    if filters.start_date:
        filtered_data = [
            item
            for item in filtered_data
            if item.get("created_at")
            and datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
            >= filters.start_date
        ]

    if filters.end_date:
        filtered_data = [
            item
            for item in filtered_data
            if item.get("created_at")
            and datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
            <= filters.end_date
        ]

    # Apply location filter (simplified - in production, use proper geospatial queries)
    if filters.latitude and filters.longitude and filters.radius:
        # This is a simplified distance calculation
        # In production, use proper geospatial libraries or database functions
        filtered_data = [
            item
            for item in filtered_data
            if _is_within_radius(
                item.get("location", {}),
                filters.latitude,
                filters.longitude,
                filters.radius,
            )
        ]

    # Apply sorting
    if filters.sort_by:
        reverse = filters.sort_order == SortOrder.DESC
        filtered_data.sort(key=lambda x: x.get(filters.sort_by, ""), reverse=reverse)

    return filtered_data


def _is_within_radius(
    location: Dict[str, Any], lat: float, lon: float, radius: float
) -> bool:
    """
    Check if location is within radius (simplified calculation).

    In production, use proper geospatial calculations or database functions.
    """
    if not location or "latitude" not in location or "longitude" not in location:
        return False

    # Simplified distance calculation (not accurate for large distances)
    lat_diff = abs(location["latitude"] - lat)
    lon_diff = abs(location["longitude"] - lon)

    # Very rough approximation - use proper geospatial libraries in production
    distance_km = ((lat_diff**2 + lon_diff**2) ** 0.5) * 111  # Rough km per degree

    return distance_km <= radius


def build_firestore_filters(filters: FilterParams) -> List[tuple]:
    """
    Build Firestore query filters from FilterParams.

    Returns:
        List of tuples for Firestore where clauses
    """
    firestore_filters = []

    if filters.category:
        firestore_filters.append(("category", "==", filters.category))

    if filters.status:
        firestore_filters.append(("status", "==", filters.status))

    if filters.severity:
        firestore_filters.append(("severity", "==", filters.severity))

    if filters.source:
        firestore_filters.append(("source", "==", filters.source))

    if filters.user_id:
        firestore_filters.append(("user_id", "==", filters.user_id))

    if filters.start_date:
        firestore_filters.append(("created_at", ">=", filters.start_date))

    if filters.end_date:
        firestore_filters.append(("created_at", "<=", filters.end_date))

    return firestore_filters
