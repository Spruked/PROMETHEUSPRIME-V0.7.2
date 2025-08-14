""
Cycle Tracker Module
Monitors execution times of each CALI module and detects drift or delays.
"""

import time
from typing import Dict

class CycleTracker:
    def __init__(self):
        self.timings: Dict[str, float] = {}
        self.start_times: Dict[str, float] = {}

    def start(self, module_name: str):
        self.start_times[module_name] = time.perf_counter()

    def stop(self, module_name: str) -> float:
        if module_name not in self.start_times:
            raise ValueError(f"No start time recorded for {module_name}")
        duration = time.perf_counter() - self.start_times[module_name]
        self.timings[module_name] = duration
        return duration

    def get_all_timings(self) -> Dict[str, float]:
        return self.timings

    def detect_drift(self, threshold: float = 0.25) -> Dict[str, float]:
        return {k: v for k, v in self.timings.items() if v > threshold}