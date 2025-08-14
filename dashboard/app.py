import os
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any
import logging
import asyncio
import socketio
from socketio.asgi import ASGIApp
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
 
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import system modules
# NOTE: These modules are not included in the provided code.
# The application will not run without them.
from config.secure_config import config
from security.monitoring import metrics_collector, system_monitor, alert_manager
from security.error_handler import health_check
from security.advanced_security import security_audit
from auth import require_api_key

logger = logging.getLogger(__name__)


# FastAPI app setup
# The main FastAPI app instance
app = FastAPI(title="Prometheus NFT Minting Engine Dashboard", version="1.0.0")

# Setup Socket.IO
# Create an async Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=[])

# Wrap the FastAPI app and the Socket.IO server into a single ASGI application
# This allows both HTTP routes and WebSocket connections to be handled
# by the same application instance. The Socket.IO endpoint will be at the root.
socket_app = socketio.ASGIApp(sio, app)

# Health check endpoints
@app.get("/health/live")
def health_live():
    return {"ok": True}

@app.get("/health/static")
def health_static():
    # Adjust path as needed if running from a different working directory
    health_file = os.path.join(os.path.dirname(__file__), "../ui/public/health.txt")
    if os.path.exists(health_file):
        return FileResponse(health_file, media_type="text/plain")
    return JSONResponse(status_code=404, content={"ok": False, "error": "health.txt not found"})

# Example protected endpoint using API key dependency
@app.post("/mint")
def mint(payload: dict, _: None = Depends(require_api_key)):
    # ... mint logic ...
    return {"status": "ok"}

# Template and Static files setup
templates = Jinja2Templates(directory="templates")
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "public")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Dashboard configuration
dashboard_config = {
    'update_interval': 5,  # seconds
    'max_log_entries': 100,
    'refresh_rate': 1000,  # milliseconds
    'chart_data_points': 50
}

# Real-time data storage
realtime_data = {
    'metrics': {},
    'logs': [],
    'alerts': [],
    'transactions': [],
    'system_status': {}
}

def get_dashboard_config():
    return {
        'title': 'Prometheus NFT Minting Engine Dashboard',
        'version': '1.0.0',
        'update_interval': dashboard_config['update_interval'],
        'refresh_rate': dashboard_config['refresh_rate'],
        'environment': config.flask_env,
        'network': config.network
    }

def get_uptime():
    try:
        uptime_seconds = (datetime.now(timezone.utc) - system_monitor.metrics.start_time).total_seconds()
        return {
            'seconds': uptime_seconds,
            'human_readable': str(timedelta(seconds=int(uptime_seconds)))
        }
    except Exception:
        return {'seconds': 0, 'human_readable': '0:00:00'}

# HTML Endpoints
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "config": get_dashboard_config()})

@app.get("/config", response_class=HTMLResponse)
def config_page(request: Request):
    return templates.TemplateResponse("config.html", {"request": request, "config": config.to_dict(), "dashboard_config": dashboard_config})

@app.get("/monitoring", response_class=HTMLResponse)
def monitoring_page(request: Request):
    return templates.TemplateResponse("monitoring.html", {"request": request})

@app.get("/security", response_class=HTMLResponse)
def security_page(request: Request):
    return templates.TemplateResponse("security.html", {"request": request})

@app.get("/transactions", response_class=HTMLResponse)
def transactions_page(request: Request):
    return templates.TemplateResponse("transactions.html", {"request": request})

@app.get("/logs", response_class=HTMLResponse)
def logs_page(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

# API Endpoints
@app.get("/api/status", response_model=None)
def api_status():
    try:
        health_result = health_check()
        return {
            'status': 'healthy' if health_result['status'] == 'healthy' else 'unhealthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'health_check': health_result,
            'uptime': get_uptime()
        }
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return JSONResponse(status_code=500, content={'error': str(e)})

@app.get("/api/metrics", response_model=None)
def api_metrics():
    try:
        metrics = metrics_collector.get_metrics()
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': metrics
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return JSONResponse(status_code=500, content={'error': str(e)})

@app.get("/api/alerts", response_model=None)
def api_alerts():
    try:
        alerts = alert_manager.get_active_alerts()
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'alerts': alerts
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        return JSONResponse(status_code=500, content={'error': str(e)})

@app.get("/api/audit", response_model=None)
def api_audit():
    try:
        compliance_results = security_audit.run_compliance_checks()
        audit_log = security_audit.get_audit_log(50)
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'compliance': compliance_results,
            'audit_log': audit_log
        }
    except Exception as e:
        logger.error(f"Error getting audit info: {str(e)}")
        return JSONResponse(status_code=500, content={'error': str(e)})

@app.get("/api/transactions", response_model=None)
def api_transactions():
    try:
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'transactions': realtime_data['transactions'][-50:]
        }
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        return JSONResponse(status_code=500, content={'error': str(e)})

@app.get("/api/config", response_model=None)
def api_config():
    try:
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'config': config.to_dict(),
            'dashboard_config': dashboard_config
        }
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        return JSONResponse(status_code=500, content={'error': str(e)})

@app.get("/api/logs", response_model=None)
def api_logs():
    try:
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'logs': realtime_data['logs'][-100:]
        }
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        return JSONResponse(status_code=500, content={'error': str(e)})

# WebSocket Handlers (Socket.IO)
@sio.on('connect')
async def handle_connect(sid, environ, auth):
    await sio.emit('connected', {'data': 'Connected to dashboard'}, room=sid)
    logger.info(f"Dashboard client connected: {sid}")

@sio.on('disconnect')
async def handle_disconnect(sid):
    logger.info(f"Dashboard client disconnected: {sid}")

@sio.on('request_update')
async def handle_request_update(sid, data):
    await send_realtime_update(sid)

@sio.on('request_metrics')
async def handle_request_metrics(sid, data):
    try:
        metrics = metrics_collector.get_metrics()
        await sio.emit('metrics_update', {'metrics': metrics}, room=sid)
    except Exception as e:
        logger.error(f"Error sending metrics: {str(e)}")
        await sio.emit('error', {'message': str(e)}, room=sid)

# Fix for the background thread issue
# Use FastAPI's lifespan events to manage an asyncio task
async def main_background_task():
    """A background task to periodically update metrics and broadcast to clients."""
    while True:
        try:
            # Update real-time data
            realtime_data['metrics'] = metrics_collector.get_metrics()
            realtime_data['alerts'] = alert_manager.get_active_alerts()
            realtime_data['system_status'] = health_check()
            
            # Broadcast the update to all connected clients
            update_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'metrics': realtime_data['metrics'],
                'alerts': realtime_data['alerts'],
                'system_status': realtime_data['system_status']
            }
            await sio.emit('realtime_update', update_data)
            
        except Exception as e:
            logger.error(f"Error in background update task: {str(e)}")

        # Wait for the next update interval
        await asyncio.sleep(dashboard_config['update_interval'])

async def send_realtime_update(sid=None):
    """Sends a real-time update to a specific client or all clients."""
    try:
        update_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': realtime_data['metrics'],
            'alerts': realtime_data['alerts'],
            'system_status': realtime_data['system_status']
        }
        await sio.emit('realtime_update', update_data, room=sid)
    except Exception as e:
        logger.error(f"Error sending real-time update: {str(e)}")

# This function is no longer needed, as the background task is managed by lifespan events
# def start_background_tasks():
#     def update_realtime_data():
#         # ... old logic ...
#         pass
#     update_thread = threading.Thread(target=update_realtime_data)
#     update_thread.daemon = True
#     update_thread.start()

# We use the FastAPI lifespan events to start and stop our background task
@app.on_event("startup")
async def startup_event():
    """Starts the background task when the application starts."""
    app.background_task = asyncio.create_task(main_background_task())

@app.on_event("shutdown")
async def shutdown_event():
    """Cancels the background task when the application shuts down."""
    app.background_task.cancel()

# Entry point for the application.
# Run with `uvicorn app:socket_app --reload`
# The `socket_app` is the combined ASGI application
# that handles both FastAPI routes and Socket.IO connections.
