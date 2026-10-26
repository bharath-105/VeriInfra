"""
Sensor-Trust Engine for VeriInfra.

Calculates Sensor-Trust Index (S_trust) to identify:
- Out-of-range sensor values
- Flatlines (stuck sensors with zero variance)
- Abnormal drift rate
- Packet loss / missing data
"""

import time
import numpy as np
import logging
from typing import Dict, Any, List, Tuple
from collections import deque

logger = logging.getLogger("SensorTrustEngine")

# Physical Range Limits for Standard Infrastructure Sensors
PHYSICAL_RANGE_LIMITS = {
    "temperature_c": (-10.0, 85.0),
    "humidity_pct": (0.0, 100.0),
    "current_amps": (0.0, 40.0),
    "vibration_g": (0.0, 5.0),
    "air_quality_index": (0.0, 500.0)
}

# Maximum Allowable Rate of Change per second
MAX_DRIFT_RATE_PER_SEC = {
    "temperature_c": 3.0,      # Max 3.0 deg per sec physical jump
    "humidity_pct": 10.0,
    "current_amps": 15.0,
    "vibration_g": 2.0,
    "air_quality_index": 100.0
}


class SensorTrustEngine:
    """
    Evaluates real-time trustworthiness of sensor readings.
    """

    def __init__(self, window_size: int = 10, flatline_variance_threshold: float = 1e-4):
        self.window_size = window_size
        self.flatline_threshold = flatline_variance_threshold
        # Stores rolling deques per node and per sensor: self.history[node_id][sensor_name] = deque(...)
        self.history: Dict[str, Dict[str, deque]] = {}
        self.last_seen_timestamps: Dict[str, float] = {}

    def _get_sensor_history(self, node_id: str, sensor_name: str) -> deque:
        if node_id not in self.history:
            self.history[node_id] = {}
        if sensor_name not in self.history[node_id]:
            self.history[node_id][sensor_name] = deque(maxlen=self.window_size)
        return self.history[node_id][sensor_name]

    def evaluate_sensor_trust(self, node_id: str, sensor_name: str, value: float, current_time: float) -> Tuple[float, str]:
        """
        Evaluate trust score (0.0 to 1.0) and status flag for a single sensor metric.
        
        Returns:
            (trust_score, status_flag)
        """
        if value is None:
            return 0.0, "MISSING"

        # 1. Range Check (T_range)
        min_val, max_val = PHYSICAL_RANGE_LIMITS.get(sensor_name, (-1000.0, 1000.0))
        if value < min_val or value > max_val:
            logger.warning(f"[{node_id}] Sensor '{sensor_name}' OUT OF RANGE: {value} (Limits: {min_val} to {max_val})")
            return 0.0, "OUT_OF_RANGE"

        history = self._get_sensor_history(node_id, sensor_name)
        history.append(value)
        self.last_seen_timestamps[node_id] = current_time

        # If history not long enough, assume OK initially
        if len(history) < 3:
            return 1.0, "OK"

        # 2. Flatline / Stuck Sensor Check (T_flat)
        # Calculate variance over sliding window
        variance = float(np.var(history))
        if variance < self.flatline_threshold:
            logger.warning(f"[{node_id}] Sensor '{sensor_name}' FLATLINE DETECTED! Variance={variance:.6f}")
            return 0.1, "FLATLINE"

        # 3. Drift Rate Check (T_drift)
        # Calculate instantaneous rate of change between last two samples
        prev_val = history[-2]
        val_diff = abs(value - prev_val)
        max_rate = MAX_DRIFT_RATE_PER_SEC.get(sensor_name, 50.0)

        if val_diff > max_rate:
            logger.warning(f"[{node_id}] Sensor '{sensor_name}' UNREALISTIC DRIFT/JUMP: diff={val_diff:.2f} > max_rate={max_rate}")
            return 0.2, "DRIFT"

        return 1.0, "OK"

    def evaluate_node_trust(self, node_id: str, metrics: Dict[str, Any], current_time: float) -> Dict[str, Any]:
        """
        Evaluate trust for all metrics on a node payload.
        
        Returns:
            {
                "overall_node_trust": float,
                "sensor_trusts": {sensor_name: {"score": float, "status": str}}
            }
        """
        sensor_trusts = {}
        scores = []

        for sensor_name in PHYSICAL_RANGE_LIMITS.keys():
            val = metrics.get(sensor_name)
            score, status = self.evaluate_sensor_trust(node_id, sensor_name, val, current_time)
            sensor_trusts[sensor_name] = {"score": score, "status": status}
            scores.append(score)

        overall_trust = float(np.min(scores)) if scores else 1.0

        return {
            "overall_node_trust": round(overall_trust, 3),
            "sensor_trusts": sensor_trusts
        }


# Global Trust Engine Instance
trust_engine_instance = SensorTrustEngine()
