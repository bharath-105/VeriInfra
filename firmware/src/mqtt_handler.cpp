#include "mqtt_handler.h"

MQTTManager MqttManager;

MQTTManager::MQTTManager()
    : client(espClient),
      last_telemetry_time(0),
      last_heartbeat_time(0),
      telemetry_counter(0) {}

void MQTTManager::begin() {
    connectWiFi();
    client.setServer(MQTT_BROKER_IP, MQTT_BROKER_PORT);
    client.setCallback(MQTTManager::mqttCallback);
    connectMQTT();
}

void MQTTManager::connectWiFi() {
    if (WiFi.status() == WL_CONNECTED) return;
    
    Serial.printf("[WIFI] Connecting to SSID: %s\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    uint8_t retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 15) {
        delay(500);
        Serial.print(".");
        retries++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n[WIFI] Connected! IP Address: %s\n", WiFi.localIP().toString().c_str());
    } else {
        Serial.println("\n[WIFI] Connection failed. Operating in local failsafe mode.");
    }
}

void MQTTManager::connectMQTT() {
    if (WiFi.status() != WL_CONNECTED) return;
    if (client.connected()) return;

    Serial.printf("[MQTT] Connecting to broker at %s:%d...\n", MQTT_BROKER_IP, MQTT_BROKER_PORT);
    if (client.connect(MQTT_CLIENT_ID)) {
        Serial.println("[MQTT] Connected successfully!");

        // Subscribe to Actuation Topic
        char actuate_topic[100];
        snprintf(actuate_topic, sizeof(actuate_topic), "%s/nodes/%s/actuate", MQTT_TOPIC_PREFIX, NODE_ID);
        client.subscribe(actuate_topic);
        Serial.printf("[MQTT] Subscribed to topic: %s\n", actuate_topic);

    } else {
        Serial.printf("[MQTT] Failed connection, state=%d. Retrying in background.\n", client.state());
    }
}

void MQTTManager::mqttCallback(char* topic, byte* payload, unsigned int length) {
    char message[512];
    if (length >= sizeof(message)) return;
    memcpy(message, payload, length);
    message[length] = '\0';

    Serial.printf("[MQTT RECV] Topic: %s | Message: %s\n", topic, message);

    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, message);
    if (error) {
        Serial.printf("[MQTT RECV ERROR] JSON parsing failed: %s\n", error.c_str());
        return;
    }

    const char* action = doc["action"];
    uint8_t relay_id = doc["relay_id"] | 1;
    bool target_state = doc["target_state"] | false;

    if (action != nullptr) {
        if (strcmp(action, "TRIP_RELAY") == 0 || strcmp(action, "SET_RELAY") == 0) {
            SafetyManager.setRelay(relay_id, target_state, "MQTT_COMMAND");
        } else if (strcmp(action, "SET_BUZZER") == 0) {
            SafetyManager.setBuzzer(target_state);
        }
    }
}

void MQTTManager::loop() {
    if (WiFi.status() != WL_CONNECTED) {
        connectWiFi();
    }
    if (!client.connected()) {
        static unsigned long last_reconnect_attempt = 0;
        if (millis() - last_reconnect_attempt > 5000) {
            last_reconnect_attempt = millis();
            connectMQTT();
        }
    } else {
        client.loop();
    }
}

bool MQTTManager::isConnected() {
    return client.connected();
}

void MQTTManager::publishTelemetry(const SensorMetrics& metrics) {
    if (!client.connected()) return;

    StaticJsonDocument<768> doc;
    doc["timestamp"] = millis() / 1000.0;
    doc["node_id"] = NODE_ID;
    doc["name"] = NODE_NAME;
    doc["location"] = NODE_LOCATION;

    JsonObject m = doc.createNestedObject("metrics");
    m["temperature_c"] = round(metrics.temperature_c * 100.0) / 100.0;
    m["humidity_pct"] = round(metrics.humidity_pct * 100.0) / 100.0;
    m["current_amps"] = round(metrics.current_amps * 100.0) / 100.0;
    m["vibration_g"] = round(metrics.vibration_g * 10000.0) / 10000.0;
    m["air_quality_index"] = round(metrics.air_quality_index * 10.0) / 10.0;
    m["water_leak_detected"] = metrics.water_leak_detected;
    m["water_flow_lpm"] = metrics.water_flow_lpm;

    JsonObject hw = doc.createNestedObject("hardware_status");
    hw["auto_mode_active"] = SafetyManager.isAutoMode();
    hw["physical_estop_pressed"] = SafetyManager.isEstopPressed();
    hw["relay_1_closed"] = SafetyManager.getRelay1State();
    hw["relay_2_closed"] = SafetyManager.getRelay2State();
    hw["buzzer_active"] = SafetyManager.getBuzzerState();
    hw["battery_pct"] = 99.5;
    hw["rssi_dbm"] = WiFi.RSSI();

    char buffer[768];
    serializeJson(doc, buffer);

    char topic[100];
    snprintf(topic, sizeof(topic), "%s/nodes/%s/telemetry", MQTT_TOPIC_PREFIX, NODE_ID);

    client.publish(topic, buffer);
    telemetry_counter++;
}

void MQTTManager::publishHeartbeat() {
    if (!client.connected()) return;

    StaticJsonDocument<256> doc;
    doc["timestamp"] = millis() / 1000.0;
    doc["node_id"] = NODE_ID;
    doc["status"] = SafetyManager.isEstopPressed() ? "ESTOP_TRIPPED" : "ONLINE";
    doc["uptime_sec"] = millis() / 1000;
    doc["firmware_version"] = FIRMWARE_VERSION;

    char buffer[256];
    serializeJson(doc, buffer);

    char topic[100];
    snprintf(topic, sizeof(topic), "%s/nodes/%s/heartbeat", MQTT_TOPIC_PREFIX, NODE_ID);

    client.publish(topic, buffer);
}
