import time
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import psutil
import os

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and store application metrics"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics = defaultdict(deque)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self.start_time = datetime.utcnow()
        self.lock = threading.Lock()
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        with self.lock:
            key = self._make_key(name, tags)
            self.counters[key] += value
            self._add_to_history(key, value, 'counter')
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        with self.lock:
            key = self._make_key(name, tags)
            self.gauges[key] = value
            self._add_to_history(key, value, 'gauge')
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram value"""
        with self.lock:
            key = self._make_key(name, tags)
            self.histograms[key].append(value)
            
            # Keep only recent values
            if len(self.histograms[key]) > self.max_history:
                self.histograms[key] = self.histograms[key][-self.max_history:]
            
            self._add_to_history(key, value, 'histogram')
    
    def record_timing(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None):
        """Record a timing metric"""
        self.record_histogram(f"{name}.duration", duration, tags)
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a key from name and tags"""
        if not tags:
            return name
        
        tag_str = ','.join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
    
    def _add_to_history(self, key: str, value: Any, metric_type: str):
        """Add metric to history"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'value': value,
            'type': metric_type
        }
        
        self.metrics[key].append(entry)
        
        # Keep only recent history
        if len(self.metrics[key]) > self.max_history:
            self.metrics[key].popleft()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        with self.lock:
            return {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {k: self._histogram_stats(v) for k, v in self.histograms.items()},
                'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds()
            }
    
    def _histogram_stats(self, values: List[float]) -> Dict[str, float]:
        """Calculate histogram statistics"""
        if not values:
            return {'count': 0, 'min': 0, 'max': 0, 'mean': 0, 'median': 0}
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            'count': count,
            'min': sorted_values[0],
            'max': sorted_values[-1],
            'mean': sum(sorted_values) / count,
            'median': sorted_values[count // 2],
            'p95': sorted_values[int(count * 0.95)] if count > 0 else 0,
            'p99': sorted_values[int(count * 0.99)] if count > 0 else 0
        }

class SystemMonitor:
    """Monitor system resources and performance"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval: int = 60):
        """Start system monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info(f"System monitoring started with {interval}s interval")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        logger.info("System monitoring stopped")
    
    def _monitor_loop(self, interval: int):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._collect_system_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(interval)
    
    def _collect_system_metrics(self):
        """Collect system metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics.set_gauge('system.cpu.percent', cpu_percent)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self.metrics.set_gauge('system.memory.percent', memory.percent)
        self.metrics.set_gauge('system.memory.used_bytes', memory.used)
        self.metrics.set_gauge('system.memory.available_bytes', memory.available)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        self.metrics.set_gauge('system.disk.percent', disk.percent)
        self.metrics.set_gauge('system.disk.used_bytes', disk.used)
        self.metrics.set_gauge('system.disk.free_bytes', disk.free)
        
        # Network metrics
        network = psutil.net_io_counters()
        self.metrics.set_gauge('system.network.bytes_sent', network.bytes_sent)
        self.metrics.set_gauge('system.network.bytes_recv', network.bytes_recv)
        
        # Process metrics
        process = psutil.Process()
        self.metrics.set_gauge('process.cpu.percent', process.cpu_percent())
        self.metrics.set_gauge('process.memory.percent', process.memory_percent())
        self.metrics.set_gauge('process.memory.rss_bytes', process.memory_info().rss)
        self.metrics.set_gauge('process.threads', process.num_threads())

class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def time_function(self, func_name: str):
        """Decorator to time function execution"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    self.metrics.increment_counter(f'{func_name}.success')
                    return result
                except Exception as e:
                    self.metrics.increment_counter(f'{func_name}.error', tags={'error_type': type(e).__name__})
                    raise
                finally:
                    duration = time.time() - start_time
                    self.metrics.record_timing(func_name, duration)
            return wrapper
        return decorator
    
    def record_api_call(self, endpoint: str, method: str, status_code: int, duration: float):
        """Record API call metrics"""
        tags = {
            'endpoint': endpoint,
            'method': method,
            'status_code': str(status_code)
        }
        
        self.metrics.increment_counter('api.requests', tags=tags)
        self.metrics.record_timing('api.request_duration', duration, tags=tags)
        
        # Record success/error
        if 200 <= status_code < 300:
            self.metrics.increment_counter('api.success', tags=tags)
        else:
            self.metrics.increment_counter('api.error', tags=tags)
    
    def record_blockchain_transaction(self, tx_type: str, success: bool, gas_used: int, duration: float):
        """Record blockchain transaction metrics"""
        tags = {
            'tx_type': tx_type,
            'success': str(success)
        }
        
        self.metrics.increment_counter('blockchain.transactions', tags=tags)
        self.metrics.record_timing('blockchain.transaction_duration', duration, tags=tags)
        self.metrics.record_histogram('blockchain.gas_used', gas_used, tags=tags)
    
    def record_ipfs_operation(self, operation: str, success: bool, size_bytes: int, duration: float):
        """Record IPFS operation metrics"""
        tags = {
            'operation': operation,
            'success': str(success)
        }
        
        self.metrics.increment_counter('ipfs.operations', tags=tags)
        self.metrics.record_timing('ipfs.operation_duration', duration, tags=tags)
        self.metrics.record_histogram('ipfs.file_size', size_bytes, tags=tags)

class AlertManager:
    """Manage alerts based on metrics"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.alerts = []
        self.alert_rules = []
    
    def add_alert_rule(self, name: str, condition: callable, message: str, severity: str = 'warning'):
        """Add an alert rule"""
        self.alert_rules.append({
            'name': name,
            'condition': condition,
            'message': message,
            'severity': severity
        })
    
    def check_alerts(self):
        """Check all alert rules"""
        current_metrics = self.metrics.get_metrics()
        
        for rule in self.alert_rules:
            try:
                if rule['condition'](current_metrics):
                    self._trigger_alert(rule)
            except Exception as e:
                logger.error(f"Error checking alert rule {rule['name']}: {str(e)}")
    
    def _trigger_alert(self, rule: Dict[str, Any]):
        """Trigger an alert"""
        alert = {
            'name': rule['name'],
            'message': rule['message'],
            'severity': rule['severity'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.alerts.append(alert)
        
        # Log the alert
        log_level = logging.ERROR if rule['severity'] == 'critical' else logging.WARNING
        logger.log(log_level, f"ALERT: {rule['name']} - {rule['message']}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        # For now, return all alerts. In a real system, you'd filter by time window
        return self.alerts[-10:]  # Last 10 alerts

# Global instances
metrics_collector = MetricsCollector()
system_monitor = SystemMonitor(metrics_collector)
performance_monitor = PerformanceMonitor(metrics_collector)
alert_manager = AlertManager(metrics_collector)

# Setup default alert rules
def setup_default_alerts():
    """Setup default alert rules"""
    alert_manager.add_alert_rule(
        'high_cpu_usage',
        lambda m: m['gauges'].get('system.cpu.percent', 0) > 80,
        'CPU usage is above 80%',
        'warning'
    )
    
    alert_manager.add_alert_rule(
        'high_memory_usage',
        lambda m: m['gauges'].get('system.memory.percent', 0) > 85,
        'Memory usage is above 85%',
        'critical'
    )
    
    alert_manager.add_alert_rule(
        'high_error_rate',
        lambda m: m['counters'].get('api.error', 0) > 10,
        'API error rate is too high',
        'critical'
    )
    
    alert_manager.add_alert_rule(
        'slow_response_time',
        lambda m: m['histograms'].get('api.request_duration.duration', {}).get('p95', 0) > 5.0,
        'API response time P95 is above 5 seconds',
        'warning'
    )

# Initialize default alerts
setup_default_alerts()
