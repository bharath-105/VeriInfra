"""
FastAPI Telemetry Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.db_models import TelemetryLogModel
from backend.app.models.schemas import TelemetryResponseSchema

router = APIRouter()


@router.get("/live/{node_id}", response_model=TelemetryResponseSchema)
def get_latest_telemetry(node_id: str, db: Session = Depends(get_db)):
    """Fetch most recent real-time sensor telemetry for a specific node."""
    log = (
        db.query(TelemetryLogModel)
        .filter(TelemetryLogModel.node_id == node_id)
        .order_by(TelemetryLogModel.timestamp.desc())
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail=f"No telemetry found for node '{node_id}'")
    return log


@router.get("/history", response_model=List[TelemetryResponseSchema])
def get_telemetry_history(
    node_id: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Fetch historical telemetry time-series logs for charting."""
    query = db.query(TelemetryLogModel)
    if node_id:
        query = query.filter(TelemetryLogModel.node_id == node_id)
    logs = query.order_by(TelemetryLogModel.timestamp.desc()).limit(limit).all()
    return logs
