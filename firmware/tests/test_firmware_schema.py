"""
Phase 2 Verification Test: ESP32 Firmware Payload Schema & Communication Specs.

Verifies that payload contracts emitted by ESP32 firmware match gateway ingestion schemas.

Run with:
    .\\.venv\\Scripts\\python.exe -m unittest discover -s firmware/tests -p "test_*.py"
"""

import sys
import os
import unittest
import json

# Add simulator path to reuse mock payload generator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "simulator")))
from simulate_esp32_nodes import SimulatedESP32Node
from config import DEFAULT_NODES


class TestFirmwarePayloadSchema(unittest.TestCase):

    def setUp(self):
        self.node = SimulatedESP32Node(DEFAULT_NODES[0])

    def test_telemetry_payload_schema(self):
        """Verify telemetry payload contains required fields and valid data types."""
        payload = self.node.step()

        # Top-level keys
        self.assertIn("timestamp", payload)
        self.assertIn("node_id", payload)
        self.assertIn("metrics", payload)
        self.assertIn("hardware_status", payload)

        metrics = payload["metrics"]
        self.assertIsInstance(metrics["temperature_c"], float)
        self.assertIsInstance(metrics["humidity_pct"], float)
        self.assertIsInstance(metrics["current_amps"], float)
        self.assertIsInstance(metrics["vibration_g"], float)
        self.assertIsInstance(metrics["air_quality_index"], float)
        self.assertIsInstance(metrics["water_leak_detected"], bool)

        hw = payload["hardware_status"]
        self.assertIsInstance(hw["auto_mode_active"], bool)
        self.assertIsInstance(hw["physical_estop_pressed"], bool)
        self.assertIsInstance(hw["relay_1_closed"], bool)
        self.assertIsInstance(hw["relay_2_closed"], bool)

    def test_heartbeat_payload_schema(self):
        """Verify heartbeat payload contract."""
        heartbeat = self.node.build_heartbeat_payload()

        self.assertIn("timestamp", heartbeat)
        self.assertIn("node_id", heartbeat)
        self.assertIn("status", heartbeat)
        self.assertIn("uptime_sec", heartbeat)
        self.assertIn("firmware_version", heartbeat)

    def test_actuation_command_schema(self):
        """Verify actuation payload format sent from Gateway to ESP32."""
        cmd_payload = {
            "timestamp": 1773665405.000,
            "command_id": "cmd_9921",
            "target_node": "node_esp32_01",
            "action": "TRIP_RELAY",
            "relay_id": 1,
            "target_state": False,
            "reason": "HYBRID_ANOMALY_OVERRIDE"
        }

        # Test command deserialization & processing
        success = self.node.process_actuation_command(cmd_payload)
        self.assertTrue(success)
        self.assertFalse(self.node.relay_1_closed)


if __name__ == "__main__":
    unittest.main()
