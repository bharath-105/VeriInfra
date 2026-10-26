"""
VeriInfra FastAPI Backend Application Entry Point.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.api.v1 import telemetry, nodes, overrides, websockets, digital_twin, trust
from gateway.src.ingestion.buffer_manager import TelemetryBufferManager
from gateway.src.ingestion.mqtt_client import MQTTIngestionService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("VeriInfraMain")

# Global Ingestion Services
buffer_manager = TelemetryBufferManager()
mqtt_service: MQTTIngestionService = None


def broadcast_to_websockets(payload: dict):
    """Callback bridge connecting MQTT telemetry stream to WebSocket clients."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(websockets.ws_manager.broadcast(payload), loop)
    except Exception as e:
        logger.debug(f"Could not broadcast via WebSocket loop: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown initialization."""
    logger.info("Initializing VeriInfra Backend & Edge Storage...")
    init_db()

    global mqtt_service
    mqtt_service = MQTTIngestionService(
        buffer_manager=buffer_manager,
        broadcast_callback=broadcast_to_websockets
    )
    overrides.set_mqtt_service(mqtt_service)
    import os
    if not os.getenv("TESTING", "").lower() in ("true", "1"):
        mqtt_service.start()

    logger.info("VeriInfra Backend startup complete.")
    yield

    logger.info("Shutting down VeriInfra Backend services...")
    if mqtt_service:
        mqtt_service.stop()
    logger.info("Shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Enable CORS for React/Streamlit frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(telemetry.router, prefix=f"{settings.API_V1_STR}/telemetry", tags=["Telemetry"])
app.include_router(nodes.router, prefix=f"{settings.API_V1_STR}/nodes", tags=["Nodes"])
app.include_router(overrides.router, prefix=f"{settings.API_V1_STR}/override", tags=["Actuation Overrides"])
app.include_router(digital_twin.router, prefix=f"{settings.API_V1_STR}/digital-twin", tags=["Digital Twin"])
app.include_router(trust.router, prefix=f"{settings.API_V1_STR}/trust", tags=["Sensor Trust & Anomalies"])
app.include_router(websockets.router, tags=["WebSockets"])


@app.get("/")
def root_status():
    return {
        "status": "ONLINE",
        "system": "VeriInfra Edge AI Digital Twin",
        "version": "1.0.0",
        "docs_url": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
