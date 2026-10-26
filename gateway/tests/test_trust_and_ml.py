"""
Unit & Integration Tests for Sensor-Trust Engine, Isolation Forest, and Physical Domain Rules (Phase 5 Verification).

Run with:
    .\\.venv\\Scripts\\python.exe -m unittest discover -s gateway/tests -p "test_*.py"
"""

import os
import sys
import time
import unittest

# Set TESTING environment variable before importing app
os.environ["TESTING"] = "true"

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from gateway.src.trust_engine.trust_scorer import SensorTrustEngine
from gateway.src.ml_engine.isolation_forest import IsolationForestAnomalyDetector
from gateway.src.ml_engine.physical_rules import PhysicalDomainRulesEngine
from backend.app.main import app
from backend.app.core.database import init_db, SessionLocal
from backend.app.models.db_models import TelemetryLogModel


class TestTrustAndMlEngines(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.trust_engine = SensorTrustEngine()
        cls.ml_engine = IsolationForestAnomalyDetector()
        cls.rules_engine = PhysicalDomainRulesEngine()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_sensor_trust_out_of_range(self):
        """Verify out-of-range sensor value drops trust score to 0.0."""
        score, status = self.trust_engine.evaluate_sensor_trust("node_01", "temperature_c", 150.0, time.time())
        self.assertEqual(score, 0.0)
        self.assertEqual(status, "OUT_OF_RANGE")

    def test_sensor_trust_flatline(self):
        """Verify stuck sensor reading triggers FLATLINE flag."""
        node_id = "node_flat_01"
        now = time.time()
        
        # Feed identical readings 10 times
        for _ in range(10):
            score, status = self.trust_engine.evaluate_sensor_trust(node_id, "temperature_c", 25.0, now)

        self.assertEqual(score, 0.1)
        self.assertEqual(status, "FLATLINE")

    def test_sensor_trust_unrealistic_drift(self):
        """Verify sudden unrealistic jump triggers DRIFT flag."""
        node_id = "node_drift_01"
        now = time.time()
        
        # Feed normal sequence then a sudden massive jump (+20°C in 1 sec)
        self.trust_engine.evaluate_sensor_trust(node_id, "temperature_c", 24.0, now)
        self.trust_engine.evaluate_sensor_trust(node_id, "temperature_c", 24.2, now + 1)
        self.trust_engine.evaluate_sensor_trust(node_id, "temperature_c", 24.3, now + 2)
        score, status = self.trust_engine.evaluate_sensor_trust(node_id, "temperature_c", 45.0, now + 3)

        self.assertEqual(score, 0.2)
        self.assertEqual(status, "DRIFT")

    def test_isolation_forest_prediction(self):
        """Verify Isolation Forest distinguishes normal telemetry from extreme anomalies."""
        normal_metrics = {
            "temperature_c": 24.0,
            "humidity_pct": 50.0,
            "current_amps": 3.5,
            "vibration_g": 0.02,
            "air_quality_index": 35.0
        }
        score_normal = self.ml_engine.predict_anomaly_score(normal_metrics)
        self.assertLessEqual(score_normal, 0.5)

        anomalous_metrics = {
            "temperature_c": 75.0,
            "humidity_pct": 10.0,
            "current_amps": 28.5,
            "vibration_g": 1.2,
            "air_quality_index": 350.0
        }
        score_anom = self.ml_engine.predict_anomaly_score(anomalous_metrics)
        self.assertGreaterEqual(score_anom, 0.5)

    def test_physical_domain_rules(self):
        """Verify physical constraint rule evaluation for water leak & phantom thermal spike."""
        metrics_leak = {
            "temperature_c": 25.0,
            "current_amps": 4.0,
            "air_quality_index": 40.0,
            "water_leak_detected": True,
            "vibration_g": 0.02
        }
        hw_status = {"relay_1_closed": True}

        rule_score, violations = self.rules_engine.evaluate_rules(metrics_leak, hw_status)
        self.assertEqual(rule_score, 1.0)
        self.assertTrue(any("Water leak" in v for v in violations))

    def test_trust_api_endpoints(self):
        """Verify API GET /api/v1/trust/scores/{node_id} and /anomaly-check/{node_id}."""
        # Insert a dummy record first
        log = TelemetryLogModel(
            node_id="test_trust_node",
            temperature_c=25.0,
            humidity_pct=50.0,
            current_amps=3.5,
            vibration_g=0.02,
            air_quality_index=35.0,
            water_leak_detected=False
        )
        self.db.add(log)
        self.db.commit()

        # Call trust scores endpoint
        res_trust = self.client.get("/api/v1/trust/scores/test_trust_node")
        self.assertEqual(res_trust.status_code, 200)
        self.assertIn("overall_trust", res_trust.json())

        # Call anomaly check endpoint
        res_anom = self.client.get("/api/v1/trust/anomaly-check/test_trust_node")
        self.assertEqual(res_anom.status_code, 200)
        self.assertIn("ml_isolation_forest_score", res_anom.json())


if __name__ == "__main__":
    unittest.main()
