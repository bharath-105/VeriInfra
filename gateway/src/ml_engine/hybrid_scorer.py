"""
Hybrid Anomaly Scorer for VeriInfra.

Formulates and evaluates the Hybrid Anomaly Scoring Equation:
    S_hybrid = w1 * S_ML_masked + w2 * S_rule + w3 * S_causal + w4 * (1 - S_trust)

Key Innovation: Sensor-Trust masking suppresses false-positive emergency shutdowns
caused by faulty, drifting, or flatlining physical sensors.
"""

import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("HybridAnomalyScorer")


class HybridAnomalyScorer:
    """
    Combines Machine Learning scores, Physical Domain Rules, Causal Consistency, 
    and Sensor-Trust Index into a single unified decision metric.
    """

    def __init__(
        self,
        weight_ml: float = 0.40,
        weight_rule: float = 0.40,
        weight_causal: float = 0.10,
        weight_trust: float = 0.10,
        trip_threshold: float = 0.70
    ):
        self.w1 = weight_ml
        self.w2 = weight_rule
        self.w3 = weight_causal
        self.w4 = weight_trust
        self.trip_threshold = trip_threshold

    def calculate_causal_inconsistency(self, metrics: Dict[str, Any], trust_score: float) -> float:
        """
        Evaluate cross-sensor causal inconsistency score S_causal.
        
        Example: Temperature is rising rapidly, but Current = 0A and Vibration = 0g.
        If trust is high, this indicates external environmental hazard (fire / HVAC failure).
        """
        temp = metrics.get("temperature_c", 24.0)
        curr = metrics.get("current_amps", 0.0)
        vib = metrics.get("vibration_g", 0.02)

        # Causal inconsistency: Temp > 45C without any current load or vibration
        if temp > 45.0 and curr < 0.5 and vib < 0.05:
            return 0.85
        
        # Causal inconsistency: Vibration > 0.5g without current load (e.g. external structural shake)
        if vib > 0.5 and curr < 0.2:
            return 0.70

        return 0.0

    def compute_hybrid_score(
        self,
        metrics: Dict[str, Any],
        hardware_status: Dict[str, Any],
        s_ml: float,
        s_rule: float,
        s_trust: float
    ) -> Dict[str, Any]:
        """
        Calculate complete Hybrid Score breakdown with Sensor-Trust masking.
        
        Returns:
            {
                "s_hybrid": float,
                "s_ml_raw": float,
                "s_ml_masked": float,
                "s_rule": float,
                "s_causal": float,
                "s_trust": float,
                "should_trip_relay": bool,
                "system_mode": str  # NORMAL, ADVISORY, HIGH_RISK, EMERGENCY_STOP
            }
        """
        # 1. Compute Cross-Sensor Causal Inconsistency (S_causal)
        s_causal = self.calculate_causal_inconsistency(metrics, s_trust)

        # 2. Apply SENSOR-TRUST MASKING INNOVATION:
        # If sensor trust is low (< 0.4), discount ML score contribution
        # to prevent a single faulty sensor from triggering false emergency trips!
        if s_trust < 0.4:
            s_ml_masked = s_ml * s_trust
            logger.info(f"SENSOR-TRUST MASKING APPLIED: S_trust={s_trust:.2f} -> S_ml reduced from {s_ml:.2f} to {s_ml_masked:.2f}")
        else:
            s_ml_masked = s_ml

        # 3. Calculate S_hybrid using weighted equation
        # S_hybrid = w1 * S_ml_masked + w2 * S_rule + w3 * S_causal + w4 * (1 - S_trust)
        s_hybrid = (self.w1 * s_ml_masked) + (self.w2 * s_rule) + (self.w3 * s_causal) + (self.w4 * (1.0 - s_trust))
        s_hybrid = round(min(1.0, max(0.0, s_hybrid)), 3)

        # 4. Determine Global Emergency Mode Decision
        should_trip_relay = False
        if s_hybrid >= self.trip_threshold or s_rule >= 1.0:
            system_mode = "EMERGENCY_STOP"
            should_trip_relay = True
        elif s_hybrid >= 0.50 or s_rule >= 0.8:
            system_mode = "HIGH_RISK"
        elif s_hybrid >= 0.35 or s_trust < 0.5:
            system_mode = "ADVISORY"
        else:
            system_mode = "NORMAL"

        return {
            "s_hybrid": s_hybrid,
            "s_ml_raw": round(s_ml, 3),
            "s_ml_masked": round(s_ml_masked, 3),
            "s_rule": round(s_rule, 3),
            "s_causal": round(s_causal, 3),
            "s_trust": round(s_trust, 3),
            "should_trip_relay": should_trip_relay,
            "system_mode": system_mode
        }


# Global Hybrid Scorer Instance
hybrid_scorer_engine = HybridAnomalyScorer()
