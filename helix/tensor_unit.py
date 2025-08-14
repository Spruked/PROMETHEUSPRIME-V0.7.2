# helix/tensor_unit.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, List
import hashlib, json, time

# ——— Interfaces CALI already has (stubs to be wired) ———
class Vault:  # a priori, curated datasets + policies
    def is_dataset_allowed(self, dataset_id: str) -> bool: ...
    def get_policy(self, key: str, default: Any=None) -> Any: ...
    def tag_provenance(self, model_id: str, meta: Dict[str, Any]) -> None: ...

class SixthLayer:  # intuition/ethics gate
    def approve_prediction(self, context: Dict[str, Any]) -> bool: ...

class EmbodimentPolicy:
    def is_output_phrase_allowed(self, text: str) -> bool: ...

# ——— Guarded Tensor Unit ———
@dataclass
class TensorConfig:
    max_epochs: int = 5
    max_params: int = 5_000_000  # cap model size
    min_confidence: float = 0.65  # gate low‑confidence outputs
    allow_training: bool = True

class GuardedTensorUnit:
    """
    A subordinate numerical engine:
      - trains ONLY on vault‑approved data
      - writes full provenance to the vault
      - routes every output through SixthLayer + embodiment checks
    """

    def __init__(self, vault: Vault, sixth: SixthLayer, embodiment: EmbodimentPolicy, cfg: Optional[TensorConfig]=None):
        self.vault = vault
        self.sixth = sixth
        self.embodiment = embodiment
        self.cfg = cfg or TensorConfig()
        self.model = None
        self.model_id = None
        self.param_count = 0

    # —— Utilities ——
    @staticmethod
    def sha256_bytes(b: bytes) -> str:
        return hashlib.sha256(b).hexdigest()

    def _assert_allowed_dataset(self, dataset_id: str) -> None:
        if not self.vault.is_dataset_allowed(dataset_id):
            raise PermissionError(f"Dataset '{dataset_id}' not approved by vault.")

    def _cap_model_size(self, params: int) -> None:
        if params > self.cfg.max_params:
            raise MemoryError(f"Model too large ({params} > {self.cfg.max_params}).")

    # —— Public API ——
    def build(self, arch_spec: Dict[str, Any]) -> str:
        """
        Build a small TF model from an architecture spec.
        NOTE: You will wire this to actual tf.keras code in your env.
        """
        # (placeholder) compute a synthetic param count from spec:
        params = int(arch_spec.get("layers", 3)) * int(arch_spec.get("width", 256)) * 10
        self._cap_model_size(params)
        self.param_count = params
        # assign deterministic model id
        self.model_id = f"tensor-{self.sha256_bytes(json.dumps(arch_spec, sort_keys=True).encode())[:12]}"
        # record provenance
        self.vault.tag_provenance(self.model_id, {
            "ts": time.time(),
            "arch": arch_spec,
            "params": params,
            "type": "build"
        })
        # (defer: actual TF model creation)
        self.model = object()
        return self.model_id

    def train(self, dataset_id: str, *, epochs: Optional[int]=None, notes: str="") -> Dict[str, Any]:
        if not self.cfg.allow_training:
            raise RuntimeError("Training disabled by config.")
        self._assert_allowed_dataset(dataset_id)
        e = min(self.cfg.max_epochs, int(epochs or self.cfg.max_epochs))
        # (defer: actual TF fit; return mock metrics)
        metrics = {"loss": 0.42, "acc": 0.81, "epochs": e}
        self.vault.tag_provenance(self.model_id, {
            "ts": time.time(),
            "dataset_id": dataset_id,
            "metrics": metrics,
            "notes": notes,
            "type": "train"
        })
        return metrics

    def predict(self, x: Any, context: Dict[str, Any]) -> Tuple[Any, float]:
        """
        Returns (y_pred, confidence) ONLY if:
          1) confidence >= min_confidence
          2) SixthLayer approves the context
          3) Embodiment policy finds output phrasing safe (if text)
        """
        # (defer: actual TF inference; stub a result)
        y_pred, conf = {"label": "ok", "text": context.get("proposed_text", "")}, 0.78

        if conf < self.cfg.min_confidence:
            raise ValueError(f"Low confidence {conf:.2f} < {self.cfg.min_confidence:.2f}")

        approve_ctx = {
            "model_id": self.model_id,
            "conf": conf,
            "context": context
        }
        if not self.sixth.approve_prediction(approve_ctx):
            raise PermissionError("SixthLayer rejected this prediction/context.")

        if isinstance(y_pred, dict) and "text" in y_pred:
            if not self.embodiment.is_output_phrase_allowed(y_pred["text"]):
                raise PermissionError("Embodiment policy blocked anthropomorphic phrasing.")

        # provenance for each decision
        self.vault.tag_provenance(self.model_id, {
            "ts": time.time(),
            "type": "predict",
            "conf": conf,
            "context_hash": self.sha256_bytes(json.dumps(context, sort_keys=True).encode())
        })
        return y_pred, conf

    def freeze(self) -> None:
        """Lock weights; disables further training until re‑approved."""
        self.cfg.allow_training = False
        self.vault.tag_provenance(self.model_id, {"ts": time.time(), "type": "freeze"})
