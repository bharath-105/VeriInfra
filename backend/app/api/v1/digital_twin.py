"""
FastAPI Digital Twin Asset Graph Endpoints.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from gateway.src.digital_twin.asset_graph import digital_twin_engine

router = APIRouter()


class UpdateAssetStatusRequest(BaseModel):
    asset_id: str
    status: str  # NORMAL, ADVISORY, HIGH_RISK, EMERGENCY_STOP
    risk_score: float = 0.0


@router.get("/topology")
def get_digital_twin_topology():
    """Fetch complete NetworkX Asset Dependency Graph for front-end rendering."""
    return digital_twin_engine.export_topology_dict()


@router.post("/status")
def update_asset_status(req: UpdateAssetStatusRequest):
    """Update risk status of a specific asset in the digital twin graph."""
    success = digital_twin_engine.update_asset_status(req.asset_id, req.status, req.risk_score)
    if not success:
        raise HTTPException(status_code=404, detail=f"Asset '{req.asset_id}' not found in Digital Twin graph.")
    return {"status": "SUCCESS", "asset_id": req.asset_id, "new_status": req.status}


@router.get("/impact/{asset_id}")
def get_downstream_impact(asset_id: str):
    """Compute downstream cascade impact path if specified asset fails."""
    if asset_id not in digital_twin_engine.graph:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found in Digital Twin graph.")
    affected = digital_twin_engine.get_downstream_impact_path(asset_id)
    return {
        "failed_asset": asset_id,
        "affected_downstream_count": len(affected),
        "affected_assets": affected
    }
