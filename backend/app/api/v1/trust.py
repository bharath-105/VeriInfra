"""
FastAPI Trust & Anomaly Detection Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.db_models import TelemetryLogModel
from gateway.src.trust_engine.trust_scorer import trust_engine_instance
from gateway.src.ml_engine.isolation_forest import isolation_forest_engine
from gateway.src.ml_engine.physical_rules import physical_rules_engine

router = APIRouter()


@router.get("/scores/{node_id}")
def get_sensor_trust_scores(node_id: str, db: Session = Depends(get_db)):
    """Fetch live Sensor-Trust Index evaluation for a node."""
    log = (
        db.query(TelemetryLogModel)
        .filter(TelemetryLogModel.node_id == node_id)
        .order_by(TelemetryLogModel.timestamp.desc())
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail=f"No telemetry records found for node '{node_id}'")

    metrics = {
        "temperature_c": log.temperature_c,
        "humidity_pct": log.humidity_pct,
        "current_amps": log.current_amps,
        "vibration_g": log.vibration_g,
        "air_quality_index": log.air_quality_index
    }

    ts = log.timestamp.timestamp() if log.timestamp else 0.0
    trust_eval = trust_engine_instance.evaluate_node_trust(node_id, metrics, ts)
    return {
        "node_id": node_id,
        "timestamp": log.timestamp,
        "overall_trust": trust_eval["overall_node_trust"],
        "sensor_trusts": trust_eval["sensor_trusts"]
    }


@router.get("/anomaly-check/{node_id}")
def check_node_anomalies(node_id: str, db: Session = Depends(get_db)):
    """Compute baseline Isolation Forest anomaly score and Physical Rule violations."""
    log = (
        db.query(TelemetryLogModel)
        .filter(TelemetryLogModel.node_id == node_id)
        .order_by(TelemetryLogModel.timestamp.desc())
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail=f"No telemetry records found for node '{node_id}'")

    metrics = {
        "temperature_c": log.temperature_c,
        "humidity_pct": log.humidity_pct,
        "current_amps": log.current_amps,
        "vibration_g": log.vibration_g,
        "air_quality_index": log.air_quality_index,
        "water_leak_detected": log.water_leak_detected
    }

    hw_status = {"relay_1_closed": True}

    ml_score = isolation_forest_engine.predict_anomaly_score(metrics)
    rule_score, violated_rules = physical_rules_engine.evaluate_rules(metrics, hw_status)

    return {
        "node_id": node_id,
        "timestamp": log.timestamp,
        "ml_isolation_forest_score": ml_score,
        "physical_rule_score": rule_score,
        "violated_rules": violated_rules
    }
