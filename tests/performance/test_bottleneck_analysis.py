"""
Bottleneck analysis and performance monitoring for CityPulse.
Identifies performance bottlenecks and monitors system resource usage.
"""

import pytest
import time
import psutil
import threading
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class ResourceMetrics:
    """System resource metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float


@dataclass
class BottleneckAnalysis:
    """Bottleneck analysis results."""
    component: str
    bottleneck_type: str
    severity: str  # low, medium, high, critical
    description: str
    metrics: Dict[str, Any]
    recommendations: List[str]


class SystemMonitor:
    """System resource monitoring for performance analysis."""
    
    def __init__(self, interval: float = 1.0):
        """Initialize system monitor."""
        self.interval = interval
        self.monitoring = False
        self.metrics = []
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start system monitoring."""
        self.monitoring = True
        self.metrics = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
        logger.info("System monitoring started")
    
    def stop_monitoring(self) -> List[ResourceMetrics]:
        """Stop system monitoring and return collected metrics."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info(f"System monitoring stopped. Collected {len(self.metrics)} data points")
        return self.metrics
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        # Get initial network and disk I/O counters
        net_io_start = psutil.net_io_counters()
        disk_io_start = psutil.disk_io_counters()
        
        while self.monitoring:
            try:
                # Get current metrics
                cpu_percent = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory()
                
                # Get network and disk I/O
                net_io_current = psutil.net_io_counters()
                disk_io_current = psutil.disk_io_counters()
                
                # Calculate I/O rates (MB/s)
                net_sent_mb = (net_io_current.bytes_sent - net_io_start.bytes_sent) / (1024 * 1024)
                net_recv_mb = (net_io_current.bytes_recv - net_io_start.bytes_recv) / (1024 * 1024)
                disk_read_mb = (disk_io_current.read_bytes - disk_io_start.read_bytes) / (1024 * 1024)
                disk_write_mb = (disk_io_current.write_bytes - disk_io_start.write_bytes) / (1024 * 1024)
                
                metrics = ResourceMetrics(
                    timestamp=datetime.utcnow(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_used_mb=memory.used / (1024 * 1024),
                    disk_io_read_mb=disk_read_mb,
                    disk_io_write_mb=disk_write_mb,
                    network_sent_mb=net_sent_mb,
                    network_recv_mb=net_recv_mb
                )
                
                self.metrics.append(metrics)
                
                # Update baseline for next iteration
                net_io_start = net_io_current
                disk_io_start = disk_io_current
                
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.interval)


class BottleneckAnalyzer:
    """Analyze performance bottlenecks from metrics."""
    
    def __init__(self):
        """Initialize bottleneck analyzer."""
        self.thresholds = {
            "cpu_high": 80.0,
            "cpu_critical": 95.0,
            "memory_high": 80.0,
            "memory_critical": 95.0,
            "disk_io_high": 100.0,  # MB/s
            "network_high": 50.0,   # MB/s
            "response_time_high": 2000.0,  # ms
            "response_time_critical": 5000.0,  # ms
            "error_rate_high": 5.0,  # %
            "error_rate_critical": 10.0  # %
        }
    
    def analyze_resource_bottlenecks(self, metrics: List[ResourceMetrics]) -> List[BottleneckAnalysis]:
        """Analyze resource-based bottlenecks."""
        bottlenecks = []
        
        if not metrics:
            return bottlenecks
        
        # Calculate statistics
        cpu_values = [m.cpu_percent for m in metrics]
        memory_values = [m.memory_percent for m in metrics]
        disk_read_values = [m.disk_io_read_mb for m in metrics]
        disk_write_values = [m.disk_io_write_mb for m in metrics]
        network_sent_values = [m.network_sent_mb for m in metrics]
        network_recv_values = [m.network_recv_mb for m in metrics]
        
        # CPU bottleneck analysis
        avg_cpu = statistics.mean(cpu_values)
        max_cpu = max(cpu_values)
        
        if max_cpu > self.thresholds["cpu_critical"]:
            bottlenecks.append(BottleneckAnalysis(
                component="CPU",
                bottleneck_type="Resource Exhaustion",
                severity="critical",
                description=f"CPU usage peaked at {max_cpu:.1f}% (avg: {avg_cpu:.1f}%)",
                metrics={"avg_cpu": avg_cpu, "max_cpu": max_cpu},
                recommendations=[
                    "Consider horizontal scaling",
                    "Optimize CPU-intensive operations",
                    "Implement caching to reduce computation",
                    "Profile code for CPU hotspots"
                ]
            ))
        elif avg_cpu > self.thresholds["cpu_high"]:
            bottlenecks.append(BottleneckAnalysis(
                component="CPU",
                bottleneck_type="High Utilization",
                severity="high",
                description=f"Sustained high CPU usage: {avg_cpu:.1f}%",
                metrics={"avg_cpu": avg_cpu, "max_cpu": max_cpu},
                recommendations=[
                    "Monitor CPU usage trends",
                    "Consider vertical scaling",
                    "Optimize algorithms and data structures"
                ]
            ))
        
        # Memory bottleneck analysis
        avg_memory = statistics.mean(memory_values)
        max_memory = max(memory_values)
        
        if max_memory > self.thresholds["memory_critical"]:
            bottlenecks.append(BottleneckAnalysis(
                component="Memory",
                bottleneck_type="Memory Pressure",
                severity="critical",
                description=f"Memory usage peaked at {max_memory:.1f}% (avg: {avg_memory:.1f}%)",
                metrics={"avg_memory": avg_memory, "max_memory": max_memory},
                recommendations=[
                    "Increase available memory",
                    "Implement memory pooling",
                    "Optimize data structures",
                    "Check for memory leaks"
                ]
            ))
        elif avg_memory > self.thresholds["memory_high"]:
            bottlenecks.append(BottleneckAnalysis(
                component="Memory",
                bottleneck_type="High Memory Usage",
                severity="high",
                description=f"Sustained high memory usage: {avg_memory:.1f}%",
                metrics={"avg_memory": avg_memory, "max_memory": max_memory},
                recommendations=[
                    "Monitor memory usage patterns",
                    "Implement garbage collection tuning",
                    "Consider memory-efficient data structures"
                ]
            ))
        
        # Disk I/O bottleneck analysis
        max_disk_read = max(disk_read_values) if disk_read_values else 0
        max_disk_write = max(disk_write_values) if disk_write_values else 0
        
        if max_disk_read > self.thresholds["disk_io_high"] or max_disk_write > self.thresholds["disk_io_high"]:
            bottlenecks.append(BottleneckAnalysis(
                component="Disk I/O",
                bottleneck_type="I/O Bottleneck",
                severity="medium",
                description=f"High disk I/O: {max_disk_read:.1f} MB/s read, {max_disk_write:.1f} MB/s write",
                metrics={"max_disk_read": max_disk_read, "max_disk_write": max_disk_write},
                recommendations=[
                    "Consider SSD storage",
                    "Implement read caching",
                    "Optimize database queries",
                    "Use connection pooling"
                ]
            ))
        
        # Network bottleneck analysis
        max_network_sent = max(network_sent_values) if network_sent_values else 0
        max_network_recv = max(network_recv_values) if network_recv_values else 0
        
        if max_network_sent > self.thresholds["network_high"] or max_network_recv > self.thresholds["network_high"]:
            bottlenecks.append(BottleneckAnalysis(
                component="Network",
                bottleneck_type="Network Bottleneck",
                severity="medium",
                description=f"High network usage: {max_network_sent:.1f} MB/s sent, {max_network_recv:.1f} MB/s received",
                metrics={"max_network_sent": max_network_sent, "max_network_recv": max_network_recv},
                recommendations=[
                    "Implement response compression",
                    "Use CDN for static assets",
                    "Optimize payload sizes",
                    "Consider network bandwidth upgrade"
                ]
            ))
        
        return bottlenecks
    
    def analyze_application_bottlenecks(self, performance_metrics: Dict[str, Any]) -> List[BottleneckAnalysis]:
        """Analyze application-level bottlenecks."""
        bottlenecks = []
        
        # Response time analysis
        if "avg_response_time" in performance_metrics:
            avg_response_time = performance_metrics["avg_response_time"]
            p95_response_time = performance_metrics.get("p95_response_time", 0)
            
            if p95_response_time > self.thresholds["response_time_critical"]:
                bottlenecks.append(BottleneckAnalysis(
                    component="Application",
                    bottleneck_type="Slow Response Times",
                    severity="critical",
                    description=f"95th percentile response time: {p95_response_time:.0f}ms",
                    metrics={"avg_response_time": avg_response_time, "p95_response_time": p95_response_time},
                    recommendations=[
                        "Profile application code",
                        "Optimize database queries",
                        "Implement caching strategies",
                        "Consider async processing"
                    ]
                ))
            elif avg_response_time > self.thresholds["response_time_high"]:
                bottlenecks.append(BottleneckAnalysis(
                    component="Application",
                    bottleneck_type="High Response Times",
                    severity="high",
                    description=f"Average response time: {avg_response_time:.0f}ms",
                    metrics={"avg_response_time": avg_response_time},
                    recommendations=[
                        "Monitor response time trends",
                        "Optimize critical code paths",
                        "Review database performance"
                    ]
                ))
        
        # Error rate analysis
        if "error_rate" in performance_metrics:
            error_rate = performance_metrics["error_rate"]
            
            if error_rate > self.thresholds["error_rate_critical"]:
                bottlenecks.append(BottleneckAnalysis(
                    component="Application",
                    bottleneck_type="High Error Rate",
                    severity="critical",
                    description=f"Error rate: {error_rate:.1f}%",
                    metrics={"error_rate": error_rate},
                    recommendations=[
                        "Investigate error logs",
                        "Implement circuit breakers",
                        "Add retry mechanisms",
                        "Improve error handling"
                    ]
                ))
            elif error_rate > self.thresholds["error_rate_high"]:
                bottlenecks.append(BottleneckAnalysis(
                    component="Application",
                    bottleneck_type="Elevated Error Rate",
                    severity="high",
                    description=f"Error rate: {error_rate:.1f}%",
                    metrics={"error_rate": error_rate},
                    recommendations=[
                        "Monitor error patterns",
                        "Review application logs",
                        "Implement better validation"
                    ]
                ))
        
        # Throughput analysis
        if "throughput" in performance_metrics:
            throughput = performance_metrics["throughput"]
            
            if throughput < 5.0:  # Less than 5 req/s is concerning
                bottlenecks.append(BottleneckAnalysis(
                    component="Application",
                    bottleneck_type="Low Throughput",
                    severity="high",
                    description=f"Low throughput: {throughput:.1f} req/s",
                    metrics={"throughput": throughput},
                    recommendations=[
                        "Optimize request processing",
                        "Implement connection pooling",
                        "Consider horizontal scaling",
                        "Profile application bottlenecks"
                    ]
                ))
        
        return bottlenecks


class TestBottleneckIdentification:
    """Tests for identifying performance bottlenecks."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.monitor = SystemMonitor(interval=0.5)
        self.analyzer = BottleneckAnalyzer()
    
    @pytest.mark.performance
    def test_cpu_bottleneck_detection(self):
        """Test CPU bottleneck detection under load."""
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Simulate CPU-intensive workload
        def cpu_intensive_task():
            # Simulate CPU-bound operation
            start_time = time.time()
            while time.time() - start_time < 5:  # Run for 5 seconds
                # CPU-intensive calculation
                sum(i * i for i in range(10000))
        
        # Run multiple CPU-intensive tasks
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(cpu_intensive_task) for _ in range(4)]
            for future in futures:
                future.result()
        
        # Stop monitoring and analyze
        metrics = self.monitor.stop_monitoring()
        bottlenecks = self.analyzer.analyze_resource_bottlenecks(metrics)
        
        # Should detect CPU bottleneck
        cpu_bottlenecks = [b for b in bottlenecks if b.component == "CPU"]
        assert len(cpu_bottlenecks) > 0, "CPU bottleneck not detected"
        
        logger.info(f"Detected {len(cpu_bottlenecks)} CPU bottlenecks")
        for bottleneck in cpu_bottlenecks:
            logger.info(f"CPU Bottleneck: {bottleneck.description}")
    
    @pytest.mark.performance
    def test_memory_bottleneck_detection(self):
        """Test memory bottleneck detection."""
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Simulate memory-intensive workload
        def memory_intensive_task():
            # Allocate large amounts of memory
            large_data = []
            for i in range(1000):
                large_data.append([0] * 10000)  # Allocate memory
                time.sleep(0.01)  # Small delay
            return len(large_data)
        
        # Run memory-intensive task
        result = memory_intensive_task()
        
        # Stop monitoring and analyze
        metrics = self.monitor.stop_monitoring()
        bottlenecks = self.analyzer.analyze_resource_bottlenecks(metrics)
        
        # Check for memory-related bottlenecks
        memory_bottlenecks = [b for b in bottlenecks if b.component == "Memory"]
        
        logger.info(f"Detected {len(memory_bottlenecks)} memory bottlenecks")
        for bottleneck in memory_bottlenecks:
            logger.info(f"Memory Bottleneck: {bottleneck.description}")
        
        assert result > 0, "Memory task should complete"
    
    @pytest.mark.performance
    def test_application_bottleneck_analysis(self):
        """Test application-level bottleneck analysis."""
        # Simulate performance metrics from a load test
        performance_metrics = {
            "avg_response_time": 3500,  # High response time
            "p95_response_time": 6000,  # Very high 95th percentile
            "error_rate": 8.5,  # High error rate
            "throughput": 3.2,  # Low throughput
            "total_requests": 1000,
            "success_count": 915,
            "error_count": 85
        }
        
        # Analyze bottlenecks
        bottlenecks = self.analyzer.analyze_application_bottlenecks(performance_metrics)
        
        # Should detect multiple application bottlenecks
        assert len(bottlenecks) > 0, "Application bottlenecks not detected"
        
        # Check for specific bottleneck types
        response_time_bottlenecks = [b for b in bottlenecks if "Response Times" in b.bottleneck_type]
        error_rate_bottlenecks = [b for b in bottlenecks if "Error Rate" in b.bottleneck_type]
        throughput_bottlenecks = [b for b in bottlenecks if "Throughput" in b.bottleneck_type]
        
        assert len(response_time_bottlenecks) > 0, "Response time bottleneck not detected"
        assert len(error_rate_bottlenecks) > 0, "Error rate bottleneck not detected"
        assert len(throughput_bottlenecks) > 0, "Throughput bottleneck not detected"
        
        logger.info(f"Detected {len(bottlenecks)} application bottlenecks:")
        for bottleneck in bottlenecks:
            logger.info(f"- {bottleneck.component}: {bottleneck.description} ({bottleneck.severity})")
    
    @pytest.mark.performance
    def test_comprehensive_bottleneck_analysis(self):
        """Test comprehensive bottleneck analysis combining system and application metrics."""
        # Start system monitoring
        self.monitor.start_monitoring()
        
        # Simulate mixed workload
        def mixed_workload():
            # CPU + Memory + I/O intensive task
            data = []
            for i in range(500):
                # CPU work
                result = sum(j * j for j in range(1000))
                # Memory allocation
                data.append([result] * 100)
                # Simulate I/O delay
                time.sleep(0.01)
            return len(data)
        
        # Run workload
        start_time = time.time()
        result = mixed_workload()
        end_time = time.time()
        
        # Stop monitoring
        resource_metrics = self.monitor.stop_monitoring()
        
        # Simulate application performance metrics
        app_metrics = {
            "avg_response_time": 2500,
            "p95_response_time": 4000,
            "error_rate": 3.2,
            "throughput": 8.5,
            "duration": end_time - start_time
        }
        
        # Analyze both types of bottlenecks
        resource_bottlenecks = self.analyzer.analyze_resource_bottlenecks(resource_metrics)
        app_bottlenecks = self.analyzer.analyze_application_bottlenecks(app_metrics)
        
        all_bottlenecks = resource_bottlenecks + app_bottlenecks
        
        logger.info(f"Comprehensive analysis found {len(all_bottlenecks)} bottlenecks:")
        for bottleneck in all_bottlenecks:
            logger.info(f"- {bottleneck.component} ({bottleneck.severity}): {bottleneck.description}")
            logger.info(f"  Recommendations: {', '.join(bottleneck.recommendations[:2])}")
        
        # Generate bottleneck report
        report = self._generate_bottleneck_report(all_bottlenecks, resource_metrics, app_metrics)
        
        # Save report
        with open("test-reports/bottleneck-analysis.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        assert result > 0, "Mixed workload should complete"
    
    def _generate_bottleneck_report(
        self, 
        bottlenecks: List[BottleneckAnalysis], 
        resource_metrics: List[ResourceMetrics],
        app_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive bottleneck analysis report."""
        return {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_bottlenecks": len(bottlenecks),
                "critical_bottlenecks": len([b for b in bottlenecks if b.severity == "critical"]),
                "high_bottlenecks": len([b for b in bottlenecks if b.severity == "high"]),
                "medium_bottlenecks": len([b for b in bottlenecks if b.severity == "medium"])
            },
            "bottlenecks": [
                {
                    "component": b.component,
                    "type": b.bottleneck_type,
                    "severity": b.severity,
                    "description": b.description,
                    "metrics": b.metrics,
                    "recommendations": b.recommendations
                }
                for b in bottlenecks
            ],
            "resource_summary": {
                "monitoring_duration": len(resource_metrics) * 0.5,  # seconds
                "avg_cpu": statistics.mean([m.cpu_percent for m in resource_metrics]) if resource_metrics else 0,
                "avg_memory": statistics.mean([m.memory_percent for m in resource_metrics]) if resource_metrics else 0,
                "max_cpu": max([m.cpu_percent for m in resource_metrics]) if resource_metrics else 0,
                "max_memory": max([m.memory_percent for m in resource_metrics]) if resource_metrics else 0
            },
            "application_summary": app_metrics
        }
