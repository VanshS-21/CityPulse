"""
Analytics API router for CityPulse.

This module provides endpoints for retrieving analytics data and KPIs
with proper authentication and authorization.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from auth import get_current_user, get_optional_user, require_authority
from auth.permissions import Permission, check_permission
from fastapi import APIRouter, Depends, HTTPException, Query, status
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared_exceptions import COMMON_ERROR_RESPONSES
from models.responses import AnalyticsKPIResponse, AnalyticsTrendResponse
from services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize analytics service
analytics_service = AnalyticsService()


@router.get(
    "/kpis",
    response_model=AnalyticsKPIResponse,
    summary="Get KPIs",
    description="Retrieve key performance indicators",
    responses=COMMON_ERROR_RESPONSES,
)
async def get_kpis(
    current_user: Dict[str, Any] = Depends(require_authority),
) -> AnalyticsKPIResponse:
    """
    Get key performance indicators.

    - **Authentication required**: Must be logged in
    - **Permissions**: Authority or admin access required
    """
    try:
        # Check permissions
        if not check_permission(current_user, Permission.READ_ANALYTICS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access analytics",
            )

        # Get KPIs from service
        kpis = await analytics_service.get_kpis(user=current_user)

        return kpis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving KPIs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KPIs",
        )


@router.get(
    "/trends",
    response_model=AnalyticsTrendResponse,
    summary="Get Trends",
    description="Retrieve trend analytics data",
    responses=COMMON_ERROR_RESPONSES,
)
async def get_trends(
    period: str = Query("daily", description="Time period: daily, weekly, monthly"),
    start_date: Optional[datetime] = Query(
        None, description="Start date for trend analysis"
    ),
    end_date: Optional[datetime] = Query(
        None, description="End date for trend analysis"
    ),
    current_user: Dict[str, Any] = Depends(require_authority),
) -> AnalyticsTrendResponse:
    """
    Get trend analytics data.

    - **Authentication required**: Must be logged in
    - **Permissions**: Authority or admin access required
    - **Parameters**: Period (daily/weekly/monthly), date range
    """
    try:
        # Check permissions
        if not check_permission(current_user, Permission.READ_ANALYTICS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access analytics",
            )

        # Validate period
        if period not in ["daily", "weekly", "monthly"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid period. Must be 'daily', 'weekly', or 'monthly'",
            )

        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()

        if not start_date:
            if period == "daily":
                start_date = end_date - timedelta(days=30)
            elif period == "weekly":
                start_date = end_date - timedelta(weeks=12)
            else:  # monthly
                start_date = end_date - timedelta(days=365)

        # Get trends from service
        trends = await analytics_service.get_trends(
            period=period, start_date=start_date, end_date=end_date, user=current_user
        )

        return trends

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trends",
        )


@router.get(
    "/public/summary",
    response_model=Dict[str, Any],
    summary="Get Public Summary",
    description="Get public analytics summary (limited data)",
    responses=COMMON_ERROR_RESPONSES,
)
async def get_public_summary(
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
) -> Dict[str, Any]:
    """
    Get public analytics summary.

    - **Public access**: Available with API key
    - **Limited data**: Only basic statistics for public consumption
    """
    try:
        # Get public summary from service
        summary = await analytics_service.get_public_summary()

        return summary

    except Exception as e:
        logger.error(f"Error retrieving public summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve public summary",
        )


@router.get(
    "/events/by-category",
    response_model=Dict[str, Any],
    summary="Get Events by Category",
    description="Get event distribution by category",
    responses=COMMON_ERROR_RESPONSES,
)
async def get_events_by_category(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    current_user: Dict[str, Any] = Depends(require_authority),
) -> Dict[str, Any]:
    """
    Get event distribution by category.

    - **Authentication required**: Must be logged in
    - **Permissions**: Authority or admin access required
    """
    try:
        # Check permissions
        if not check_permission(current_user, Permission.READ_ANALYTICS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access analytics",
            )

        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()

        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Get category distribution from service
        category_data = await analytics_service.get_events_by_category(
            start_date=start_date, end_date=end_date, user=current_user
        )

        return category_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving events by category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve category analytics",
        )


@router.get(
    "/events/by-location",
    response_model=Dict[str, Any],
    summary="Get Events by Location",
    description="Get event distribution by location/ward",
    responses=COMMON_ERROR_RESPONSES,
)
async def get_events_by_location(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    current_user: Dict[str, Any] = Depends(require_authority),
) -> Dict[str, Any]:
    """
    Get event distribution by location.

    - **Authentication required**: Must be logged in
    - **Permissions**: Authority or admin access required
    """
    try:
        # Check permissions
        if not check_permission(current_user, Permission.READ_ANALYTICS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access analytics",
            )

        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()

        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Get location distribution from service
        location_data = await analytics_service.get_events_by_location(
            start_date=start_date, end_date=end_date, user=current_user
        )

        return location_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving events by location: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve location analytics",
        )


@router.get(
    "/performance",
    response_model=Dict[str, Any],
    summary="Get Performance Metrics",
    description="Get detailed performance metrics (admin only)",
    responses=COMMON_ERROR_RESPONSES,
)
async def get_performance_metrics(
    current_user: Dict[str, Any] = Depends(require_authority),
) -> Dict[str, Any]:
    """
    Get detailed performance metrics.

    - **Authentication required**: Must be logged in
    - **Permissions**: Admin access required for detailed metrics
    """
    try:
        # Check permissions for detailed analytics
        if not check_permission(current_user, Permission.READ_DETAILED_ANALYTICS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access detailed analytics",
            )

        # Get performance metrics from service
        performance = await analytics_service.get_performance_metrics(user=current_user)

        return performance

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance metrics",
        )
