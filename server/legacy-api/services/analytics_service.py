"""
Analytics service for CityPulse API.

This module provides business logic for analytics operations including
KPI calculations, trend analysis, and data aggregation using BigQuery.
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Add parent directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.responses import AnalyticsKPIResponse, AnalyticsTrendResponse

from shared_config import get_config, get_database_config
from shared_exceptions import (
    CityPulseException,
    DatabaseException,
    ErrorCode,
    ValidationException,
    handle_database_error,
    log_exception,
)
from shared_services import get_database_service

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service class for analytics operations."""

    def __init__(self):
        """Initialize the analytics service with unified database service."""
        self.config = get_config()
        self.db_config = get_database_config()
        self.db_service = get_database_service()

        # Legacy properties for backward compatibility
        self.dataset_id = self.db_config.bigquery_dataset
        self.events_table = f"{self.dataset_id}.events"
        self.feedback_table = f"{self.dataset_id}.feedback"

    async def get_kpis(self, user: Dict[str, Any]) -> AnalyticsKPIResponse:
        """
        Get key performance indicators.

        Args:
            user: Current user context

        Returns:
            KPI data
        """
        try:
            # Query BigQuery for KPI data using parameterized query
            query = """
            WITH event_stats AS (
                SELECT
                    COUNT(*) as total_reports,
                    COUNTIF(status = 'resolved') as resolved_reports,
                    COUNTIF(status = 'pending') as pending_reports,
                    COUNTIF(status = 'in_progress') as in_progress_reports,
                    COUNTIF(severity = 'critical') as critical_issues,
                    AVG(DATETIME_DIFF(updated_at, created_at, HOUR)) as avg_response_time_hours
                FROM `@events_table`
                WHERE created_at >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 30 DAY)
            ),
            feedback_stats AS (
                SELECT
                    AVG(CASE WHEN ai_accuracy_rating IS NOT NULL THEN ai_accuracy_rating ELSE 4.0 END) as user_satisfaction
                FROM `@feedback_table`
                WHERE created_at >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 30 DAY)
            )
            SELECT
                e.total_reports,
                e.resolved_reports,
                e.pending_reports,
                e.in_progress_reports,
                SAFE_DIVIDE(e.resolved_reports * 100.0, e.total_reports) as resolution_rate,
                COALESCE(e.avg_response_time_hours, 24.0) as avg_response_time_hours,
                e.critical_issues,
                COALESCE(f.user_satisfaction, 4.0) as user_satisfaction
            FROM event_stats e
            CROSS JOIN feedback_stats f
            """

            # Configure parameterized query
            from google.cloud import bigquery
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("events_table", "STRING", self.events_table),
                    bigquery.ScalarQueryParameter("feedback_table", "STRING", self.feedback_table),
                ]
            )

            query_job = self.bigquery_client.query(query, job_config=job_config)
            results = list(query_job)

            if results:
                row = results[0]
                return AnalyticsKPIResponse(
                    total_reports=int(row.total_reports or 0),
                    resolved_reports=int(row.resolved_reports or 0),
                    pending_reports=int(row.pending_reports or 0),
                    in_progress_reports=int(row.in_progress_reports or 0),
                    resolution_rate=float(row.resolution_rate or 0.0),
                    avg_response_time_hours=float(row.avg_response_time_hours or 24.0),
                    critical_issues=int(row.critical_issues or 0),
                    user_satisfaction=float(row.user_satisfaction or 4.0),
                    last_updated=datetime.utcnow(),
                )
            else:
                # Return default values if no data
                return AnalyticsKPIResponse(
                    total_reports=0,
                    resolved_reports=0,
                    pending_reports=0,
                    in_progress_reports=0,
                    resolution_rate=0.0,
                    avg_response_time_hours=24.0,
                    critical_issues=0,
                    user_satisfaction=4.0,
                    last_updated=datetime.utcnow(),
                )

        except Exception as e:
            logger.error(f"Error getting KPIs: {e}")
            # Return default values on error
            return AnalyticsKPIResponse(
                total_reports=0,
                resolved_reports=0,
                pending_reports=0,
                in_progress_reports=0,
                resolution_rate=0.0,
                avg_response_time_hours=24.0,
                critical_issues=0,
                user_satisfaction=4.0,
                last_updated=datetime.utcnow(),
            )

    async def get_trends(
        self,
        period: str,
        start_date: datetime,
        end_date: datetime,
        user: Dict[str, Any],
    ) -> AnalyticsTrendResponse:
        """
        Get trend analytics data.

        Args:
            period: Time period (daily, weekly, monthly)
            start_date: Start date for analysis
            end_date: End date for analysis
            user: Current user context

        Returns:
            Trend data
        """
        try:
            # Determine date truncation based on period
            if period == "daily":
                date_trunc = "DATE(created_at)"
                date_format = "%Y-%m-%d"
            elif period == "weekly":
                date_trunc = "DATE_TRUNC(DATE(created_at), WEEK)"
                date_format = "%Y-%m-%d"
            else:  # monthly
                date_trunc = "DATE_TRUNC(DATE(created_at), MONTH)"
                date_format = "%Y-%m-%d"

            # Use parameterized query to prevent SQL injection
            query = f"""
            SELECT
                {date_trunc} as date,
                COUNT(*) as total_reports,
                COUNTIF(status = 'resolved') as resolved_reports,
                AVG(DATETIME_DIFF(updated_at, created_at, HOUR)) as avg_response_time
            FROM `@events_table`
            WHERE created_at >= @start_date
                AND created_at <= @end_date
            GROUP BY date
            ORDER BY date
            """

            # Configure parameterized query
            from google.cloud import bigquery
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("events_table", "STRING", self.events_table),
                    bigquery.ScalarQueryParameter("start_date", "DATETIME", start_date),
                    bigquery.ScalarQueryParameter("end_date", "DATETIME", end_date),
                ]
            )

            query_job = self.bigquery_client.query(query, job_config=job_config)
            results = list(query_job)

            data_points = []
            for row in results:
                data_points.append(
                    {
                        "date": row.date.strftime(date_format),
                        "total_reports": int(row.total_reports),
                        "resolved_reports": int(row.resolved_reports or 0),
                        "avg_response_time": float(row.avg_response_time or 24.0),
                    }
                )

            return AnalyticsTrendResponse(period=period, data_points=data_points)

        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            # Return empty data on error
            return AnalyticsTrendResponse(period=period, data_points=[])

    async def get_public_summary(self) -> Dict[str, Any]:
        """
        Get public analytics summary with limited data.

        Returns:
            Public summary data
        """
        try:
            # Query for basic public statistics
            query = f"""
            SELECT 
                COUNT(*) as total_reports,
                COUNTIF(status = 'resolved') as resolved_reports,
                COUNTIF(created_at >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 24 HOUR)) as reports_last_24h
            FROM `{self.events_table}`
            WHERE created_at >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 30 DAY)
            """

            query_job = self.bigquery_client.query(query)
            results = list(query_job)

            if results:
                row = results[0]
                return {
                    "total_reports_30_days": int(row.total_reports or 0),
                    "resolved_reports_30_days": int(row.resolved_reports or 0),
                    "reports_last_24h": int(row.reports_last_24h or 0),
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                }
            else:
                return {
                    "total_reports_30_days": 0,
                    "resolved_reports_30_days": 0,
                    "reports_last_24h": 0,
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                }

        except Exception as e:
            logger.error(f"Error getting public summary: {e}")
            return {
                "total_reports_30_days": 0,
                "resolved_reports_30_days": 0,
                "reports_last_24h": 0,
                "last_updated": datetime.utcnow().isoformat() + "Z",
            }

    async def get_events_by_category(
        self, start_date: datetime, end_date: datetime, user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get event distribution by category.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            user: Current user context

        Returns:
            Category distribution data
        """
        try:
            query = f"""
            SELECT 
                category,
                COUNT(*) as count,
                COUNTIF(status = 'resolved') as resolved_count
            FROM `{self.events_table}`
            WHERE created_at >= DATETIME('{start_date.isoformat()}')
                AND created_at <= DATETIME('{end_date.isoformat()}')
            GROUP BY category
            ORDER BY count DESC
            """

            query_job = self.bigquery_client.query(query)
            results = list(query_job)

            categories = []
            for row in results:
                categories.append(
                    {
                        "category": row.category,
                        "count": int(row.count),
                        "resolved_count": int(row.resolved_count or 0),
                        "resolution_rate": (
                            float((row.resolved_count or 0) / row.count * 100)
                            if row.count > 0
                            else 0.0
                        ),
                    }
                )

            return {
                "categories": categories,
                "period": {
                    "start_date": start_date.isoformat() + "Z",
                    "end_date": end_date.isoformat() + "Z",
                },
            }

        except Exception as e:
            logger.error(f"Error getting events by category: {e}")
            return {
                "categories": [],
                "period": {
                    "start_date": start_date.isoformat() + "Z",
                    "end_date": end_date.isoformat() + "Z",
                },
            }

    async def get_events_by_location(
        self, start_date: datetime, end_date: datetime, user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get event distribution by location.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            user: Current user context

        Returns:
            Location distribution data
        """
        try:
            # Note: This is a simplified query. In production, you'd use proper geospatial functions
            # Use parameterized query to prevent SQL injection
            query = """
            SELECT
                JSON_EXTRACT_SCALAR(metadata, '$.ward') as ward,
                COUNT(*) as count,
                COUNTIF(status = 'resolved') as resolved_count
            FROM `@events_table`
            WHERE created_at >= @start_date
                AND created_at <= @end_date
                AND JSON_EXTRACT_SCALAR(metadata, '$.ward') IS NOT NULL
            GROUP BY ward
            ORDER BY count DESC
            LIMIT 20
            """

            # Configure parameterized query
            from google.cloud import bigquery
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("events_table", "STRING", self.events_table),
                    bigquery.ScalarQueryParameter("start_date", "DATETIME", start_date),
                    bigquery.ScalarQueryParameter("end_date", "DATETIME", end_date),
                ]
            )

            query_job = self.bigquery_client.query(query, job_config=job_config)
            results = list(query_job)

            locations = []
            for row in results:
                if row.ward:
                    locations.append(
                        {
                            "ward": row.ward,
                            "count": int(row.count),
                            "resolved_count": int(row.resolved_count or 0),
                            "resolution_rate": (
                                float((row.resolved_count or 0) / row.count * 100)
                                if row.count > 0
                                else 0.0
                            ),
                        }
                    )

            return {
                "locations": locations,
                "period": {
                    "start_date": start_date.isoformat() + "Z",
                    "end_date": end_date.isoformat() + "Z",
                },
            }

        except Exception as e:
            logger.error(f"Error getting events by location: {e}")
            return {
                "locations": [],
                "period": {
                    "start_date": start_date.isoformat() + "Z",
                    "end_date": end_date.isoformat() + "Z",
                },
            }

    async def get_performance_metrics(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed performance metrics.

        Args:
            user: Current user context

        Returns:
            Performance metrics data
        """
        try:
            # This would include more detailed metrics for admin users
            # Use parameterized query to prevent SQL injection
            query = """
            SELECT
                COUNT(*) as total_events,
                AVG(DATETIME_DIFF(updated_at, created_at, MINUTE)) as avg_processing_time_minutes,
                COUNTIF(ai_summary IS NOT NULL) as ai_processed_events,
                COUNT(DISTINCT user_id) as active_users,
                COUNT(DISTINCT DATE(created_at)) as active_days
            FROM `@events_table`
            WHERE created_at >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 30 DAY)
            """

            # Configure parameterized query
            from google.cloud import bigquery
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("events_table", "STRING", self.events_table),
                ]
            )

            query_job = self.bigquery_client.query(query, job_config=job_config)
            results = list(query_job)

            if results:
                row = results[0]
                return {
                    "total_events": int(row.total_events or 0),
                    "avg_processing_time_minutes": float(
                        row.avg_processing_time_minutes or 0
                    ),
                    "ai_processed_events": int(row.ai_processed_events or 0),
                    "ai_processing_rate": float(
                        (row.ai_processed_events or 0) / (row.total_events or 1) * 100
                    ),
                    "active_users": int(row.active_users or 0),
                    "active_days": int(row.active_days or 0),
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                }
            else:
                return {
                    "total_events": 0,
                    "avg_processing_time_minutes": 0.0,
                    "ai_processed_events": 0,
                    "ai_processing_rate": 0.0,
                    "active_users": 0,
                    "active_days": 0,
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                }

        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                "total_events": 0,
                "avg_processing_time_minutes": 0.0,
                "ai_processed_events": 0,
                "ai_processing_rate": 0.0,
                "active_users": 0,
                "active_days": 0,
                "last_updated": datetime.utcnow().isoformat() + "Z",
            }
