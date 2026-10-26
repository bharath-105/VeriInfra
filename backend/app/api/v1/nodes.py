"""
FastAPI Nodes Management Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.db_models import NodeModel
from backend.app.models.schemas import NodeResponseSchema

router = APIRouter()


@router.get("", response_model=List[NodeResponseSchema])
def list_nodes(db: Session = Depends(get_db)):
    """List all registered ESP32 nodes and online status."""
    nodes = db.query(NodeModel).order_by(NodeModel.node_id).all()
    return nodes
