"""
ESP32 Node Simulator for VeriInfra.

Simulates multiple ESP32 edge sensor nodes publishing real-time telemetry over MQTT.
Features:
- Realistic sensor noise generation (Gaussian distribution)
- Real-time actuation listener (responds to remote relay trip commands)
- Runtime fault injection engine (flatline, sensor drift, thermal runaway, current overload, water leak, hardware E-Stop)
- Battery drain and hardware state reporting

Usage:
    python simulate_esp32_nodes.py
"""

import sys
import time
import json
import random
import math
import logging
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_KEEPALIVE,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_TOPIC_PREFIX,
    PUBLISH_INTERVAL_SEC,
    HEARTBEAT_INTERVAL_SEC,
    DEFAULT_NODES
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("ESP32Simulator")


class SimulatedESP32Node:
    """
    Class representing a single ESP32 sensor node state and physics simulation.
    """

    def __init__(self, node_config: Dict[str, Any]):
        self.node_id: str = node_config["node_id"]
        self.name: str = node_config["name"]
        self.location: str = node_config["location"]
        self.base_metrics: Dict[str, float] = dict(node_config["base_metrics"])

        # Dynamic State Variables
        self.current_metrics: Dict[str, Any] = dict(self.base_metrics)
        self.battery_pct: float = 100.0
        self.rssi_dbm: int = -60
        self.relay_1_closed: bool = True  # Relay 1 ON by default (normal operating load)
        self.relay_2_closed: bool = False
        self.buzzer_active: bool = False
        self.auto_mode_active: bool = True  # True = Auto, False = Manual physical override
        self.physical_estop_pressed: bool = False

        # Active Fault Injection State
        self.active_faults: Dict[str, Dict[str, Any]] = {}
        # Fault types: 'flatline', 'drift', 'thermal_spike', 'current_spike', 'water_leak', 'network_drop'

        # Time tracking
        self.step_counter: int = 0
        self.last_heartbeat_time: float = 0.0

    def inject_fault(self, fault_type: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """Inject an intentional fault into this node."""
        params = parameters or {}
        self.active_faults[fault_type] = params
        logger.warning(f"[{self.node_id}] FAULT INJECTED: {fault_type} with params {params}")

    def clear_fault(self, fault_type: str) -> None:
        """Clear an active fault."""
        if fault_type in self.active_faults:
            del self.active_faults[fault_type]
            logger.info(f"[{self.node_id}] FAULT CLEARED: {fault_type}")

    def clear_all_faults(self) -> None:
        """Clear all active faults on node."""
        self.active_faults.clear()
        logger.info(f"[{self.node_id}] ALL FAULTS CLEARED.")

    def step(self) -> Dict[str, Any]:
        """
        Advance node physics by 1 time step (1 second) and calculate metrics.
        """
        self.step_counter += 1

        # Slowly simulate battery drain
        if self.battery_pct > 0:
            self.battery_pct = max(0.0, self.battery_pct - 0.001)

        # Fluctuate WiFi RSSI slightly
        self.rssi_dbm = -60 + random.randint(-5, 5)

        # Base noise simulation (normal operating state)
        temp_val = self.base_metrics["temperature_c"] + random.gauss(0, 0.15)
        hum_val = self.base_metrics["humidity_pct"] + random.gauss(0, 0.3)
        curr_val = self.base_metrics["current_amps"] + random.gauss(0, 0.05) if self.relay_1_closed else 0.0
        vib_val = max(0.0, self.base_metrics["vibration_g"] + random.gauss(0, 0.005))
        air_val = max(0.0, self.base_metrics["air_quality_index"] + random.gauss(0, 0.5))
        water_leak = self.base_metrics["water_leak_detected"]
        water_flow = self.base_metrics["water_flow_lpm"]

        # Apply Active Fault Transformations
        
        # 1. Flatline fault (Sensor stuck on fixed value)
        if "flatline" in self.active_faults:
            target_sensor = self.active_faults["flatline"].get("sensor", "temperature_c")
            flat_val = self.active_faults["flatline"].get("value", 25.0)
            if target_sensor == "temperature_c":
                temp_val = flat_val
            elif target_sensor == "current_amps":
                curr_val = flat_val
            elif target_sensor == "vibration_g":
                vib_val = flat_val

        # 2. Sensor Drift fault (Gradual linear increase/decrease over time)
        if "drift" in self.active_faults:
            target_sensor = self.active_faults["drift"].get("sensor", "temperature_c")
            rate = self.active_faults["drift"].get("rate", 0.2)  # +0.2 deg per sec
            drift_offset = self.step_counter * rate
            if target_sensor == "temperature_c":
                temp_val += drift_offset
            elif target_sensor == "current_amps":
                curr_val += drift_offset

        # 3. Thermal Spike / Overload
        if "thermal_spike" in self.active_faults:
            target_temp = self.active_faults["thermal_spike"].get("target_c", 65.0)
            # Exponential warm-up curve towards target
            temp_val += (target_temp - temp_val) * 0.15

        # 4. Current Overload Spike
        if "current_spike" in self.active_faults:
            spike_amps = self.active_faults["current_spike"].get("amps", 25.0)
            curr_val = spike_amps + random.gauss(0, 0.5)

        # 5. Water Leak Trigger
        if "water_leak" in self.active_faults:
            water_leak = True

        # 6. Physical E-Stop Button Pressed
        if "estop_pressed" in self.active_faults:
            self.physical_estop_pressed = True
            self.relay_1_closed = False  # Hardware forces relay open!
        else:
            self.physical_estop_pressed = False

        # Store updated current metrics
        self.current_metrics = {
            "temperature_c": round(temp_val, 2),
            "humidity_pct": round(hum_val, 2),
            "current_amps": round(max(0.0, curr_val), 2),
            "vibration_g": round(vib_val, 4),
            "air_quality_index": round(air_val, 1),
            "water_leak_detected": water_leak,
            "water_flow_lpm": round(water_flow, 2)
        }

        # Build Telemetry JSON Payload
        payload = {
            "timestamp": round(time.time(), 3),
            "node_id": self.node_id,
            "name": self.name,
            "location": self.location,
            "metrics": self.current_metrics,
            "hardware_status": {
                "auto_mode_active": self.auto_mode_active,
                "physical_estop_pressed": self.physical_estop_pressed,
                "relay_1_closed": self.relay_1_closed,
                "relay_2_closed": self.relay_2_closed,
                "buzzer_active": self.buzzer_active,
                "battery_pct": round(self.battery_pct, 1),
                "rssi_dbm": self.rssi_dbm
            }
        }
        return payload

    def build_heartbeat_payload(self) -> Dict[str, Any]:
        """Build periodic heartbeat diagnostic payload."""
        return {
            "timestamp": round(time.time(), 3),
            "node_id": self.node_id,
            "status": "ONLINE" if not self.physical_estop_pressed else "ESTOP_TRIPPED",
            "uptime_sec": self.step_counter,
            "firmware_version": "1.0.4-edge",
            "active_faults": list(self.active_faults.keys())
        }

    def process_actuation_command(self, payload: Dict[str, Any]) -> bool:
        """
        Process incoming MQTT actuation command from Gateway or User Dashboard.
        """
        action = payload.get("action")
        relay_id = payload.get("relay_id", 1)
        target_state = payload.get("target_state", False)

        logger.info(f"[{self.node_id}] ACTUATION COMMAND RECEIVED: {action} (Relay {relay_id} -> {target_state})")

        # Hardware E-Stop check dominance
        if self.physical_estop_pressed:
            logger.warning(f"[{self.node_id}] REJECTED COMMAND: Physical E-Stop button is mechanically engaged!")
            return False

        if action in ["TRIP_RELAY", "SET_RELAY"]:
            if relay_id == 1:
                self.relay_1_closed = target_state
            elif relay_id == 2:
                self.relay_2_closed = target_state
            logger.info(f"[{self.node_id}] Relay {relay_id} set to {'CLOSED/ON' if target_state else 'OPEN/TRIPPED'}")

        elif action == "SET_BUZZER":
            self.buzzer_active = target_state
            logger.info(f"[{self.node_id}] Buzzer alarm set to {target_state}")

        return True


class VeriInfraSimulatorRunner:
    """
    Main Runner managing MQTT connections and simulation loop.
    """

    def __init__(self):
        self.nodes: Dict[str, SimulatedESP32Node] = {}
        for config in DEFAULT_NODES:
            node = SimulatedESP32Node(config)
            self.nodes[node.node_id] = node

        # MQTT Client initialization
        self.mqtt_client = mqtt.Client(client_id="veriinfra_esp32_simulator")
        if MQTT_USERNAME and MQTT_PASSWORD:
            self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Successfully connected to MQTT Broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
            # Subscribe to actuation topics for all nodes
            for node_id in self.nodes:
                actuate_topic = f"{MQTT_TOPIC_PREFIX}/nodes/{node_id}/actuate"
                client.subscribe(actuate_topic)
                logger.info(f"Subscribed to command topic: {actuate_topic}")
        else:
            logger.error(f"MQTT Connection failed with return code {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            topic_parts = msg.topic.split("/")
            node_id = topic_parts[3]  # Extract node_id from topic hierarchy

            if node_id in self.nodes:
                self.nodes[node_id].process_actuation_command(payload)
            elif node_id == "all":
                for node in self.nodes.values():
                    node.process_actuation_command(payload)
        except Exception as e:
            logger.error(f"Failed to process actuation message on {msg.topic}: {e}")

    def start(self):
        """Start simulator execution loop."""
        logger.info("Starting VeriInfra ESP32 Simulator...")
        logger.info(f"Configured Nodes: {list(self.nodes.keys())}")
        
        # Connect to MQTT Broker with fallback
        try:
            self.mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEPALIVE)
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.warning(f"Could not connect to MQTT Broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT} ({e}).")
            logger.warning("Running in STDOUT Logging mode only. Start Mosquitto to enable live MQTT publishing.")

        try:
            while True:
                now = time.time()
                for node_id, node in self.nodes.items():
                    # 1. Step Node Physics & Build Telemetry
                    telemetry = node.step()
                    telemetry_topic = f"{MQTT_TOPIC_PREFIX}/nodes/{node_id}/telemetry"

                    # 2. Publish Telemetry Payload
                    try:
                        self.mqtt_client.publish(telemetry_topic, json.dumps(telemetry))
                    except Exception:
                        pass
                    
                    # Log summary to console
                    metrics = telemetry["metrics"]
                    logger.info(
                        f"[{node_id}] Temp: {metrics['temperature_c']}°C | "
                        f"Curr: {metrics['current_amps']}A | Vib: {metrics['vibration_g']}g | "
                        f"Relay: {'ON' if node.relay_1_closed else 'TRIPPED'} | "
                        f"Faults: {list(node.active_faults.keys()) or 'None'}"
                    )

                    # 3. Publish Heartbeat if interval elapsed
                    if now - node.last_heartbeat_time >= HEARTBEAT_INTERVAL_SEC:
                        heartbeat = node.build_heartbeat_payload()
                        heartbeat_topic = f"{MQTT_TOPIC_PREFIX}/nodes/{node_id}/heartbeat"
                        try:
                            self.mqtt_client.publish(heartbeat_topic, json.dumps(heartbeat))
                        except Exception:
                            pass
                        node.last_heartbeat_time = now

                time.sleep(PUBLISH_INTERVAL_SEC)

        except KeyboardInterrupt:
            logger.info("Stopping ESP32 Simulator gracefully.")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()


if __name__ == "__main__":
    runner = VeriInfraSimulatorRunner()
    runner.start()
