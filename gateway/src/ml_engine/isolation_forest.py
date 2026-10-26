"""
Baseline ML Anomaly Detector using Scikit-Learn Isolation Forest.
"""

import os
import joblib
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger("IsolationForestML")

FEATURE_NAMES = ["temperature_c", "humidity_pct", "current_amps", "vibration_g", "air_quality_index"]
DEFAULT_MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "isolation_forest.joblib"


class IsolationForestAnomalyDetector:
    """
    Baseline ML Anomaly Detector for VeriInfra Edge Gateway.
    """

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        self.scaler = StandardScaler()
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.is_trained = False

        # Attempt to load pre-trained model if exists
        self.load_model()

        # If model does not exist yet, fit on baseline normal telemetry
        if not self.is_trained:
            self.fit_baseline_normal_data()

    def fit_baseline_normal_data(self):
        """Fit Isolation Forest on synthetic normal operating telemetry baseline."""
        logger.info("Generating synthetic normal baseline data to fit Isolation Forest...")
        np.random.seed(42)
        n_samples = 1000

        # Normal operational ranges
        temps = np.random.normal(24.0, 1.5, n_samples)
        hums = np.random.normal(50.0, 3.0, n_samples)
        currs = np.random.normal(3.5, 0.5, n_samples)
        vibs = np.random.normal(0.02, 0.005, n_samples)
        aqis = np.random.normal(35.0, 5.0, n_samples)

        X_normal = np.column_stack([temps, hums, currs, vibs, aqis])
        
        self.train(X_normal)

    def train(self, X: np.ndarray):
        """Train scaler and Isolation Forest model on feature matrix X."""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True
        logger.info(f"Isolation Forest trained successfully on {X.shape[0]} samples.")
        self.save_model()

    def predict_anomaly_score(self, metrics: Dict[str, Any]) -> float:
        """
        Compute normalized anomaly score S_ML in range [0.0, 1.0].
        
        Returns:
            0.0 = Normal behavior
            1.0 = High Anomaly
        """
        if not self.is_trained:
            return 0.0

        try:
            vector = np.array([[
                float(metrics.get("temperature_c", 24.0)),
                float(metrics.get("humidity_pct", 50.0)),
                float(metrics.get("current_amps", 3.5)),
                float(metrics.get("vibration_g", 0.02)),
                float(metrics.get("air_quality_index", 35.0))
            ]])

            vector_scaled = self.scaler.transform(vector)
            
            # IsolationForest decision_function returns negative values for anomalies
            # raw score typically ranges from -0.5 (extreme anomaly) to +0.5 (normal)
            raw_score = self.model.decision_function(vector_scaled)[0]

            # Map raw score [-0.5, +0.5] -> normalized anomaly score [1.0, 0.0]
            # Normal (0.5) -> 0.0, Anomaly (-0.5) -> 1.0
            normalized_score = np.clip((0.3 - raw_score) / 0.6, 0.0, 1.0)
            return round(float(normalized_score), 3)

        except Exception as e:
            logger.error(f"Error predicting Isolation Forest anomaly score: {e}")
            return 0.0

    def save_model(self):
        """Save model artifact to disk."""
        try:
            joblib.dump({"scaler": self.scaler, "model": self.model}, self.model_path)
            logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save model artifact: {e}")

    def load_model(self):
        """Load model artifact from disk."""
        if self.model_path.exists():
            try:
                data = joblib.load(self.model_path)
                self.scaler = data["scaler"]
                self.model = data["model"]
                self.is_trained = True
                logger.info(f"Model loaded from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load model artifact: {e}")


# Global Baseline ML Engine Instance
isolation_forest_engine = IsolationForestAnomalyDetector()
