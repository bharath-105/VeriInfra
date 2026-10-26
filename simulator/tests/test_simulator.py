"""
Unit and Integration Tests for VeriInfra ESP32 Simulator (Phase 1 Verification).

Run with:
    python -m unittest discover -s simulator/tests -p "test_*.py"
    OR
    pytest simulator/tests
"""

import os
import sys
import unittest

# Add parent directory to path so imports work smoothly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulate_esp32_nodes import SimulatedESP32Node
from config import DEFAULT_NODES


class TestESP32NodeSimulator(unittest.TestCase):

    def setUp(self):
        self.node_config = DEFAULT_NODES[0]
        self.node = SimulatedESP32Node(self.node_config)

    def test_initial_telemetry_structure(self):
        """Verify initial telemetry payload structure and metric types."""
        payload = self.node.step()
        
        self.assertEqual(payload["node_id"], "node_esp32_01")
        self.assertIn("timestamp", payload)
        self.assertIn("metrics", payload)
        self.assertIn("hardware_status", payload)

        metrics = payload["metrics"]
        self.assertIn("temperature_c", metrics)
        self.assertIn("humidity_pct", metrics)
        self.assertIn("current_amps", metrics)
        self.assertIn("vibration_g", metrics)
        self.assertIn("air_quality_index", metrics)
        self.assertIn("water_leak_detected", metrics)

        hw = payload["hardware_status"]
        self.assertTrue(hw["relay_1_closed"])
        self.assertFalse(hw["physical_estop_pressed"])

    def test_flatline_fault_injection(self):
        """Verify flatline fault injection freezes metric at specified value."""
        self.node.inject_fault("flatline", {"sensor": "temperature_c", "value": 31.4})
        
        for _ in range(5):
            payload = self.node.step()
            self.assertEqual(payload["metrics"]["temperature_c"], 31.4)

    def test_thermal_spike_fault_injection(self):
        """Verify thermal spike fault injection drives temperature upward."""
        initial_temp = self.node.step()["metrics"]["temperature_c"]
        self.node.inject_fault("thermal_spike", {"target_c": 75.0})

        # Step 5 times
        for _ in range(5):
            payload = self.node.step()

        final_temp = payload["metrics"]["temperature_c"]
        self.assertGreater(final_temp, initial_temp)

    def test_actuation_command_processing(self):
        """Verify remote actuation relay trip command handling."""
        self.assertTrue(self.node.relay_1_closed)

        # Issue trip command
        success = self.node.process_actuation_command({
            "action": "TRIP_RELAY",
            "relay_id": 1,
            "target_state": False
        })

        self.assertTrue(success)
        self.assertFalse(self.node.relay_1_closed)

    def test_estop_hardware_dominance(self):
        """Verify that physical E-Stop overrides software actuation."""
        self.node.inject_fault("estop_pressed", {})
        payload = self.node.step()

        self.assertTrue(payload["hardware_status"]["physical_estop_pressed"])
        self.assertFalse(payload["hardware_status"]["relay_1_closed"])

        # Try to send software command to close relay
        success = self.node.process_actuation_command({
            "action": "TRIP_RELAY",
            "relay_id": 1,
            "target_state": True
        })

        # Software command MUST BE REJECTED when hardware E-stop is active
        self.assertFalse(success)
        self.assertFalse(self.node.relay_1_closed)


if __name__ == "__main__":
    unittest.main()
