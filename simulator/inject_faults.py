"""
Controlled Fault Injector for VeriInfra Testing & IEEE Verification.

CLI Utility to publish fault control commands to simulated or live ESP32 nodes over MQTT.

Supported Fault Types:
  - flatline: Sensor reading freezes on a fixed value (Tests Sensor-Trust Engine)
  - drift: Sensor reading gradually rises or drifts over time (Tests Trust Rate Check)
  - thermal_spike: Triggers high temperature overload (Tests Hybrid Anomaly Scorer & Relay Trip)
  - current_spike: Triggers electrical overload spike (Tests Physical Rule Violations)
  - water_leak: Triggers water leak probe pin (Tests Emergency State Manager)
  - estop: Simulates physical hardware E-Stop switch press (Tests Safety Override Dominance)
  - clear: Clears all active faults on node

Usage Examples:
    python inject_faults.py --node node_esp32_01 --fault flatline --sensor temperature_c --val 25.0
    python inject_faults.py --node node_esp32_01 --fault thermal_spike --temp 65.0
    python inject_faults.py --node node_esp32_01 --fault clear
"""

import sys
import json
import argparse
import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_TOPIC_PREFIX
)


def send_fault_command(node_id: str, action: str, fault_type: str, parameters: dict):
    topic = f"{MQTT_TOPIC_PREFIX}/fault_injector"
    payload = {
        "target_node": node_id,
        "action": action,  # 'INJECT' or 'CLEAR'
        "fault_type": fault_type,
        "parameters": parameters
    }

    client = mqtt.Client(client_id="veriinfra_fault_injector")
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        client.publish(topic, json.dumps(payload))
        print(f"[SUCCESS] Fault command sent to topic: {topic}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        client.disconnect()
    except Exception as e:
        print(f"[ERROR] Failed to publish fault command to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}: {e}")


def main():
    parser = argparse.ArgumentParser(description="VeriInfra Controlled Fault Injector")
    parser.add_argument("--node", type=str, default="node_esp32_01", help="Target ESP32 Node ID")
    parser.add_argument(
        "--fault",
        type=str,
        required=True,
        choices=["flatline", "drift", "thermal_spike", "current_spike", "water_leak", "estop", "clear"],
        help="Type of fault to inject"
    )
    parser.add_argument("--sensor", type=str, default="temperature_c", help="Target sensor for flatline/drift")
    parser.add_argument("--val", type=float, default=25.0, help="Value for flatline sensor")
    parser.add_argument("--rate", type=float, default=0.2, help="Drift rate per second")
    parser.add_argument("--temp", type=float, default=65.0, help="Target temperature for thermal spike")
    parser.add_argument("--amps", type=float, default=25.0, help="Amperage for current spike")

    args = parser.parse_args()

    if args.fault == "clear":
        send_fault_command(args.node, "CLEAR", "all", {})
    else:
        params = {}
        if args.fault == "flatline":
            params = {"sensor": args.sensor, "value": args.val}
        elif args.fault == "drift":
            params = {"sensor": args.sensor, "rate": args.rate}
        elif args.fault == "thermal_spike":
            params = {"target_c": args.temp}
        elif args.fault == "current_spike":
            params = {"amps": args.amps}
        elif args.fault == "water_leak":
            params = {"detected": True}
        elif args.fault == "estop":
            params = {"pressed": True}

        send_fault_command(args.node, "INJECT", args.fault, params)


if __name__ == "__main__":
    main()
