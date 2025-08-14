from fastapi import APIRouter, HTTPException, Request
from .helix_echo_core import HelixEchoCore, PrometheusCodex

router = APIRouter()
helix = HelixEchoCore()
codex = PrometheusCodex(helix_core=helix)
helix.prometheus_codex = codex

@router.get("/codex/pulse")
def codex_pulse():
    return {"resonance": codex.resonance_pulse()}

@router.get("/helix/state")
def helix_state():
    return {
        "emotional_state": helix.emotional_state,
        "epigenetic_memory": helix.epigenetic_memory
    }

@router.post("/helix/execute")
async def execute_helix(request: Request):
    data = await request.json()
    helix.execute(data)
    return {"status": "executed", "input": data}

@router.post("/codex/echo")
async def codex_echo(request: Request):
    data = await request.json()
    message = data.get("message", "")
    if not message:
        raise HTTPException(status_code=400, detail="Message required")
    response = codex.echo(message)
    return {"echo": response}

@router.get("/logs/consolidation")
def get_consolidation_logs():
    import os
    log_path = "logs/consolidation_log.json"
    if not os.path.exists(log_path):
        return {"logs": []}
    try:
        with open(log_path, "r") as f:
            raw = f.read()
            lines = raw.split("\n")
            lines = [line.strip() for line in lines if line.strip()]
            if not lines:
                return {"logs": []}
            return {"logs": lines[-50:]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/daemon/sanctify")
async def daemon_sanctify(request: Request):
    from .vault_sync_daemon import VaultSyncDaemon
    data = await request.json()
    changelist_id = data.get("changelist_id", "0000")
    description = data.get("description", "")
    files = data.get("files", [])

    try:
        daemon = VaultSyncDaemon()
        result = daemon.process_changelist(changelist_id, description, files)
    from fastapi.responses import JSONResponse
    return JSONResponse(content={
            "changelist_id": changelist_id,
            "result": "sanctified" if result else "rejected"
        }), 200
    except Exception as e:
    return JSONResponse(content={"error": str(e)}, status_code=500)

@codex_bp.route("/codex/query", methods=["POST"])
def codex_query():
    import requests
    data = request.get_json()
    prompt = data.get("prompt", "")

    if not prompt:
    return JSONResponse(content={"error": "Prompt is required"}, status_code=400)

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            },
            timeout=10
        )
        result = response.json().get("response", "[No response from Minstrel]")
    return JSONResponse(content={"response": result})
    except Exception as e:
    return JSONResponse(content={"error": f"Failed to connect to Minstrel: {str(e)}"}, status_code=500)

@codex_bp.route("/codex/vault", methods=["GET"])
def codex_vault_contents():
    try:
        summary = codex.seed_vault.summarize()
        entries = codex.seed_vault.entries[-50:]  # Return last 50 entries
    return JSONResponse(content={"summary": summary, "entries": entries})
    except Exception as e:
    return JSONResponse(content={"error": str(e)}, status_code=500)