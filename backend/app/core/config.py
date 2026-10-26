"""
Backend Configuration Module.
Loads environment variables for FastAPI and Database.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Find .env file in root
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "VeriInfra Edge AI Digital Twin"
    API_V1_STR: str = "/api/v1"
    
    # MQTT Config
    MQTT_BROKER_HOST: str = os.getenv("MQTT_BROKER_HOST", "localhost")
    MQTT_BROKER_PORT: int = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    MQTT_TOPIC_PREFIX: str = os.getenv("MQTT_TOPIC_PREFIX", "veriinfra/v1")
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "")
    MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD", "")

    # Storage Config
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "gateway/veriinfra_edge.db")
    
    @property
    def DATABASE_URI(self) -> str:
        db_path = Path(self.SQLITE_DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path.as_posix()}"

    class Config:
        case_sensitive = True


settings = Settings()
