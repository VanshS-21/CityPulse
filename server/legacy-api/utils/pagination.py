"""
Pagination utilities for CityPulse API.

This module provides pagination support for list endpoints with
cursor-based and offset-based pagination options.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field, validator

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Parameters for pagination."""

    page: int = Field(1, ge=1, description="Page number (1-based)")
    limit: int = Field(20, ge=1, le=100, description="Number of items per page")
    cursor: Optional[str] = Field(
        None, description="Cursor for cursor-based pagination"
    )

    @validator("limit")
    def validate_limit(cls, v):
        """Ensure limit is within reasonable bounds."""
        if v > 100:
            raise ValueError("Limit cannot exceed 100")
        return v


class PaginationMeta(BaseModel):
    """Metadata for paginated responses."""

    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total_items: Optional[int] = Field(None, description="Total number of items")
    total_pages: Optional[int] = Field(None, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more items")
    has_previous: bool = Field(..., description="Whether there are previous items")
    next_cursor: Optional[str] = Field(None, description="Cursor for next page")
    previous_cursor: Optional[str] = Field(None, description="Cursor for previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""

    data: List[T] = Field(..., description="List of items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {"id": "1", "title": "Example Event"},
                    {"id": "2", "title": "Another Event"},
                ],
                "meta": {
                    "page": 1,
                    "limit": 20,
                    "total_items": 150,
                    "total_pages": 8,
                    "has_next": True,
                    "has_previous": False,
                    "next_cursor": "eyJpZCI6IjIifQ==",
                    "previous_cursor": None,
                },
            }
        }


def create_pagination_params(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    cursor: Optional[str] = Query(
        None, description="Cursor for cursor-based pagination"
    ),
) -> PaginationParams:
    """FastAPI dependency for pagination parameters."""
    return PaginationParams(page=page, limit=limit, cursor=cursor)


def paginate_query(
    items: List[T], pagination: PaginationParams, total_count: Optional[int] = None
) -> PaginatedResponse[T]:
    """
    Apply pagination to a list of items.

    Args:
        items: List of items to paginate
        pagination: Pagination parameters
        total_count: Total count of items (if known)

    Returns:
        Paginated response with metadata
    """
    # Calculate pagination metadata
    offset = (pagination.page - 1) * pagination.limit

    # Get items for current page
    paginated_items = items[offset : offset + pagination.limit]

    # Calculate metadata
    has_next = len(items) > offset + pagination.limit
    has_previous = pagination.page > 1

    total_pages = None
    if total_count is not None:
        total_pages = (total_count + pagination.limit - 1) // pagination.limit

    meta = PaginationMeta(
        page=pagination.page,
        limit=pagination.limit,
        total_items=total_count,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
        next_cursor=None,  # Implement cursor logic if needed
        previous_cursor=None,
    )

    return PaginatedResponse(data=paginated_items, meta=meta)


def paginate_firestore_query(
    query_results: List[Dict[str, Any]],
    pagination: PaginationParams,
    total_count: Optional[int] = None,
) -> PaginatedResponse[Dict[str, Any]]:
    """
    Paginate Firestore query results.

    Args:
        query_results: Results from Firestore query
        pagination: Pagination parameters
        total_count: Total count from Firestore

    Returns:
        Paginated response
    """
    return paginate_query(query_results, pagination, total_count)


def paginate_bigquery_results(
    query_results: List[Dict[str, Any]],
    pagination: PaginationParams,
    total_count: Optional[int] = None,
) -> PaginatedResponse[Dict[str, Any]]:
    """
    Paginate BigQuery results.

    Args:
        query_results: Results from BigQuery
        pagination: Pagination parameters
        total_count: Total count from BigQuery

    Returns:
        Paginated response
    """
    return paginate_query(query_results, pagination, total_count)
