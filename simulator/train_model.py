"""
Script to train and save Isolation Forest model artifact.
"""

from gateway.src.ml_engine.isolation_forest import isolation_forest_engine

print("Isolation Forest trained status:", isolation_forest_engine.is_trained)
print("Model saved to:", isolation_forest_engine.model_path)
