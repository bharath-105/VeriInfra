"""
SQLAlchemy Database Models for VeriInfra Digital Twin & Edge Storage.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class NodeModel(Base):
    """ESP32 Edge Microcontroller Nodes Registry."""
    __tablename__ = "nodes"

    node_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100))
    ip_address = Column(String(45))
    firmware_version = Column(String(30), default="1.0.4-edge")
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    telemetries = relationship("TelemetryLogModel", back_populates="node", cascade="all, delete-orphan")
    trust_logs = relationship("SensorTrustLogModel", back_populates="node", cascade="all, delete-orphan")
    assets = relationship("AssetModel", back_populates="node")


class AssetModel(Base):
    """Digital Twin Infrastructure Assets (e.g. Server Rack, Cooling Pump, Mains Power)."""
    __tablename__ = "assets"

    asset_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    asset_type = Column(String(50), nullable=False)  # SERVER_RACK, COOLING_FAN, WATER_PUMP, MAIN_POWER
    node_id = Column(String(50), ForeignKey("nodes.node_id"), nullable=True)
    criticality_weight = Column(Float, default=1.0)
    status = Column(String(30), default="NORMAL")  # NORMAL, ADVISORY, HIGH_RISK, EMERGENCY_STOP

    node = relationship("NodeModel", back_populates="assets")


class AssetDependencyModel(Base):
    """Directed edges for NetworkX Asset Dependency Graph."""
    __tablename__ = "asset_dependencies"

    parent_asset_id = Column(String(50), ForeignKey("assets.asset_id"), primary_key=True)
    child_asset_id = Column(String(50), ForeignKey("assets.asset_id"), primary_key=True)
    dependency_type = Column(String(50), nullable=False)  # POWER_DEPENDENCY, COOLING_DEPENDENCY, DATA
    impact_weight = Column(Float, default=1.0)


class TelemetryLogModel(Base):
    """Indexed Time-Series Telemetry Store."""
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    node_id = Column(String(50), ForeignKey("nodes.node_id"), index=True)
    temperature_c = Column(Float)
    humidity_pct = Column(Float)
    current_amps = Column(Float)
    vibration_g = Column(Float)
    air_quality_index = Column(Float)
    water_leak_detected = Column(Boolean, default=False)
    water_flow_lpm = Column(Float, default=0.0)
    battery_pct = Column(Float, default=100.0)

    node = relationship("NodeModel", back_populates="telemetries")


class SensorTrustLogModel(Base):
    """Sensor-Trust Metric Log ($S_{trust}$)."""
    __tablename__ = "sensor_trust_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    node_id = Column(String(50), ForeignKey("nodes.node_id"), index=True)
    sensor_name = Column(String(50), nullable=False)
    trust_score = Column(Float, nullable=False)  # 0.0 to 1.0
    status_flag = Column(String(30), nullable=False)  # OK, FLATLINE, DRIFT, OUT_OF_RANGE, MISSING

    node = relationship("NodeModel", back_populates="trust_logs")


class AnomalyEventModel(Base):
    """Hybrid Anomaly Scoring & Root Cause Audit Log."""
    __tablename__ = "anomaly_events"

    event_id = Column(String(50), primary_key=True, index=True)
    timestamp = Column(DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    trigger_asset_id = Column(String(50), ForeignKey("assets.asset_id"), nullable=True)
    ml_score = Column(Float, nullable=False)
    rule_score = Column(Float, nullable=False)
    causal_score = Column(Float, nullable=False)
    trust_score = Column(Float, nullable=False)
    hybrid_score = Column(Float, nullable=False)
    root_cause_asset = Column(String(50))
    system_mode = Column(String(30), nullable=False)  # NORMAL, ADVISORY, HIGH_RISK, EMERGENCY_STOP


class OverrideActionModel(Base):
    """Audit Log of Hardware & Software Actuation Overrides."""
    __tablename__ = "override_actions"

    action_id = Column(String(50), primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    node_id = Column(String(50), ForeignKey("nodes.node_id"))
    trigger_source = Column(String(30), nullable=False)  # PHYSICAL_ESTOP, AUTO_HYBRID_AI, DASHBOARD_MANUAL
    action_taken = Column(String(50), nullable=False)
    reason = Column(Text)
    success = Column(Boolean, default=True)
