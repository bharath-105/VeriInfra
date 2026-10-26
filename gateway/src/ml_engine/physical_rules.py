"""
Physical Domain Constraint Rules Engine for VeriInfra.

Computes Physical Rule Violation Score (S_rule) based on domain laws and hardware cross-checks.
"""

import logging
from typing import Dict, Any, Tuple, List

logger = logging.getLogger("PhysicalRulesEngine")


class PhysicalDomainRulesEngine:
    """
    Evaluates physical domain consistency and hazard constraints.
    """

    def evaluate_rules(self, metrics: Dict[str, Any], hardware_status: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Evaluate physical constraint rules against telemetry metrics and hardware status.
        
        Returns:
            (rule_violation_score, violated_rules_list)
            rule_violation_score ranges from 0.0 (Normal) to 1.0 (Critical Violation).
        """
        temp = metrics.get("temperature_c", 24.0)
        curr = metrics.get("current_amps", 0.0)
        aqi = metrics.get("air_quality_index", 35.0)
        water_leak = metrics.get("water_leak_detected", False)
        vib = metrics.get("vibration_g", 0.02)
        relay_1_closed = hardware_status.get("relay_1_closed", True)

        violated_rules = []
        max_severity = 0.0

        # Rule 1: Water Leak Hazard while Relay is Energized
        if water_leak and relay_1_closed:
            violated_rules.append("CRITICAL: Water leak detected while main electrical load is ENERGIZED.")
            max_severity = max(max_severity, 1.0)

        # Rule 2: Phantom Thermal Spike (High Temperature without Electrical Load)
        if temp > 50.0 and curr < 0.5:
            violated_rules.append("WARNING: Extreme temperature surge detected with 0A electrical load (External Heat Hazard).")
            max_severity = max(max_severity, 0.9)

        # Rule 3: Overcurrent Thermal Runaway (High Current + High Temp)
        if curr > 12.0 and temp > 45.0:
            violated_rules.append("CRITICAL: Simultaneous Overcurrent & Thermal Overload (Electrical Overload Runaway).")
            max_severity = max(max_severity, 0.95)

        # Rule 4: Air Quality Smoke Hazard
        if aqi > 250.0:
            violated_rules.append("WARNING: High Air Quality Index / Smoke Proxy threshold exceeded (AQI > 250).")
            max_severity = max(max_severity, 0.85)

        # Rule 5: Severe Fan/Pump Motor Mechanical Vibration
        if vib > 0.8:
            violated_rules.append("WARNING: Excessive mechanical vibration detected on motor/fan (Vibration > 0.8g).")
            max_severity = max(max_severity, 0.75)

        return round(max_severity, 3), violated_rules


# Global Physical Rules Engine Instance
physical_rules_engine = PhysicalDomainRulesEngine()
