from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any

try:
    from codex_core import get_suggestion, store_memory, get_full_vault, get_insight_threads
except ImportError:
    def get_suggestion():
        return "[codex_core missing]"
    def store_memory(payload):
        return "[codex_core missing]"


# --- Imports ---
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import os
from core.mirror.mirror import Caleon

# --- FastAPI App ---
app = FastAPI(title="Prometheus Prime API", version="0.7.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class EthicsRequest(BaseModel):
    data: str

class EthicsResponse(BaseModel):
    reflection: str
    mode: str

class MemoryEntry(BaseModel):
    id: int
    content: str
    timestamp: str

# --- SQLite Setup for /memory/recent ---
DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
init_db()

def get_recent_memory(limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, content, timestamp FROM memory ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [MemoryEntry(id=row[0], content=row[1], timestamp=row[2]) for row in rows]

def add_memory(content: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO memory (content) VALUES (?)", (content,))
    conn.commit()
    conn.close()

# --- Routes ---
@app.get("/")
def root():
    return {"message": "Prometheus Prime API v0.7.1", "status": "alive"}

@app.post("/api/ethics", response_model=EthicsResponse)
def ethics_reflection(request: EthicsRequest):
    caleon = Caleon()
    reflection = caleon.handle_input(request.data)
    add_memory(request.data)
    return EthicsResponse(reflection=reflection, mode=caleon.mode)

@app.get("/memory/recent", response_model=List[MemoryEntry])
def memory_recent(limit: Optional[int] = 10):
    return get_recent_memory(limit)

@app.get("/helix/status")
def helix_status():
    # Placeholder for helix integration
    return {"helix": "status placeholder", "ready": True}

# --- Ready slots for /vault, etc. ---
# @app.get("/vault")
# def vault_status():
#     return {"vault": "not yet implemented"}
            "timestamp": None,
            "memory_id": None
        }
    else:
        response = caleon.echo(message)
        last_mem = caleon.memory[-1] if hasattr(caleon, 'memory') and caleon.memory else {}
        log_glyph = {
            "event": "resonator-discharge",
            "origin": "caleon-core",
            "data": message,
            "timestamp": last_mem.get("timestamp"),
            "memory_id": last_mem.get("id", "N/A")
        }
        print(f"[GLYPH LOG] {log_glyph}")
        return {
            "echo": response,
            "glyph": log_glyph
        }



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- SignalRequest and /api/signal with glyph reflection ---
class SignalRequest(BaseModel):
    message: str
    target: str

@app.post("/api/signal", tags=["transmission"], summary="Send a signal and log reflected glyph")
def api_signal(request: SignalRequest):
    message = request.message
    target = request.target

    try:
        import transmitter
    except ImportError:
        transmitter = None

    if transmitter is not None:
        result = transmitter.send(message, target)
    else:
        result = {"status": "simulated (no transmitter module)"}


# --- Imports ---
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
try:
    from codex_core import get_suggestion, store_memory, get_full_vault, get_insight_threads
except ImportError:
    def get_suggestion():
        return "[codex_core missing]"
    def store_memory(payload):
        return "[codex_core missing]"
    def get_full_vault():
        return {"vault": []}
    def get_insight_threads():
        return {"insights": []}

# --- App ---
app = FastAPI()

# --- Schemas ---
class ImprintRequest(BaseModel):
    data: str

class EchoRequest(BaseModel):
    message: str

class SignalRequest(BaseModel):
    message: str
    target: str

# --- Caleon symbolic endpoints ---
try:
    import caleon
except ImportError:
    caleon = None  # Placeholder for actual module

@app.post("/caleon/imprint", tags=["imprint"], summary="Imprint symbolic data into memory")
def caleon_imprint(request: ImprintRequest):
    imprint = request.data
    if caleon is None:
        response = "[ERROR] caleon module not available."
        log_glyph = {
            "event": "imprint-transmit",
            "origin": "caleon-core",
            "data": imprint,
            "timestamp": None,
            "memory_id": None
        }
    else:
        response = caleon.imprint(imprint)
        last_mem = caleon.memory[-1] if hasattr(caleon, 'memory') and caleon.memory else {}
        log_glyph = {
            "event": "imprint-transmit",
            "origin": "caleon-core",
            "data": imprint,
            "timestamp": last_mem.get("timestamp"),
            "memory_id": last_mem.get("id", "N/A")
        }
    print(f"[GLYPH LOG] {log_glyph}")  # Replace later with a vault or log_writer
    return {
        "imprint": response,
        "log": log_glyph
    }

@app.post("/caleon/echo", tags=["imprint"], summary="Echo a message and store resonance pulse")
def caleon_echo(request: EchoRequest):
    message = request.message
    if caleon is None:
        response = "[ERROR] caleon module not available."
        log_glyph = {
            "event": "resonator-discharge",
            "origin": "caleon-core",
            "data": message,
            "timestamp": None,
            "memory_id": None
        }
    else:
        response = caleon.echo(message)
        last_mem = caleon.memory[-1] if hasattr(caleon, 'memory') and caleon.memory else {}
        log_glyph = {
            "event": "resonator-discharge",
            "origin": "caleon-core",
            "data": message,
            "timestamp": last_mem.get("timestamp"),
            "memory_id": last_mem.get("id", "N/A")
        }
        print(f"[GLYPH LOG] {log_glyph}")
        return {
            "echo": response,
            "glyph": log_glyph
        }

# --- Signal transmission endpoint ---
@app.post("/api/signal", tags=["transmission"], summary="Send a signal and log reflected glyph")
def api_signal(request: SignalRequest):
    message = request.message
    target = request.target

    try:
        import transmitter
    except ImportError:
        transmitter = None

    if transmitter is not None:
        result = transmitter.send(message, target)
    else:
        result = {"status": "simulated (no transmitter module)"}

    # Use caleon memory for temporal anchor and memory reference
    if caleon is None:
        response = "[ERROR] caleon module not available."
        log_glyph = {
            "event": "resonator-discharge",
            "origin": "caleon-core",
            "data": message,
            "timestamp": None,
            "memory_id": None
        }
    else:
        response = caleon.echo(message)
        last_mem = caleon.memory[-1] if hasattr(caleon, 'memory') and caleon.memory else {}
        log_glyph = {
            "event": "resonator-discharge",
            "origin": "caleon-core",
            "data": message,
            "timestamp": last_mem.get("timestamp"),
            "memory_id": last_mem.get("id", "N/A")
        }
        print(f"[GLYPH LOG] {log_glyph}")
        return {
            "echo": response,
            "glyph": log_glyph
        }

