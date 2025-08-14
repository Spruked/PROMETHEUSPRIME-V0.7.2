import os
from datetime import datetime
from typing import List, Dict
import logging
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from prometheus_client import CollectorRegistry, Gauge, generate_latest
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# --- Pydantic Models for Data Validation ---
class GlyphRequest(BaseModel):
    """Model for the glyph activation request body."""
    context: str

class ReconcileRequest(BaseModel):
    """Model for the reconciliation request body."""
    entity1: str
    entity2: str

# --- Mock Modules and Data for Demonstration ---
class MockMetricsCollector:
    """Mocks a Prometheus metrics collector."""
    def __init__(self):
        self.registry = CollectorRegistry()
        self.gauge_requests_total = Gauge('fastapi_requests_total', 'Total number of requests', registry=self.registry)
        self.gauge_status_total = Gauge('fastapi_requests_status_total', 'Requests by status code', ['status'], registry=self.registry)
        self.gauge_http_total = Gauge('fastapi_requests_http_total', 'Requests by HTTP method', ['method'], registry=self.registry)
        self.gauge_latency = Gauge('fastapi_request_latency_seconds', 'Request latency in seconds', ['route'], registry=self.registry)

    def get_metrics(self):
        self.gauge_requests_total.inc()
        self.gauge_status_total.labels(status='200').inc()
        self.gauge_http_total.labels(method='GET').inc()
        self.gauge_latency.labels(route='/metrics').set(0.01)
        return generate_latest(self.registry).decode('utf-8')

class MockCaliClient:
    """Mocks the Cali core logic for glyph activation."""
    def __init__(self):
        self.behavioral_log: List[Dict[str, str]] = []
    
    def activate_glyphs(self, context: str) -> Dict[str, object]:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "Glyph Activation",
            "context": context,
            "details": f"Simulated activation for context: '{context}'"
        }
        self.behavioral_log.append(log_entry)
        return {"message": "Glyphs activated successfully!", "log_entry": log_entry}

    def get_behavioral_log(self):
        return self.behavioral_log

    def reconcile_entities(self, entity1: str, entity2: str):
        return {"result": f"Reconciliation between {entity1} and {entity2} successful."}

metrics_collector = MockMetricsCollector()
cali_client = MockCaliClient()
# End of mock classes

logger = logging.getLogger(__name__)

# FastAPI app setup
app = FastAPI(title="Prometheus Master Dashboard")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

## Removed logic that overwrites dashboard.html with Python code

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})