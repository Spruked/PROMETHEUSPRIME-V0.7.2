from fastapi import FastAPI
from fastapi.responses import JSONResponse
import random
import threading
import time

app = FastAPI()

STATES = [
    "Dormant", "Imprint-Ready", "Active", "Loop-Charged", "Resonance-Calibrating",
    "Vault-Syncing", "Ethical-Lock", "Module-Isolated", "Legacy-Surge", "Loop-Reflective"
]

@app.get("/state")
def get_state():
    """Endpoint to get the current state."""
    current_state = random.choice(STATES)
    return JSONResponse(content={"state": current_state})

def loop_monitor():
    """Background task to monitor and update state."""
    while True:
        current_state = random.choice(STATES)
        print(f"State updated: {current_state}")
        time.sleep(3)

if __name__ == "__main__":
    t = threading.Thread(target=loop_monitor)
    t.daemon = True
    t.start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5050)
