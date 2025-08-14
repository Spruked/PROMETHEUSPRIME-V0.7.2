
from fastapi import FastAPI, Path, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from uuid import uuid4
from datetime import datetime

app = FastAPI(title="CALI API", description="Generational Artifact Vault", version="1.0.0")


# In-memory storage for generational lineages (replace with DB in production)
GENERATIONS = []
# In-memory storage for pet health entries (replace with DB in production)
PET_HEALTH_ENTRIES = []
# --- Generational Pet Models ---
class PetHealthEntry(BaseModel):
    lineage_id: str
    timestamp: datetime
    vitals: Dict[str, Union[int, float, str]]  # e.g., weight, heart_rate, temp, mood
    health_event: Optional[str] = None
    notes: Optional[str] = None


class SignalPayload(BaseModel):
    ritual_name: str
    timestamp: datetime
    artifact_id: str
    symbolic_color: Optional[str] = None
    emotion_trace: Optional[str] = None

# --- Generational Pet Models ---
class BondGlyph(BaseModel):
    glyph_id: str
    emotion_trace: str
    timestamp_mark: str
    visual_aura: Optional[str] = None
    custom_emotion_trace: Optional[str] = None

class ArtifactBinding(BaseModel):
    type: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None

class RitualChronicle(BaseModel):
    timestamp: str
    event_type: Optional[str] = None
    description: Optional[str] = None
    related_pet_name: Optional[str] = None

class GenerationalLineage(BaseModel):
    lineage_id: str = Field(default_factory=lambda: str(uuid4()))
    species: str
    breed: Optional[str] = None
    generation_count: int
    heritage_weight: str
    narrative_spine: Optional[str] = None
    archival_status: bool = False
    bond_glyphs: List[BondGlyph] = []
    artifact_bindings: List[ArtifactBinding] = []
    ritual_chronicle: List[RitualChronicle] = []
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

@app.post("/artifact/signal/{latitude},{longitude}", tags=["Artifact GPS"])
async def emit_artifact_signal(
    payload: SignalPayload,
    latitude: float = Path(..., description="Latitude of ritual event"),
    longitude: float = Path(..., description="Longitude of ritual event")
):
    # Simulated storage/response logic
    signal = {
        "coords": {"lat": latitude, "long": longitude},
        "payload": payload.dict(),
        "status": "logged",
        "ritual_hash": f"{payload.ritual_name[:3]}-{payload.artifact_id[-4:]}"
    }
    return signal

# --- Generational Pet Endpoints ---
@app.get("/pets/generational", response_model=List[GenerationalLineage], tags=["Generational Pets"])
async def get_generational_lineages():
    return GENERATIONS

@app.post("/pets/generational/add", response_model=GenerationalLineage, tags=["Generational Pets"])
async def add_generational_lineage(lineage: GenerationalLineage):
    GENERATIONS.append(lineage)
    return lineage

# --- Generational Health Endpoints ---
@app.post("/pets/health/add", response_model=PetHealthEntry, tags=["Generational Health"])
async def add_pet_health_entry(entry: PetHealthEntry):
    PET_HEALTH_ENTRIES.append(entry)
    return entry

@app.get("/pets/health/{lineage_id}", response_model=List[PetHealthEntry], tags=["Generational Health"])
async def get_pet_health_history(lineage_id: str):
    # Return all health entries for a given lineage, sorted by timestamp
    entries = [e for e in PET_HEALTH_ENTRIES if e.lineage_id == lineage_id]
    entries.sort(key=lambda e: e.timestamp)
    return entries

@app.get("/pets/health/alerts", response_model=List[PetHealthEntry], tags=["Generational Health"])
async def get_health_alerts():
    # Example: abnormal if heart_rate < 40 or > 180, temp < 97 or > 104, mood == 'Distressed'
    alerts = []
    for entry in PET_HEALTH_ENTRIES:
        hr = entry.vitals.get('heart_rate')
        temp = entry.vitals.get('temperature')
        mood = entry.vitals.get('mood')
        try:
            if (isinstance(hr, (int, float)) and (hr < 40 or hr > 180)) or \
               (isinstance(temp, (int, float)) and (temp < 97 or temp > 104)) or \
               (isinstance(mood, str) and mood.lower() in ['distressed', 'lethargic', 'critical']):
                alerts.append(entry)
        except Exception:
            continue
    return alerts
