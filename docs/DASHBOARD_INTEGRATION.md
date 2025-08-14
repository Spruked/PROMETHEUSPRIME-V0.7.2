# Dashboard Integration Guide

## Overview

The Pro Prime Minting Alpha dashboard provides a comprehensive web-based interface for monitoring and managing the NFT minting engine. It includes real-time monitoring, security auditing, and configuration management.

## Quick Start

### 1. Installation

```bash
# Install all dependencies
pip install -r requirements.txt

# For Windows users (recommended)
pip install pywin32 winshell
```

### 2. Starting the Dashboard

```bash
# Option 1: Using the startup script (recommended)
python start_dashboard.py

# Option 2: Manual start
python dashboard/app.py
```

### 3. Access the Dashboard

- **URL**: http://localhost:5001
- **Default Port**: 5001 (configurable)
- **Auto-open**: Browser opens automatically with startup script

## Features

### Main Dashboard
- **Real-time Metrics**: Live charts and statistics
- **System Status**: Health indicators and alerts
- **Performance Monitor**: Resource usage tracking
- **Recent Activity**: Latest transactions and events

### Security Audit
- **Threat Detection**: Real-time security monitoring
- **Compliance Checks**: Regulatory compliance tracking
- **Audit Logs**: Detailed security event logging
- **Risk Assessment**: Automated security scoring

### Configuration Management
- **Settings**: Runtime configuration updates
- **Environment**: Environment variable management
- **API Keys**: Secure key management
- **Permissions**: Access control settings

### Monitoring & Alerts
- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Request rates, response times
- **Custom Alerts**: Configurable thresholds
- **Notification System**: Email and webhook alerts

## Configuration

### Environment Variables

```bash
# Dashboard Configuration
DASHBOARD_PORT=5001
DASHBOARD_HOST=0.0.0.0
DASHBOARD_SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///dashboard.db
REDIS_URL=redis://localhost:6379

# Security Settings
SECURITY_AUDIT_ENABLED=true
COMPLIANCE_CHECKING=true
THREAT_DETECTION=true

# Monitoring Configuration
METRICS_ENABLED=true
PROMETHEUS_ENABLED=true
ALERT_WEBHOOK_URL=https://your-webhook-url.com
```

### Configuration Files

- `config/config.json`: Main configuration
- `config/dashboard_config.json`: Dashboard-specific settings
- `config/security_config.json`: Security configuration
- `config/monitoring_config.json`: Monitoring settings

## API Integration

### WebSocket Events

The dashboard uses WebSocket for real-time updates:

```javascript
// Connect to dashboard WebSocket
const socket = io();

// Listen for metrics updates
socket.on('metrics_update', (data) => {
    updateDashboard(data);
});

// Listen for security alerts
socket.on('security_alert', (alert) => {
    handleSecurityAlert(alert);
});
```

### REST API Endpoints

- `GET /api/metrics`: Get current metrics
- `GET /api/security/status`: Security status
- `GET /api/config`: Configuration data
- `POST /api/config`: Update configuration
- `GET /api/audit/logs`: Audit log entries

## Monitoring Integration

### Prometheus Metrics

The dashboard exposes metrics in Prometheus format:

```
# HELP minting_requests_total Total number of minting requests
# TYPE minting_requests_total counter
minting_requests_total{status="success"} 1234

# HELP security_events_total Total number of security events
# TYPE security_events_total counter
security_events_total{severity="high"} 5
```

### Custom Metrics

Add custom metrics to your code:

```python
from dashboard.monitoring import MetricsCollector

metrics = MetricsCollector()

# Increment counters
metrics.increment_counter('custom_event_total')

# Set gauges
metrics.set_gauge('queue_size', 42)

# Record histograms
metrics.record_histogram('request_duration', 0.123)
```

## Security Features

### Authentication

- **JWT Tokens**: Secure authentication
- **Session Management**: Automatic session handling
- **Multi-factor**: Optional 2FA support

### Authorization

- **Role-based Access**: Different permission levels
- **Resource Protection**: Endpoint-level security
- **Audit Trail**: All access logged

### Data Protection

- **Encryption**: All sensitive data encrypted
- **Secure Storage**: Protected configuration
- **Input Validation**: Comprehensive sanitization

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using port 5001
   netstat -ano | findstr :5001
   
   # Kill the process or change port
   set DASHBOARD_PORT=5002
   ```

2. **Permission Errors**
   ```bash
   # Run as administrator (Windows)
   # Or check file permissions
   ```

3. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
set FLASK_ENV=development
set FLASK_DEBUG=1
python dashboard/app.py
```

### Log Files

- `logs/dashboard.log`: Main dashboard logs
- `logs/security.log`: Security event logs
- `logs/monitoring.log`: Monitoring system logs
- `logs/api.log`: API request logs

## Performance Optimization

### Production Deployment

```bash
# Use Gunicorn for production
gunicorn -w 4 -k eventlet dashboard.app:app --bind 0.0.0.0:5001
```

### Caching

- **Redis**: Session and metric caching
- **Memory Cache**: Frequent data caching
- **Static Files**: CDN integration

### Database Optimization

- **Connection Pooling**: Efficient database usage
- **Query Optimization**: Indexed queries
- **Cleanup Tasks**: Automatic log rotation

## Integration with Main API

### Shared Configuration

The dashboard shares configuration with the main minting API:

```python
# In your main API
from dashboard.config import DashboardConfig

config = DashboardConfig()
dashboard_url = config.get_dashboard_url()
```

### Event Broadcasting

Send events to the dashboard from your main application:

```python
from dashboard.events import EventBroadcaster

broadcaster = EventBroadcaster()
broadcaster.send_event('minting_completed', {
    'transaction_hash': '0x123...',
    'token_id': 42,
    'timestamp': datetime.now()
})
```

## Support and Maintenance

### Updates

```bash
# Update dashboard
git pull origin main
pip install -r requirements.txt

# Restart dashboard
python start_dashboard.py
```

### Backup

```bash
# Backup configuration
cp -r config/ config_backup/

# Backup database
cp dashboard.db dashboard_backup.db
```

### Monitoring Health

The dashboard includes health checks:

- `/health`: Basic health check
- `/metrics`: Prometheus metrics
- `/status`: Detailed system status

## Development

### Local Development

```bash
# Clone and setup
git clone <repository>
cd Pro_Prime_Minting_Alpha
pip install -r requirements.txt

# Run in development mode
set FLASK_ENV=development
python dashboard/app.py
```

### Testing

```bash
# Run dashboard tests
pytest dashboard/tests/

# Run with coverage
pytest --cov=dashboard dashboard/tests/
```

### Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

This dashboard is part of the Pro Prime Minting Alpha system and follows the same license terms.
