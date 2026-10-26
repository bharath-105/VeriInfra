"""
Database Module.
Handles SQLAlchemy Engine initialization, Session local creation, and Base declarative model.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

# SQLite connection args (check_same_thread=False allows multi-threaded MQTT ingestion)
connect_args = {"check_same_thread": False} if settings.DATABASE_URI.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URI,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI Dependency for database session injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in database if they do not exist."""
    from backend.app.models.db_models import (
        NodeModel, AssetModel, AssetDependencyModel,
        TelemetryLogModel, SensorTrustLogModel, AnomalyEventModel, OverrideActionModel
    )
    Base.metadata.create_all(bind=engine)
