"""
Simulator Configuration Module.
Loads configuration from environment variables or .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in repository root or simulator folder
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# MQTT Settings
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "veriinfra/v1")

# Simulator Parameters
SIMULATOR_NUM_NODES = int(os.getenv("SIMULATOR_NUM_NODES", "2"))
PUBLISH_INTERVAL_SEC = float(os.getenv("SIMULATOR_PUBLISH_INTERVAL_SEC", "1.0"))
HEARTBEAT_INTERVAL_SEC = float(os.getenv("SIMULATOR_HEARTBEAT_INTERVAL_SEC", "10.0"))

# Node Configurations for Prototype Simulation
DEFAULT_NODES = [
    {
        "node_id": "node_esp32_01",
        "name": "Server Room Rack 01",
        "location": "building_a_floor_2_server_room",
        "base_metrics": {
            "temperature_c": 23.5,
            "humidity_pct": 50.0,
            "current_amps": 3.5,
            "vibration_g": 0.02,
            "air_quality_index": 35.0,
            "water_leak_detected": False,
            "water_flow_lpm": 0.0
        }
    },
    {
        "node_id": "node_esp32_02",
        "name": "Hostel Utility Pump Room",
        "location": "hostel_block_b_basement",
        "base_metrics": {
            "temperature_c": 28.0,
            "humidity_pct": 65.0,
            "current_amps": 8.2,
            "vibration_g": 0.15,
            "air_quality_index": 42.0,
            "water_leak_detected": False,
            "water_flow_lpm": 12.5
        }
    }
]
