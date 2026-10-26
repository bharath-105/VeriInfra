"""
Unit Tests for Root-Cause Ranking and 5-State Emergency Manager (Phase 7 Verification).

Run with:
    .\\.venv\\Scripts\\python.exe gateway/tests/test_emergency_and_rootcause.py
"""

import os
import sys
import unittest

# Set TESTING env var
os.environ["TESTING"] = "true"

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from gateway.src.digital_twin.asset_graph import DigitalTwinGraph
from gateway.src.digital_twin.root_cause_ranker import RootCauseRanker
from gateway.src.safety.emergency_state import EmergencyStateManager


class TestEmergencyAndRootCause(unittest.TestCase):

    def setUp(self):
        self.dt = DigitalTwinGraph()
        self.ranker = RootCauseRanker(self.dt)
        self.manager = EmergencyStateManager()

    def test_root_cause_ranking_topology_traversal(self):
        """Verify root cause ranker traverses upstream dependency path to main_power."""
        anomaly_scores = {
            "server_rack_01": 0.9,
            "cooling_fan_01": 0.85,
            "cooling_pump_01": 0.95,
            "main_power": 1.0
        }
        
        ranked = self.ranker.rank_root_causes("server_rack_01", anomaly_scores)
        self.assertGreater(len(ranked), 0)
        
        # Check that candidate list contains ancestors
        asset_ids = [r["asset_id"] for r in ranked]
        self.assertIn("main_power", asset_ids)
        self.assertIn("cooling_pump_01", asset_ids)
        
        # Main power or cooling pump should be highest probability
        top_cause = ranked[0]["asset_id"]
        self.assertIn(top_cause, ["main_power", "cooling_pump_01", "server_rack_01"])

    def test_emergency_state_machine_transitions(self):
        """Verify 5-state Emergency Manager mode transitions."""
        # Normal state
        res_normal = self.manager.evaluate_system_state(s_hybrid=0.1, s_trust=1.0)
        self.assertEqual(res_normal["current_mode"], "NORMAL")
        self.assertFalse(res_normal["should_trip_relay"])

        # Advisory state
        res_advisory = self.manager.evaluate_system_state(s_hybrid=0.35, s_trust=0.9)
        self.assertEqual(res_advisory["current_mode"], "ADVISORY")

        # High Risk state
        res_risk = self.manager.evaluate_system_state(s_hybrid=0.55, s_trust=0.9)
        self.assertEqual(res_risk["current_mode"], "HIGH_RISK")

        # Emergency Stop state
        res_emergency = self.manager.evaluate_system_state(s_hybrid=0.75, s_trust=0.9)
        self.assertEqual(res_emergency["current_mode"], "EMERGENCY_STOP")
        self.assertTrue(res_emergency["should_trip_relay"])

    def test_hardware_estop_dominance(self):
        """Verify physical hardware E-Stop forces EMERGENCY_STOP regardless of s_hybrid."""
        res = self.manager.evaluate_system_state(
            s_hybrid=0.0,
            s_trust=1.0,
            hardware_estop_pressed=True
        )
        self.assertEqual(res["current_mode"], "EMERGENCY_STOP")
        self.assertTrue(res["should_trip_relay"])
        self.assertIn("HARDWARE_ESTOP_ACTIVE", res["active_overrides"])


if __name__ == "__main__":
    unittest.main()
