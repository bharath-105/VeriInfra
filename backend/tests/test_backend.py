"""
Integration and Unit Tests for FastAPI Backend & Ingestion Buffer (Phase 3 Verification).

Run with:
    .\\.venv\\Scripts\\python.exe -m unittest discover -s backend/tests -p "test_*.py"
"""

import os
import sys
import unittest
import time
from fastapi.testclient import TestClient

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.main import app
from backend.app.core.database import init_db, SessionLocal
from backend.app.models.db_models import NodeModel, TelemetryLogModel
from gateway.src.ingestion.buffer_manager import TelemetryBufferManager


class TestBackendAndIngestion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_root_endpoint(self):
        """Test API root status response."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ONLINE")

    def test_telemetry_buffer_manager_flushing(self):
        """Test that TelemetryBufferManager queues and persists telemetry to SQLite."""
        buffer_mgr = TelemetryBufferManager(flush_interval_sec=0.5)
        
        sample_payload = {
            "timestamp": time.time(),
            "node_id": "test_node_01",
            "name": "Test Node 01",
            "location": "lab_rack_01",
            "metrics": {
                "temperature_c": 26.4,
                "humidity_pct": 48.5,
                "current_amps": 4.1,
                "vibration_g": 0.03,
                "air_quality_index": 50.0,
                "water_leak_detected": False,
                "water_flow_lpm": 0.0
            },
            "hardware_status": {
                "auto_mode_active": True,
                "physical_estop_pressed": False,
                "relay_1_closed": True,
                "relay_2_closed": False,
                "buzzer_active": False,
                "battery_pct": 100.0,
                "rssi_dbm": -55
            }
        }

        # Enqueue item and flush explicitly
        buffer_mgr.enqueue(sample_payload)
        buffer_mgr.flush_buffer()

        # Check DB persistence
        node = self.db.query(NodeModel).filter(NodeModel.node_id == "test_node_01").first()
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "Test Node 01")

        telemetry = self.db.query(TelemetryLogModel).filter(TelemetryLogModel.node_id == "test_node_01").first()
        self.assertIsNotNone(telemetry)
        self.assertEqual(telemetry.temperature_c, 26.4)

    def test_nodes_api(self):
        """Test GET /api/v1/nodes returns registered nodes."""
        response = self.client.get("/api/v1/nodes")
        self.assertEqual(response.status_code, 200)
        nodes = response.json()
        self.assertIsInstance(nodes, list)

    def test_actuation_override_api(self):
        """Test POST /api/v1/override/actuate triggers actuation action."""
        payload = {
            "node_id": "test_node_01",
            "action": "TRIP_RELAY",
            "relay_id": 1,
            "target_state": False,
            "reason": "TEST_UNIT_OVERRIDE"
        }
        response = self.client.post("/api/v1/override/actuate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["node_id"], "test_node_01")


if __name__ == "__main__":
    unittest.main()
