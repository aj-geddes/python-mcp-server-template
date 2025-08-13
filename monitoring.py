#!/usr/bin/env python3
"""
Enhanced monitoring and observability module for MCP server.
Provides comprehensive metrics, health checks, and alerting capabilities.
"""

import asyncio
import time
import psutil
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import os

# Optional imports for enhanced features
try:
    from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


@dataclass
class HealthMetric:
    """Health metric data structure."""
    name: str
    value: float
    unit: str
    status: str  # OK, WARNING, CRITICAL
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
            
    def evaluate_status(self) -> str:
        """Evaluate health status based on thresholds."""
        if self.threshold_critical is not None and self.value >= self.threshold_critical:
            return "CRITICAL"
        elif self.threshold_warning is not None and self.value >= self.threshold_warning:
            return "WARNING"
        else:
            return "OK"


@dataclass
class SystemHealth:
    """System health snapshot."""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    memory_available: float
    disk_usage: float
    active_connections: int
    uptime_seconds: float
    request_count_1m: int
    error_rate_1m: float
    avg_response_time_1m: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class MetricsCollector:
    """Advanced metrics collection and health monitoring."""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_history = []
        self.error_history = []
        self.response_times = []
        self.active_requests = 0
        self.total_requests = 0
        self.lock = threading.Lock()
        
        # Prometheus metrics (if available)
        if PROMETHEUS_AVAILABLE:
            self.setup_prometheus_metrics()
            
        # System monitoring
        self.process = psutil.Process()
        
        # Health thresholds
        self.health_thresholds = {
            "cpu_usage": {"warning": 70.0, "critical": 90.0},
            "memory_usage": {"warning": 80.0, "critical": 95.0},
            "disk_usage": {"warning": 85.0, "critical": 95.0},
            "error_rate": {"warning": 5.0, "critical": 10.0},
            "response_time": {"warning": 500.0, "critical": 1000.0},
        }
        
    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics."""
        self.prom_request_count = Counter(
            'mcp_requests_total', 
            'Total MCP requests', 
            ['tool', 'status']
        )
        self.prom_request_duration = Histogram(
            'mcp_request_duration_seconds', 
            'Request duration in seconds', 
            ['tool']
        )
        self.prom_active_requests = Gauge(
            'mcp_active_requests', 
            'Currently active requests'
        )
        self.prom_system_cpu = Gauge(
            'mcp_system_cpu_percent', 
            'CPU usage percentage'
        )
        self.prom_system_memory = Gauge(
            'mcp_system_memory_percent', 
            'Memory usage percentage'
        )
        self.prom_system_uptime = Gauge(
            'mcp_system_uptime_seconds', 
            'System uptime in seconds'
        )
        self.prom_health_status = Gauge(
            'mcp_health_status', 
            'Overall health status (1=OK, 0.5=WARNING, 0=CRITICAL)'
        )
        
    def record_request_start(self, tool_name: str) -> str:
        """Record the start of a request."""
        request_id = f"{tool_name}_{int(time.time() * 1000)}"
        
        with self.lock:
            self.active_requests += 1
            self.total_requests += 1
            self.request_history.append({
                "id": request_id,
                "tool": tool_name,
                "start_time": time.time(),
                "status": "active"
            })
            
        if PROMETHEUS_AVAILABLE:
            self.prom_active_requests.set(self.active_requests)
            
        return request_id
        
    def record_request_end(self, request_id: str, success: bool, error: Optional[str] = None):
        """Record the end of a request."""
        end_time = time.time()
        
        with self.lock:
            self.active_requests = max(0, self.active_requests - 1)
            
            # Find and update request in history
            for req in self.request_history:
                if req["id"] == request_id:
                    duration = end_time - req["start_time"]
                    req["end_time"] = end_time
                    req["duration"] = duration
                    req["status"] = "success" if success else "error"
                    req["error"] = error
                    
                    self.response_times.append(duration)
                    if not success:
                        self.error_history.append({
                            "timestamp": end_time,
                            "tool": req["tool"],
                            "error": error
                        })
                    
                    if PROMETHEUS_AVAILABLE:
                        tool_name = req["tool"]
                        status = "success" if success else "error"
                        self.prom_request_count.labels(tool=tool_name, status=status).inc()
                        self.prom_request_duration.labels(tool=tool_name).observe(duration)
                        self.prom_active_requests.set(self.active_requests)
                    
                    break
                    
        # Cleanup old history (keep last 1000 requests)
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
            
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
            
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
            
    def get_system_health(self) -> SystemHealth:
        """Get comprehensive system health metrics."""
        current_time = time.time()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Calculate metrics over last minute
        one_minute_ago = current_time - 60
        
        recent_requests = [
            req for req in self.request_history 
            if req.get("end_time", current_time) >= one_minute_ago
        ]
        
        recent_errors = [
            err for err in self.error_history 
            if err["timestamp"] >= one_minute_ago
        ]
        
        recent_response_times = [
            rt for rt in self.response_times 
            if rt is not None
        ][-100:]  # Last 100 response times
        
        request_count_1m = len(recent_requests)
        error_rate_1m = (len(recent_errors) / max(1, request_count_1m)) * 100
        avg_response_time_1m = (
            sum(recent_response_times) / len(recent_response_times) * 1000 
            if recent_response_times else 0
        )
        
        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            self.prom_system_cpu.set(cpu_percent)
            self.prom_system_memory.set(memory.percent)
            self.prom_system_uptime.set(current_time - self.start_time)
            
        return SystemHealth(
            timestamp=current_time,
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            memory_available=memory.available / (1024 * 1024 * 1024),  # GB
            disk_usage=disk.percent,
            active_connections=self.active_requests,
            uptime_seconds=current_time - self.start_time,
            request_count_1m=request_count_1m,
            error_rate_1m=error_rate_1m,
            avg_response_time_1m=avg_response_time_1m
        )
        
    def get_health_metrics(self) -> List[HealthMetric]:
        """Get detailed health metrics with status evaluation."""
        health = self.get_system_health()
        metrics = []
        
        # CPU usage metric
        cpu_thresholds = self.health_thresholds["cpu_usage"]
        cpu_metric = HealthMetric(
            name="cpu_usage",
            value=health.cpu_usage,
            unit="percent",
            status="",
            threshold_warning=cpu_thresholds["warning"],
            threshold_critical=cpu_thresholds["critical"]
        )
        cpu_metric.status = cpu_metric.evaluate_status()
        metrics.append(cpu_metric)
        
        # Memory usage metric
        mem_thresholds = self.health_thresholds["memory_usage"]
        mem_metric = HealthMetric(
            name="memory_usage",
            value=health.memory_usage,
            unit="percent",
            status="",
            threshold_warning=mem_thresholds["warning"],
            threshold_critical=mem_thresholds["critical"]
        )
        mem_metric.status = mem_metric.evaluate_status()
        metrics.append(mem_metric)
        
        # Disk usage metric
        disk_thresholds = self.health_thresholds["disk_usage"]
        disk_metric = HealthMetric(
            name="disk_usage",
            value=health.disk_usage,
            unit="percent",
            status="",
            threshold_warning=disk_thresholds["warning"],
            threshold_critical=disk_thresholds["critical"]
        )
        disk_metric.status = disk_metric.evaluate_status()
        metrics.append(disk_metric)
        
        # Error rate metric
        error_thresholds = self.health_thresholds["error_rate"]
        error_metric = HealthMetric(
            name="error_rate_1m",
            value=health.error_rate_1m,
            unit="percent",
            status="",
            threshold_warning=error_thresholds["warning"],
            threshold_critical=error_thresholds["critical"]
        )
        error_metric.status = error_metric.evaluate_status()
        metrics.append(error_metric)
        
        # Response time metric
        rt_thresholds = self.health_thresholds["response_time"]
        rt_metric = HealthMetric(
            name="avg_response_time_1m",
            value=health.avg_response_time_1m,
            unit="milliseconds",
            status="",
            threshold_warning=rt_thresholds["warning"],
            threshold_critical=rt_thresholds["critical"]
        )
        rt_metric.status = rt_metric.evaluate_status()
        metrics.append(rt_metric)
        
        return metrics
        
    def get_overall_health_status(self) -> str:
        """Get overall health status."""
        metrics = self.get_health_metrics()
        
        if any(m.status == "CRITICAL" for m in metrics):
            status = "CRITICAL"
        elif any(m.status == "WARNING" for m in metrics):
            status = "WARNING" 
        else:
            status = "OK"
            
        # Update Prometheus health metric
        if PROMETHEUS_AVAILABLE:
            status_value = {"OK": 1.0, "WARNING": 0.5, "CRITICAL": 0.0}[status]
            self.prom_health_status.set(status_value)
            
        return status
        
    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics for external monitoring."""
        health = self.get_system_health()
        metrics = self.get_health_metrics()
        
        return {
            "timestamp": time.time(),
            "system_health": health.to_dict(),
            "health_metrics": [asdict(m) for m in metrics],
            "overall_status": self.get_overall_health_status(),
            "request_statistics": {
                "total_requests": self.total_requests,
                "active_requests": self.active_requests,
                "recent_requests": len([
                    r for r in self.request_history 
                    if r.get("end_time", time.time()) >= time.time() - 300
                ]),
                "recent_errors": len([
                    e for e in self.error_history 
                    if e["timestamp"] >= time.time() - 300
                ])
            }
        }


class HealthMonitor:
    """Health monitoring and alerting service."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.alerts = []
        self.running = False
        self.monitor_task = None
        
    async def start_monitoring(self, interval: int = 30):
        """Start continuous health monitoring."""
        self.running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(interval))
        
    async def stop_monitoring(self):
        """Stop health monitoring."""
        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
                
    async def _monitor_loop(self, interval: int):
        """Main monitoring loop."""
        while self.running:
            try:
                await self._check_health()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Health monitoring error: {e}")
                await asyncio.sleep(interval)
                
    async def _check_health(self):
        """Check system health and generate alerts."""
        metrics = self.metrics.get_health_metrics()
        
        for metric in metrics:
            if metric.status in ["WARNING", "CRITICAL"]:
                alert = {
                    "timestamp": time.time(),
                    "level": metric.status,
                    "metric": metric.name,
                    "value": metric.value,
                    "unit": metric.unit,
                    "threshold": (
                        metric.threshold_critical 
                        if metric.status == "CRITICAL" 
                        else metric.threshold_warning
                    ),
                    "message": f"{metric.name} is {metric.status}: {metric.value}{metric.unit}"
                }
                
                # Add to alerts (keep last 100)
                self.alerts.append(alert)
                if len(self.alerts) > 100:
                    self.alerts = self.alerts[-100:]
                    
                # Log alert
                if STRUCTLOG_AVAILABLE:
                    logger = structlog.get_logger()
                    logger.warning("health_alert", **alert)
                else:
                    print(f"HEALTH ALERT [{alert['level']}]: {alert['message']}")
                    
    def get_recent_alerts(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get recent alerts within specified time window."""
        cutoff = time.time() - (minutes * 60)
        return [alert for alert in self.alerts if alert["timestamp"] >= cutoff]


# Global metrics collector instance
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def start_metrics_server(port: int = 9090):
    """Start Prometheus metrics server."""
    if PROMETHEUS_AVAILABLE:
        try:
            start_http_server(port)
            print(f"📊 Metrics server started on port {port}")
            return True
        except Exception as e:
            print(f"Failed to start metrics server: {e}")
            return False
    else:
        print("⚠️  Prometheus not available - metrics server not started")
        return False


async def main():
    """Demo/test function for monitoring system."""
    print("🔍 Starting Enhanced Monitoring Demo")
    
    # Create metrics collector
    collector = get_metrics_collector()
    
    # Start metrics server
    start_metrics_server(9090)
    
    # Create health monitor
    monitor = HealthMonitor(collector)
    await monitor.start_monitoring(5)  # Check every 5 seconds
    
    # Simulate some requests
    for i in range(10):
        req_id = collector.record_request_start("demo_tool")
        await asyncio.sleep(0.1)  # Simulate work
        collector.record_request_end(req_id, success=i % 4 != 0)  # 25% error rate
        
    # Get health report
    print("\n📊 System Health Report:")
    health = collector.get_system_health()
    print(json.dumps(health.to_dict(), indent=2))
    
    print("\n🏥 Health Metrics:")
    metrics = collector.get_health_metrics()
    for metric in metrics:
        status_icon = {"OK": "✅", "WARNING": "⚠️", "CRITICAL": "🔴"}[metric.status]
        print(f"  {status_icon} {metric.name}: {metric.value:.1f}{metric.unit} ({metric.status})")
        
    print(f"\n🎯 Overall Status: {collector.get_overall_health_status()}")
    
    # Export full metrics
    print("\n📤 Exported Metrics:")
    exported = collector.export_metrics()
    print(json.dumps(exported, indent=2))
    
    await monitor.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())