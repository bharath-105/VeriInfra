"""
Pydantic Schemas for API Requests, Responses, and Payload Contracts.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# -----------------------------------
# Telemetry Schemas
# -----------------------------------
class SensorMetricsSchema(BaseModel):
    temperature_c: float
    humidity_pct: float
    current_amps: float
    vibration_g: float
    air_quality_index: float
    water_leak_detected: bool
    water_flow_lpm: Optional[float] = 0.0


class HardwareStatusSchema(BaseModel):
    auto_mode_active: bool
    physical_estop_pressed: bool
    relay_1_closed: bool
    relay_2_closed: bool
    buzzer_active: bool
    battery_pct: float
    rssi_dbm: int


class TelemetryIngestSchema(BaseModel):
    timestamp: float
    node_id: str
    name: Optional[str] = ""
    location: Optional[str] = ""
    metrics: SensorMetricsSchema
    hardware_status: HardwareStatusSchema


class TelemetryResponseSchema(BaseModel):
    id: int
    timestamp: datetime
    node_id: str
    temperature_c: float
    humidity_pct: float
    current_amps: float
    vibration_g: float
    air_quality_index: float
    water_leak_detected: bool

    class Config:
        from_attributes = True


# -----------------------------------
# Node Schemas
# -----------------------------------
class NodeResponseSchema(BaseModel):
    node_id: str
    name: str
    location: Optional[str]
    firmware_version: str
    is_active: bool
    last_seen: datetime

    class Config:
        from_attributes = True


# -----------------------------------
# Actuation Override Request Schema
# -----------------------------------
class OverrideRequestSchema(BaseModel):
    node_id: str
    action: str = Field(..., description="TRIP_RELAY, SET_RELAY, SET_BUZZER")
    relay_id: int = 1
    target_state: bool = False
    reason: str = "MANUAL_DASHBOARD_OVERRIDE"


class OverrideResponseSchema(BaseModel):
    action_id: str
    node_id: str
    action: str
    success: bool
    timestamp: datetime
