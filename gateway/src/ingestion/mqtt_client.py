"""
MQTT Subscriber and Telemetry Ingestion Client for Edge Gateway.
"""

import json
import logging
import threading
import paho.mqtt.client as mqtt
from typing import Callable, Optional

from backend.app.core.config import settings
from gateway.src.ingestion.buffer_manager import TelemetryBufferManager

logger = logging.getLogger("MQTTIngestionClient")


class MQTTIngestionService:
    """
    Background MQTT Service subscribing to telemetry and forwarding to storage buffer.
    """

    def __init__(self, buffer_manager: TelemetryBufferManager, broadcast_callback: Optional[Callable] = None):
        self.buffer_manager = buffer_manager
        self.broadcast_callback = broadcast_callback
        self.client = mqtt.Client(client_id="veriinfra_gateway_ingestion")
        
        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.is_running = False

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Gateway Connected to MQTT Broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
            # Wildcard subscription for all node telemetries & heartbeats
            telemetry_topic = f"{settings.MQTT_TOPIC_PREFIX}/nodes/+/telemetry"
            heartbeat_topic = f"{settings.MQTT_TOPIC_PREFIX}/nodes/+/heartbeat"
            
            client.subscribe(telemetry_topic)
            client.subscribe(heartbeat_topic)
            logger.info(f"Subscribed to ingestion topics: {telemetry_topic}, {heartbeat_topic}")
        else:
            logger.error(f"MQTT Ingestion Connection failed with return code {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode("utf-8")
            payload = json.loads(payload_str)

            if "telemetry" in msg.topic:
                # 1. Push payload into offline telemetry buffer queue
                self.buffer_manager.enqueue(payload)

                # 2. Trigger WebSocket broadcast callback if registered
                if self.broadcast_callback:
                    self.broadcast_callback(payload)

            elif "heartbeat" in msg.topic:
                logger.debug(f"Heartbeat received from {payload.get('node_id')}: {payload.get('status')}")

        except Exception as e:
            logger.error(f"Error parsing MQTT message on {msg.topic}: {e}")

    def start(self):
        """Start non-blocking MQTT ingestion loop."""
        self.is_running = True
        self.buffer_manager.start()
        try:
            self.client.connect_async(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
            self.client.loop_start()
            logger.info("MQTT Ingestion Service loop started.")
        except Exception as e:
            logger.warning(f"MQTT Broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT} unreachable ({e}). Operating offline.")

    def stop(self):
        """Stop MQTT subscriber and buffer manager."""
        self.is_running = False
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            pass
        self.buffer_manager.stop()
        logger.info("MQTT Ingestion Service stopped.")

    def publish_actuation(self, node_id: str, payload: dict) -> bool:
        """Publish remote actuation command to specific node over MQTT."""
        topic = f"{settings.MQTT_TOPIC_PREFIX}/nodes/{node_id}/actuate"
        try:
            res = self.client.publish(topic, json.dumps(payload))
            logger.info(f"Published actuation to {topic}: {payload}")
            return res.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"Failed to publish actuation command to {topic}: {e}")
            return False
