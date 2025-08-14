# ============================================================================
# CALI: Prometheus Prime Backend — app.py
# ============================================================================

# --- Conceptual config.py (In a real project, this would be a separate file) ---
# For demonstration, we'll define these directly in app.py or load from env vars
import os

class Config:
    # Basic App Config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_very_secret_key_for_dev') # IMPORTANT: Change for production!
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')

    # Paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    VAULT_DIR = os.path.join(BASE_DIR, 'data', 'vault_files')
    DATABASE_PATH = os.path.join(BASE_DIR, 'legacy_vault.db')
    ETHICS_CONFIG_PATH = os.path.join(BASE_DIR, 'cali', 'config', 'ethics.yaml')
    LOG_FILE_PATH = os.path.join(BASE_DIR, 'logs', 'app.log') # New log file path

    # Logging Config
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper() # Default log level
    LOG_MAX_BYTES = 10 * 1024 * 1024 # 10 MB
    LOG_BACKUP_COUNT = 5 # Keep 5 backup log files

# Ensure VAULT_DIR and LOG_DIR exist
os.makedirs(Config.VAULT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(Config.LOG_FILE_PATH), exist_ok=True)

# --- Force module visibility ---
import sys
# sys.path.append(os.path.abspath(os.path.dirname(__file__))) # This is often handled by proper project structure or virtual envs

# --- Imports: Standard & Flask ---
import uuid
import logging
from logging.handlers import RotatingFileHandler
import yaml
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# --- Imports: Custom Modules ---
from routes.glyphfeed import glyphfeed_bp
from cali.sandbox import sanitize_input, SandboxError
from cali.vault.storage.cali_vault_storage import load_memory_vault, save_memory_vault # VAULT_DIR is now from Config
from core.trust_glyph_verifier import TrustGlyphVerifier
from core.helix_echo_core import HelixEchoCore
# For MemoryStore, we'll handle its import below more robustly

# ============================================================================
# Initialization & Logging Setup
# ============================================================================


app = FastAPI(title="Prometheus Prime Backend", version="0.7.2")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# --- Advanced Logging Setup ---
# Get the root logger
root_logger = logging.getLogger()
root_logger.setLevel(Config.LOG_LEVEL) # Set overall log level

# Create a formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# Create a rotating file handler
file_handler = RotatingFileHandler(
    Config.LOG_FILE_PATH,
    maxBytes=Config.LOG_MAX_BYTES,
    backupCount=Config.LOG_BACKUP_COUNT
)
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)



# Get a dedicated logger for CALI components
cali_logger = logging.getLogger("CALI")
cali_logger.setLevel(Config.LOG_LEVEL) # Ensure it respects the overall level

cali_logger.info("Prometheus Prime Backend Starting...")



# ============================================================================
# Ethics Framework Loader
# ============================================================================

ethics = {}
try:
    with open(app.config['ETHICS_CONFIG_PATH'], 'r', encoding='utf-8') as f:
        ethics = yaml.safe_load(f)
        cali_logger.info("✅ Ethical framework loaded.")
except FileNotFoundError:
    cali_logger.error(f"❌ Ethics configuration file not found at {app.config['ETHICS_CONFIG_PATH']}. Using empty ethics.")
except Exception as e:
    cali_logger.error(f"❌ Failed to load ethics.yaml: {e}")

# ============================================================================
# SQLite Vault DB Utilities (Improved with app context)
# ============================================================================


# Dependency for DB connection
def get_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS legacy_vault (
        vault_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        trigger_keywords TEXT,
        delivery_mode TEXT,
        unlock_condition TEXT,
        is_active INTEGER,
        created_at TEXT,
        category TEXT
    )''')
    conn.commit()
    conn.close()
    cali_logger.info("✅ Legacy Vault database schema checked/initialized.")

# ============================================================================
# Root Endpoint
# ============================================================================


@app.get("/")
def index():
    return {"message": "Prometheus Prime backend online."}

# ============================================================================
# Vault Routes (DB + File-Based)
# ============================================================================


from pydantic import BaseModel

class PromptRequest(BaseModel):
    title: Optional[str] = 'User Prompt'
    description: Optional[str] = ''
    keywords: Optional[List[str]] = []
    category: Optional[str] = 'tasks'

@app.post('/prompt')
def handle_prompt(prompt: PromptRequest, db=Depends(get_db)):
    try:
        title = sanitize_input(prompt.title)
        description = sanitize_input(prompt.description)
        keywords = [sanitize_input(k) for k in prompt.keywords]
        keywords_str = ",".join(keywords)
        category = sanitize_input(prompt.category)
        vault_id = str(uuid.uuid4())

        db.execute('''
            INSERT INTO legacy_vault (
                vault_id, title, description, trigger_keywords, delivery_mode,
                unlock_condition, is_active, created_at, category
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            vault_id,
            title,
            description,
            keywords_str,
            "manual",
            "none",
            1,
            datetime.now().isoformat(),
            category
        ))
        db.commit()
        cali_logger.info(f"💾 Vault entry {vault_id} added to SQLite DB.")
    except SandboxError as e:
        cali_logger.error(f"Input sanitization error for /prompt: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
    except Exception as e:
        cali_logger.error(f"❌ DB error on /prompt: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database error")

    try:
        save_memory_vault(vault_id, {
            "vault_id": vault_id, "title": title,
            "description": description, "keywords": keywords,
            "category": category, "created_at": datetime.now().isoformat()
        })
        cali_logger.info(f"📁 Vault entry {vault_id} saved to file system.")
    except Exception as e:
        cali_logger.error(f"❌ File system vault save error for {vault_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="File system save error, DB may be updated.")

    return {"status": "created", "vault_id": vault_id}


@app.get('/vault-files')
def list_vault_files():
    try:
        files = [f.replace(".json", "") for f in os.listdir(Config.VAULT_DIR) if f.endswith(".json")]
        return {"vault_files": files}
    except FileNotFoundError:
        cali_logger.warning(f"Vault directory not found: {Config.VAULT_DIR}")
        return {"vault_files": []}
    except Exception as e:
        cali_logger.error(f"❌ Error listing vault files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Server error listing files")


@app.get('/vault-files/{vault_id}')
def view_vault_file(vault_id: str):
    vault = load_memory_vault(vault_id)
    if not vault:
        cali_logger.warning(f"Vault {vault_id} not found.")
        raise HTTPException(status_code=404, detail="Vault not found")
    return vault


@app.get('/vault-files/{vault_id}/download')
def download_vault_file(vault_id: str):
    path = os.path.join(Config.VAULT_DIR, f"{vault_id}.json")
    if not os.path.exists(path):
        cali_logger.warning(f"Vault file {vault_id}.json not found for download.")
        raise HTTPException(status_code=404, detail="File not found")
    try:
        return FileResponse(path, filename=f"{vault_id}.json", media_type="application/json")
    except Exception as e:
        cali_logger.error(f"❌ Error downloading vault file {vault_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to download file")


@app.get('/reconcile')
def reconcile_vault():
    cali_logger.info("Initiating vault reconciliation.")
    return {"status": "success", "message": "Reconciliation completed"}

# ============================================================================
# Helix Echo Integration
# ============================================================================

HELIX_AVAILABLE = False
helix_engine = None

try:
    helix_engine = HelixEchoCore(ethics)
    HELIX_AVAILABLE = True
    cali_logger.info("🧠 HelixEchoCore integrated successfully.")
except Exception as e:
    cali_logger.warning(f"⚠️ HelixEchoCore unavailable: {e}", exc_info=True)

@app.route("/helix/process", methods=["POST"])
def helix_process():
    if not HELIX_AVAILABLE:
        cali_logger.warning("Attempted Helix process, but Helix is unavailable.")
    from fastapi.responses import JSONResponse
    return JSONResponse(content={"error": "Helix unavailable"}, status_code=503)
    try:
        data = request.get_json()
        if not data or "input" not in data:
            cali_logger.warning("No input provided for Helix process.")
            return JSONResponse(content={"error": "Input required"}, status_code=400)
        
        # Sanitize input before passing to HelixEchoCore
        processed_input = sanitize_input(data["input"])
        if helix_engine is None:
            cali_logger.error("HelixEchoCore is not initialized.")
            return JSONResponse(content={"error": "HelixEchoCore not initialized"}, status_code=503)
        result = helix_engine.echo(processed_input)
        cali_logger.info("Helix Echo processing successful.")
    return JSONResponse(content={"status": "success", "helix_response": result})
    except SandboxError as e:
        cali_logger.error(f"Input sanitization error for Helix process: {e}")
    return JSONResponse(content={"error": f"Invalid input: {e}"}, status_code=400)
    except Exception as e:
        cali_logger.error(f"❌ Helix error during processing: {e}", exc_info=True)
    return JSONResponse(content={"error": str(e)}, status_code=500)

@app.route("/helix/status")
def helix_status():
    status_msg = "ok" if HELIX_AVAILABLE else "not initialized"
    cali_logger.debug(f"Helix status requested: {status_msg}")
    return JSONResponse(content={
        "available": HELIX_AVAILABLE,
        "status": status_msg
    })

# ============================================================================
# Mirror + Codex Integration (Caleon)
# ============================================================================

from core.mirror.mirror import Caleon

caleon = None # Initialize as None
try:
    caleon = Caleon()
    cali_logger.info("✨ Caleon (Mirror + Codex) integrated successfully.")
except Exception as e:
    cali_logger.warning(f"⚠️ Caleon (Mirror + Codex) unavailable: {e}", exc_info=True)

@app.route("/api/reflect", methods=["POST"])
def reflect_input():
    if not caleon:
        cali_logger.warning("Attempted Caleon reflection, but Caleon is unavailable.")
    return JSONResponse(content={"error": "Caleon not ready"}, status_code=503)
    try:
        data = request.get_json()
        user_input = sanitize_input(data.get("input", ""))
        if not user_input:
            cali_logger.warning("No input provided for Caleon reflection.")
            return JSONResponse(content={"error": "Input required"}, status_code=400)

        result = caleon.handle_input(user_input)
        cali_logger.info("Caleon reflection successful.")
    return JSONResponse(content={"response": result})
    except SandboxError as e:
        cali_logger.error(f"Input sanitization error for Caleon reflection: {e}")
    return JSONResponse(content={"error": f"Invalid input: {e}"}, status_code=400)
    except Exception as e:
        cali_logger.error(f"❌ Caleon reflection error: {e}", exc_info=True)
    return JSONResponse(content={"error": str(e)}, status_code=500)

@app.route("/reflect", methods=["GET", "POST"])
def reflect():
    if not caleon:
        cali_logger.warning("Attempted Caleon reflection, but Caleon is unavailable.")
    return JSONResponse(content={'error': 'Caleon not ready'}, status_code=503)
    try:
        input_text = request.values.get("input")
        if not input_text:
            cali_logger.warning("No input provided for Caleon reflection (GET/POST).")
            return JSONResponse(content={'error': 'No input provided'}, status_code=400)
        
        sanitized_input_text = sanitize_input(input_text)
        output = caleon.handle_input(sanitized_input_text)
        cali_logger.info("Caleon reflection (GET/POST) successful.")
    return JSONResponse(content={'input': input_text, 'output': output})
    except SandboxError as e:
        cali_logger.error(f"Input sanitization error for Caleon reflection (GET/POST): {e}")
    return JSONResponse(content={"error": f"Invalid input: {e}"}, status_code=400)
    except Exception as e:
        cali_logger.error(f"❌ Caleon reflection (GET/POST) error: {e}", exc_info=True)
    return JSONResponse(content={"error": str(e)}, status_code=500)

# ============================================================================
# Memory Store API (SQLite)
# ============================================================================

memory_store = None # Initialize as None
try:
    from cali.memory.memory_store import MemoryStore
    memory_store = MemoryStore() # Initialize without db_path
    cali_logger.info("📚 MemoryStore initialized successfully.")
except ModuleNotFoundError:
    cali_logger.error("❌ MemoryStore module not found. Please ensure 'cali/memory/memory_store.py' exists and is accessible.", exc_info=True)
    # Re-adding sys.path.append for MemoryStore specifically if it's in a non-standard path
    # This might be needed if cali.memory isn't directly importable
    # sys.path.append(os.path.abspath(os.path.join(Config.BASE_DIR, 'cali', 'memory')))
    # try:
    #     from memory_store import MemoryStore
    #     memory_store = MemoryStore(db_path=app.config['DATABASE_PATH'])
    #     cali_logger.info("📚 MemoryStore initialized successfully after path adjustment.")
    # except Exception as e:
    #     cali_logger.error(f"❌ MemoryStore still unavailable after path adjustment: {e}", exc_info=True)
except Exception as e:
    cali_logger.error(f"❌ Failed to initialize MemoryStore: {e}", exc_info=True)


@app.route('/memory/add', methods=['POST'])
def memory_add():
    if not memory_store:
        cali_logger.warning("Attempted memory add, but MemoryStore is unavailable.")
    return JSONResponse(content={'error': 'MemoryStore unavailable'}, status_code=503)
    data = request.get_json() or {}
    if not data.get('text'):
        cali_logger.warning("No text provided for memory add.")
    return JSONResponse(content={'error': 'No text provided'}, status_code=400)
    try:
        # Sanitize all inputs
        text = sanitize_input(data['text'])
        emotion = sanitize_input(data.get('emotion', ''))
        context = sanitize_input(data.get('context', ''))
        tags_raw = data.get('tags', [])
        tags = [sanitize_input(t) for t in tags_raw] if isinstance(tags_raw, list) else sanitize_input(tags_raw).split(',')
        usage_score = float(data.get('usage_score', 1.0)) # Convert to float

        entry_id = memory_store.add_entry(
            text, emotion, context,
            ",".join(tags), usage_score # Store tags as comma-separated string in DB
        )
        cali_logger.info(f"Memory entry {entry_id} added.")
    return JSONResponse(content={'status': 'created', 'entry_id': entry_id})
    except SandboxError as e:
        cali_logger.error(f"Input sanitization error for memory add: {e}")
    return JSONResponse(content={"error": f"Invalid input: {e}"}, status_code=400)
    except Exception as e:
        cali_logger.error(f"❌ Error adding memory entry: {e}", exc_info=True)
    return JSONResponse(content={'error': 'Failed to add memory entry'}, status_code=500)

@app.route('/memory/get/<int:entry_id>', methods=['GET'])
def memory_get(entry_id: int):
    if not memory_store:
        cali_logger.warning("Attempted memory get, but MemoryStore is unavailable.")
    return JSONResponse(content={'error': 'MemoryStore unavailable'}, status_code=503)
    try:
        row = memory_store.get_entry(entry_id)
        if not row:
            cali_logger.warning(f"Memory entry {entry_id} not found.")
            abort(404, description="Not found")
        keys = ['id', 'text', 'emotion', 'context', 'tags', 'created_at', 'usage_score']
        # Convert tags string back to list for frontend if needed, or keep as string
        result = dict(zip(keys, row))
        if 'tags' in result and result['tags'] is not None:
            result['tags'] = result['tags'].split(',') # Convert tags string to list
        cali_logger.info(f"Memory entry {entry_id} retrieved.")
    return JSONResponse(content=result)
    except Exception as e:
        cali_logger.error(f"❌ Error getting memory entry {entry_id}: {e}", exc_info=True)
    return JSONResponse(content={'error': 'Failed to retrieve memory entry'}, status_code=500)

@app.route('/memory/search', methods=['GET'])
def memory_search():
    if not memory_store:
        cali_logger.warning("Attempted memory search, but MemoryStore is unavailable.")
    return JSONResponse(content={'error': 'MemoryStore unavailable'}, status_code=503)
    q = request.args.get('q')
    if not q:
        cali_logger.warning("No query provided for memory search.")
    return JSONResponse(content={'error': 'No query provided'}, status_code=400)
    try:
        sanitized_q = sanitize_input(q)
        rows = memory_store.search_text(sanitized_q)
        keys = ['id', 'text', 'emotion', 'context', 'tags', 'created_at', 'usage_score']
        results = []
        for row in rows:
            item = dict(zip(keys, row))
            if 'tags' in item and item['tags'] is not None:
                item['tags'] = item['tags'].split(',')
            results.append(item)
        cali_logger.info(f"Memory search for '{q}' returned {len(results)} results.")
    return JSONResponse(content=results)
    except SandboxError as e:
        cali_logger.error(f"Input sanitization error for memory search: {e}")
    return JSONResponse(content={"error": f"Invalid query: {e}"}, status_code=400)
    except Exception as e:
        cali_logger.error(f"❌ Error searching memory: {e}", exc_info=True)
    return JSONResponse(content={'error': 'Failed to search memory'}, status_code=500)

@app.route('/memory/tag/<tag>', methods=['GET'])
def memory_tag_search(tag: str):
    if not memory_store:
        cali_logger.warning("Attempted memory tag search, but MemoryStore is unavailable.")
    return JSONResponse(content={'error': 'MemoryStore unavailable'}, status_code=503)
    try:
        sanitized_tag = sanitize_input(tag)
        rows = memory_store.search_by_tag(sanitized_tag)
        keys = ['id', 'text', 'emotion', 'context', 'tags', 'created_at', 'usage_score']
        results = []
        for row in rows:
            item = dict(zip(keys, row))
            if 'tags' in item and item['tags'] is not None:
                item['tags'] = item['tags'].split(',')
            results.append(item)
        cali_logger.info(f"Memory tag search for '{tag}' returned {len(results)} results.")
        return jsonify(results)
    except SandboxError as e:
        cali_logger.error(f"Input sanitization error for memory tag search: {e}")
        return jsonify({"error": f"Invalid tag: {e}"}), 400
    except Exception as e:
        cali_logger.error(f"❌ Error searching memory by tag: {e}", exc_info=True)
        return jsonify({'error': 'Failed to search memory by tag'}), 500

@app.route('/memory/recent', methods=['GET'])
def memory_recent():
    if not memory_store:
        cali_logger.warning("Attempted memory recent, but MemoryStore is unavailable.")
        return jsonify({'error': 'MemoryStore unavailable'}), 503
    try:
        n = int(request.args.get('n', 10))
        if n <= 0:
            cali_logger.warning(f"Invalid 'n' value for recent memories: {n}")
        return JSONResponse(content={'error': 'Number of recent entries must be positive'}, status_code=400)
        rows = memory_store.search_recent(n)
        keys = ['id', 'text', 'emotion', 'context', 'tags', 'created_at', 'usage_score']
        results = []
        for row in rows:
            item = dict(zip(keys, row))
            if 'tags' in item and item['tags'] is not None:
                item['tags'] = item['tags'].split(',')
            results.append(item)
        cali_logger.info(f"Retrieved {len(results)} recent memory entries.")
    return JSONResponse(content=results)
    except ValueError:
        cali_logger.error("Invalid 'n' parameter for recent memories (not an integer).")
    return JSONResponse(content={'error': 'Invalid number of entries requested'}, status_code=400)
    except Exception as e:
        cali_logger.error(f"❌ Error retrieving recent memories: {e}", exc_info=True)
    return JSONResponse(content={'error': 'Failed to retrieve recent memory entries'}, status_code=500)

# ============================================================================
# Security Headers (Improved)
# ============================================================================


# FastAPI middleware for security headers
from starlette.middleware.base import BaseHTTPMiddleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
        cali_logger.debug("Security headers added to response.")
        return response
app.add_middleware(SecurityHeadersMiddleware)

# ============================================================================
# Run App
# ============================================================================

# Entrypoint for manual run
if __name__ == "__main__":
    init_db()
    import uvicorn
    cali_logger.info("Prometheus Prime backend is ready to serve.")
    uvicorn.run("app:app", host="0.0.0.0", port=Config.PORT, reload=True)
# ============================================================================
