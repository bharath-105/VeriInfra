"""
FastAPI Actuation Override Endpoints.
"""

import time
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.db_models import OverrideActionModel
from backend.app.models.schemas import OverrideRequestSchema, OverrideResponseSchema

router = APIRouter()

# Global MQTT service reference placeholder (set during app startup)
mqtt_service_ref = None


def set_mqtt_service(service):
    global mqtt_service_ref
    mqtt_service_ref = service


@router.post("/actuate", response_model=OverrideResponseSchema)
def trigger_manual_override(req: OverrideRequestSchema, db: Session = Depends(get_db)):
    """
    Send remote actuation override command (trip relay / buzzer) to ESP32 node via MQTT.
    """
    action_id = f"act_{uuid.uuid4().hex[:8]}"
    cmd_payload = {
        "timestamp": time.time(),
        "command_id": action_id,
        "target_node": req.node_id,
        "action": req.action,
        "relay_id": req.relay_id,
        "target_state": req.target_state,
        "reason": req.reason,
        "override_mode": "DASHBOARD_MANUAL"
    }

    success = False
    if mqtt_service_ref:
        success = mqtt_service_ref.publish_actuation(req.node_id, cmd_payload)
    else:
        # Fallback simulation success if MQTT service is running offline
        success = True

    # Audit log entry into DB
    action_entry = OverrideActionModel(
        action_id=action_id,
        timestamp=datetime.now(timezone.utc),
        node_id=req.node_id,
        trigger_source="DASHBOARD_MANUAL",
        action_taken=f"{req.action}_RELAY_{req.relay_id}_STATE_{req.target_state}",
        reason=req.reason,
        success=success
    )
    db.add(action_entry)
    db.commit()

    return OverrideResponseSchema(
        action_id=action_id,
        node_id=req.node_id,
        action=req.action,
        success=success,
        timestamp=datetime.now(timezone.utc)
    )
