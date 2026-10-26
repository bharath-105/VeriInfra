"""
5-State Emergency Manager & Safety Override Controller for VeriInfra.

Manages system transitions between:
    - NORMAL: Regular operational status
    - ADVISORY: Minor anomaly or sensor trust warning
    - HIGH_RISK: Multi-metric hazard elevated
    - EMERGENCY_STOP: Severe hazard -> Automatic relay trip & acoustic alarm
    - DISASTER_MODE: Total gateway / network / cascade collapse
"""

import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("EmergencyStateManager")


class EmergencyStateManager:
    """
    State machine governing global system security modes and physical actuation dispatches.
    """

    def __init__(self, default_mode: str = "NORMAL"):
        self.current_mode = default_mode
        self.last_transition_time = time.time()
        self.active_overrides = []

    def transition_state(self, new_mode: str, reason: str = "") -> bool:
        """Transition global system mode with logging audit."""
        if new_mode == self.current_mode:
            return False

        logger.warning(f"SYSTEM STATE TRANSITION: [{self.current_mode}] ===> [{new_mode}] (Reason: {reason})")
        self.current_mode = new_mode
        self.last_transition_time = time.time()
        return True

    def evaluate_system_state(
        self,
        s_hybrid: float,
        s_trust: float,
        hardware_estop_pressed: bool = False,
        network_connected: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate inputs and execute state machine transitions.
        
        Returns:
            {
                "current_mode": str,
                "should_trip_relay": bool,
                "should_sound_buzzer": bool,
                "active_overrides": List[str]
            }
        """
        overrides = []
        should_trip = False
        should_buzzer = False

        # 1. HARDWARE E-STOP DOMINANCE (Highest Priority)
        if hardware_estop_pressed:
            self.transition_state("EMERGENCY_STOP", "Physical Mushroom E-Stop Button Pressed")
            overrides.append("HARDWARE_ESTOP_ACTIVE")
            return {
                "current_mode": "EMERGENCY_STOP",
                "should_trip_relay": True,
                "should_sound_buzzer": True,
                "active_overrides": overrides
            }

        # 2. DISASTER MODE (Cloud/Gateway Collapse + Extreme Anomaly)
        if not network_connected and s_hybrid >= 0.70:
            self.transition_state("DISASTER_MODE", "Offline network disconnect during severe anomaly cascade")
            overrides.append("DISASTER_OFFLINE_PROTECTION")
            return {
                "current_mode": "DISASTER_MODE",
                "should_trip_relay": True,
                "should_sound_buzzer": True,
                "active_overrides": overrides
            }

        # 3. HYBRID SCORE DRIVEN TRANSITIONS
        if s_hybrid >= 0.70:
            self.transition_state("EMERGENCY_STOP", f"Hybrid Anomaly Score {s_hybrid:.3f} >= 0.70 threshold")
            should_trip = True
            should_buzzer = True
            overrides.append("HYBRID_AI_AUTOMATIC_TRIP")

        elif s_hybrid >= 0.50:
            self.transition_state("HIGH_RISK", f"Hybrid Anomaly Score {s_hybrid:.3f} >= 0.50 elevated risk")
            should_buzzer = True
            overrides.append("HIGH_RISK_WARNING")

        elif s_hybrid >= 0.30 or s_trust < 0.5:
            self.transition_state("ADVISORY", f"Hybrid Score {s_hybrid:.3f} or Sensor Trust {s_trust:.2f} degraded")

        else:
            self.transition_state("NORMAL", "All sensors and hybrid metrics within baseline limits")

        self.active_overrides = overrides
        return {
            "current_mode": self.current_mode,
            "should_trip_relay": should_trip,
            "should_sound_buzzer": should_buzzer,
            "active_overrides": overrides
        }


# Global Emergency Manager Instance
emergency_state_engine = EmergencyStateManager()
