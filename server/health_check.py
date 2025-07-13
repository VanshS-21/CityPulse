"""
Comprehensive health check system for CityPulse API
Provides detailed health status for all system components
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

from google.cloud import firestore, bigquery, pubsub_v1
from google.cloud.exceptions import GoogleCloudError

from shared_config import get_config
from shared_services import get_database_service

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status for a single component"""
    name: str
    status: HealthStatus
    response_time_ms: float
    last_check: datetime
    details: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class SystemHealth:
    """Overall system health status"""
    status: HealthStatus
    timestamp: datetime
    uptime_seconds: float
    components: List[ComponentHealth]
    summary: Dict[str, Any]


class HealthChecker:
    """Comprehensive health checker for all system components"""
    
    def __init__(self):
        self.config = get_config()
        self.start_time = time.time()
        self.last_full_check = None
        self.cached_health = None
        self.cache_ttl = 30  # Cache health status for 30 seconds
        
    async def check_system_health(self, include_detailed: bool = False) -> SystemHealth:
        """
        Check overall system health
        
        Args:
            include_detailed: Include detailed component checks
            
        Returns:
            SystemHealth object with overall status
        """
        # Use cached result if available and fresh
        if (self.cached_health and 
            self.last_full_check and 
            time.time() - self.last_full_check < self.cache_ttl):
            return self.cached_health
        
        start_time = time.time()
        components = []
        
        # Check all components
        if include_detailed:
            components.extend(await self._check_all_components())
        else:
            components.extend(await self._check_critical_components())
        
        # Determine overall status
        overall_status = self._determine_overall_status(components)
        
        # Calculate uptime
        uptime = time.time() - self.start_time
        
        # Create summary
        summary = self._create_summary(components, time.time() - start_time)
        
        health = SystemHealth(
            status=overall_status,
            timestamp=datetime.utcnow(),
            uptime_seconds=uptime,
            components=components,
            summary=summary
        )
        
        # Cache the result
        self.cached_health = health
        self.last_full_check = time.time()
        
        return health
    
    async def _check_all_components(self) -> List[ComponentHealth]:
        """Check all system components"""
        checks = [
            self._check_database(),
            self._check_firestore(),
            self._check_bigquery(),
            self._check_pubsub(),
            self._check_storage(),
            self._check_memory(),
            self._check_disk_space(),
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        components = []
        for result in results:
            if isinstance(result, ComponentHealth):
                components.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Health check failed: {result}")
                components.append(ComponentHealth(
                    name="unknown",
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=0,
                    last_check=datetime.utcnow(),
                    details={},
                    error=str(result)
                ))
        
        return components
    
    async def _check_critical_components(self) -> List[ComponentHealth]:
        """Check only critical components for faster response"""
        checks = [
            self._check_database(),
            self._check_firestore(),
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        components = []
        for result in results:
            if isinstance(result, ComponentHealth):
                components.append(result)
        
        return components
    
    async def _check_database(self) -> ComponentHealth:
        """Check database connectivity and performance"""
        start_time = time.time()
        
        try:
            db_service = get_database_service()
            
            # Test basic connectivity
            test_collection = "health_check"
            test_doc = {"timestamp": datetime.utcnow().isoformat(), "test": True}
            
            # Add and immediately delete a test document
            doc_id = db_service.add_document(test_collection, test_doc)
            db_service.delete_document(test_collection, doc_id)
            
            response_time = (time.time() - start_time) * 1000
            
            # Get connection stats if available
            stats = {}
            if hasattr(db_service, 'get_connection_stats'):
                stats = db_service.get_connection_stats()
            
            status = HealthStatus.HEALTHY
            if response_time > 1000:  # > 1 second
                status = HealthStatus.DEGRADED
            elif response_time > 5000:  # > 5 seconds
                status = HealthStatus.UNHEALTHY
            
            return ComponentHealth(
                name="database",
                status=status,
                response_time_ms=response_time,
                last_check=datetime.utcnow(),
                details={
                    "connection_stats": stats,
                    "test_operation": "add_delete_document"
                }
            )
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow(),
                details={},
                error=str(e)
            )
    
    async def _check_firestore(self) -> ComponentHealth:
        """Check Firestore connectivity"""
        start_time = time.time()
        
        try:
            client = firestore.Client(project=self.config.project_id)
            
            # Test read operation
            collections = list(client.collections())
            
            response_time = (time.time() - start_time) * 1000
            
            status = HealthStatus.HEALTHY
            if response_time > 2000:  # > 2 seconds
                status = HealthStatus.DEGRADED
            
            return ComponentHealth(
                name="firestore",
                status=status,
                response_time_ms=response_time,
                last_check=datetime.utcnow(),
                details={
                    "collections_count": len(collections),
                    "project_id": self.config.project_id
                }
            )
            
        except Exception as e:
            logger.error(f"Firestore health check failed: {e}")
            return ComponentHealth(
                name="firestore",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow(),
                details={},
                error=str(e)
            )
    
    async def _check_bigquery(self) -> ComponentHealth:
        """Check BigQuery connectivity"""
        start_time = time.time()
        
        try:
            client = bigquery.Client(project=self.config.project_id)
            
            # Test simple query
            query = "SELECT 1 as test_value"
            job = client.query(query)
            results = list(job.result())
            
            response_time = (time.time() - start_time) * 1000
            
            status = HealthStatus.HEALTHY
            if response_time > 3000:  # > 3 seconds
                status = HealthStatus.DEGRADED
            
            return ComponentHealth(
                name="bigquery",
                status=status,
                response_time_ms=response_time,
                last_check=datetime.utcnow(),
                details={
                    "query_result": results[0].test_value if results else None,
                    "project_id": self.config.project_id
                }
            )
            
        except Exception as e:
            logger.error(f"BigQuery health check failed: {e}")
            return ComponentHealth(
                name="bigquery",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow(),
                details={},
                error=str(e)
            )
    
    async def _check_pubsub(self) -> ComponentHealth:
        """Check Pub/Sub connectivity"""
        start_time = time.time()
        
        try:
            publisher = pubsub_v1.PublisherClient()
            
            # List topics to test connectivity
            project_path = f"projects/{self.config.project_id}"
            topics = list(publisher.list_topics(request={"project": project_path}))
            
            response_time = (time.time() - start_time) * 1000
            
            status = HealthStatus.HEALTHY
            if response_time > 2000:  # > 2 seconds
                status = HealthStatus.DEGRADED
            
            return ComponentHealth(
                name="pubsub",
                status=status,
                response_time_ms=response_time,
                last_check=datetime.utcnow(),
                details={
                    "topics_count": len(topics),
                    "project_id": self.config.project_id
                }
            )
            
        except Exception as e:
            logger.error(f"Pub/Sub health check failed: {e}")
            return ComponentHealth(
                name="pubsub",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow(),
                details={},
                error=str(e)
            )
    
    async def _check_storage(self) -> ComponentHealth:
        """Check Cloud Storage connectivity"""
        start_time = time.time()
        
        try:
            from google.cloud import storage
            client = storage.Client(project=self.config.project_id)
            
            # List buckets to test connectivity
            buckets = list(client.list_buckets())
            
            response_time = (time.time() - start_time) * 1000
            
            status = HealthStatus.HEALTHY
            if response_time > 2000:  # > 2 seconds
                status = HealthStatus.DEGRADED
            
            return ComponentHealth(
                name="storage",
                status=status,
                response_time_ms=response_time,
                last_check=datetime.utcnow(),
                details={
                    "buckets_count": len(buckets),
                    "project_id": self.config.project_id
                }
            )
            
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return ComponentHealth(
                name="storage",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow(),
                details={},
                error=str(e)
            )
    
    async def _check_memory(self) -> ComponentHealth:
        """Check memory usage"""
        start_time = time.time()
        
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on memory usage
            status = HealthStatus.HEALTHY
            if memory.percent > 80:
                status = HealthStatus.DEGRADED
            elif memory.percent > 95:
                status = HealthStatus.UNHEALTHY
            
            return ComponentHealth(
                name="memory",
                status=status,
                response_time_ms=response_time,
                last_check=datetime.utcnow(),
                details={
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent
                }
            )
            
        except Exception as e:
            logger.error(f"Memory health check failed: {e}")
            return ComponentHealth(
                name="memory",
                status=HealthStatus.UNKNOWN,
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow(),
                details={},
                error=str(e)
            )
    
    async def _check_disk_space(self) -> ComponentHealth:
        """Check disk space usage"""
        start_time = time.time()
        
        try:
            import psutil
            
            disk = psutil.disk_usage('/')
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on disk usage
            used_percent = (disk.used / disk.total) * 100
            status = HealthStatus.HEALTHY
            if used_percent > 80:
                status = HealthStatus.DEGRADED
            elif used_percent > 95:
                status = HealthStatus.UNHEALTHY
            
            return ComponentHealth(
                name="disk",
                status=status,
                response_time_ms=response_time,
                last_check=datetime.utcnow(),
                details={
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": round(used_percent, 2)
                }
            )
            
        except Exception as e:
            logger.error(f"Disk health check failed: {e}")
            return ComponentHealth(
                name="disk",
                status=HealthStatus.UNKNOWN,
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow(),
                details={},
                error=str(e)
            )
    
    def _determine_overall_status(self, components: List[ComponentHealth]) -> HealthStatus:
        """Determine overall system status based on component health"""
        if not components:
            return HealthStatus.UNKNOWN
        
        statuses = [comp.status for comp in components]
        
        # If any critical component is unhealthy, system is unhealthy
        critical_components = ["database", "firestore"]
        critical_statuses = [
            comp.status for comp in components 
            if comp.name in critical_components
        ]
        
        if HealthStatus.UNHEALTHY in critical_statuses:
            return HealthStatus.UNHEALTHY
        
        # If any component is unhealthy, system is degraded
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.DEGRADED
        
        # If any component is degraded, system is degraded
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        
        # If all components are healthy, system is healthy
        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        
        return HealthStatus.UNKNOWN
    
    def _create_summary(self, components: List[ComponentHealth], check_duration: float) -> Dict[str, Any]:
        """Create summary of health check results"""
        status_counts = {}
        for status in HealthStatus:
            status_counts[status.value] = sum(
                1 for comp in components if comp.status == status
            )
        
        avg_response_time = (
            sum(comp.response_time_ms for comp in components) / len(components)
            if components else 0
        )
        
        return {
            "total_components": len(components),
            "status_breakdown": status_counts,
            "average_response_time_ms": round(avg_response_time, 2),
            "check_duration_ms": round(check_duration * 1000, 2),
            "healthy_components": [
                comp.name for comp in components 
                if comp.status == HealthStatus.HEALTHY
            ],
            "unhealthy_components": [
                comp.name for comp in components 
                if comp.status == HealthStatus.UNHEALTHY
            ]
        }


# Global health checker instance
health_checker = HealthChecker()


async def get_health_status(detailed: bool = False) -> Dict[str, Any]:
    """
    Get system health status
    
    Args:
        detailed: Include detailed component checks
        
    Returns:
        Dictionary with health status information
    """
    health = await health_checker.check_system_health(detailed)
    
    # Convert to dictionary for JSON serialization
    result = asdict(health)
    
    # Convert enums to strings
    result["status"] = health.status.value
    for component in result["components"]:
        component["status"] = component["status"].value if hasattr(component["status"], 'value') else component["status"]
        # Convert datetime to ISO string
        if isinstance(component["last_check"], datetime):
            component["last_check"] = component["last_check"].isoformat()
    
    # Convert datetime to ISO string
    if isinstance(result["timestamp"], datetime):
        result["timestamp"] = result["timestamp"].isoformat()
    
    return result


async def get_readiness_status() -> Dict[str, Any]:
    """
    Get readiness status (critical components only)
    Used by load balancers and orchestrators
    """
    health = await health_checker.check_system_health(include_detailed=False)
    
    is_ready = health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
    
    return {
        "ready": is_ready,
        "status": health.status.value,
        "timestamp": health.timestamp.isoformat(),
        "critical_components": [
            {
                "name": comp.name,
                "status": comp.status.value,
                "response_time_ms": comp.response_time_ms
            }
            for comp in health.components
        ]
    }


async def get_liveness_status() -> Dict[str, Any]:
    """
    Get liveness status (basic health check)
    Used to determine if the service should be restarted
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - health_checker.start_time
    }


# FastAPI endpoints (to be integrated with main API)
def create_health_endpoints():
    """
    Create FastAPI endpoints for health checks
    This function should be called from the main FastAPI app
    """
    from fastapi import APIRouter, HTTPException
    from fastapi.responses import JSONResponse

    router = APIRouter(prefix="/health", tags=["health"])

    @router.get("/")
    async def health_check():
        """Basic health check endpoint"""
        try:
            health_data = await get_health_status(detailed=False)
            status_code = 200 if health_data["status"] in ["healthy", "degraded"] else 503
            return JSONResponse(content=health_data, status_code=status_code)
        except Exception as e:
            logger.error(f"Health check endpoint failed: {e}")
            return JSONResponse(
                content={"status": "unhealthy", "error": str(e)},
                status_code=503
            )

    @router.get("/detailed")
    async def detailed_health_check():
        """Detailed health check with all components"""
        try:
            health_data = await get_health_status(detailed=True)
            status_code = 200 if health_data["status"] in ["healthy", "degraded"] else 503
            return JSONResponse(content=health_data, status_code=status_code)
        except Exception as e:
            logger.error(f"Detailed health check endpoint failed: {e}")
            return JSONResponse(
                content={"status": "unhealthy", "error": str(e)},
                status_code=503
            )

    @router.get("/ready")
    async def readiness_check():
        """Kubernetes readiness probe endpoint"""
        try:
            readiness_data = await get_readiness_status()
            status_code = 200 if readiness_data["ready"] else 503
            return JSONResponse(content=readiness_data, status_code=status_code)
        except Exception as e:
            logger.error(f"Readiness check endpoint failed: {e}")
            return JSONResponse(
                content={"ready": False, "error": str(e)},
                status_code=503
            )

    @router.get("/live")
    async def liveness_check():
        """Kubernetes liveness probe endpoint"""
        try:
            liveness_data = await get_liveness_status()
            return JSONResponse(content=liveness_data, status_code=200)
        except Exception as e:
            logger.error(f"Liveness check endpoint failed: {e}")
            return JSONResponse(
                content={"alive": False, "error": str(e)},
                status_code=503
            )

    return router
