"""
Unit Tests for PyTorch LSTM Autoencoder and Hybrid Anomaly Scorer (Phase 6 Verification).

Run with:
    .\\.venv\\Scripts\\python.exe gateway/tests/test_lstm_and_hybrid.py
"""

import os
import sys
import unittest

# Set TESTING env var
os.environ["TESTING"] = "true"

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from gateway.src.ml_engine.hybrid_scorer import HybridAnomalyScorer
from gateway.src.ml_engine.lstm_autoencoder import LSTMAutoencoderDetector


class TestHybridScorerAndLSTM(unittest.TestCase):

    def setUp(self):
        self.scorer = HybridAnomalyScorer(trip_threshold=0.70)
        self.lstm = LSTMAutoencoderDetector(seq_len=3)

    def test_hybrid_normal_operating_state(self):
        """Verify normal telemetry produces low hybrid score and NORMAL state."""
        metrics = {"temperature_c": 24.0, "current_amps": 3.5, "vibration_g": 0.02}
        hw = {"relay_1_closed": True}
        
        result = self.scorer.compute_hybrid_score(metrics, hw, s_ml=0.1, s_rule=0.0, s_trust=1.0)
        
        self.assertLess(result["s_hybrid"], 0.35)
        self.assertEqual(result["system_mode"], "NORMAL")
        self.assertFalse(result["should_trip_relay"])

    def test_hybrid_emergency_stop_trip(self):
        """Verify severe anomaly drives S_hybrid > 0.65 triggering EMERGENCY_STOP."""
        metrics = {"temperature_c": 70.0, "current_amps": 25.0, "vibration_g": 1.1}
        hw = {"relay_1_closed": True}
        
        result = self.scorer.compute_hybrid_score(metrics, hw, s_ml=0.9, s_rule=0.95, s_trust=1.0)
        
        self.assertGreaterEqual(result["s_hybrid"], 0.65)
        self.assertEqual(result["system_mode"], "EMERGENCY_STOP")
        self.assertTrue(result["should_trip_relay"])

    def test_sensor_trust_masking_suppresses_false_shutdown(self):
        """
        KEY INNOVATION TEST:
        When a sensor flatlines or drifts (S_trust = 0.1), S_ML is masked.
        Verify that false-positive system emergency shutdown is SUPPRESSED.
        """
        metrics = {"temperature_c": 25.0, "current_amps": 3.5, "vibration_g": 0.02}
        hw = {"relay_1_closed": True}
        
        # High raw S_ml (0.8) caused by faulty sensor, but S_trust is LOW (0.1)
        result = self.scorer.compute_hybrid_score(metrics, hw, s_ml=0.8, s_rule=0.0, s_trust=0.1)
        
        # S_ml should be masked: 0.8 * 0.1 = 0.08
        self.assertEqual(result["s_ml_masked"], 0.08)
        # S_hybrid should remain below trip threshold (< 0.80)
        self.assertFalse(result["should_trip_relay"])
        self.assertNotEqual(result["system_mode"], "EMERGENCY_STOP")

    def test_lstm_sequence_reconstruction(self):
        """Verify LSTM autoencoder accepts sequence metrics buffer."""
        seq = [
            {"temperature_c": 24.0, "humidity_pct": 50.0, "current_amps": 3.5, "vibration_g": 0.02, "air_quality_index": 35.0},
            {"temperature_c": 24.1, "humidity_pct": 50.1, "current_amps": 3.5, "vibration_g": 0.02, "air_quality_index": 35.0},
            {"temperature_c": 24.2, "humidity_pct": 50.2, "current_amps": 3.6, "vibration_g": 0.02, "air_quality_index": 35.0}
        ]
        score = self.lstm.predict_reconstruction_loss(seq)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


if __name__ == "__main__":
    unittest.main()
