#ifndef MQTT_HANDLER_H
#define MQTT_HANDLER_H

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "config.h"
#include "sensor_drivers.h"
#include "safety_override.h"

class MQTTManager {
private:
    WiFiClient espClient;
    PubSubClient client;
    unsigned long last_telemetry_time;
    unsigned long last_heartbeat_time;
    uint32_t telemetry_counter;

    void connectWiFi();
    void connectMQTT();
    static void mqttCallback(char* topic, byte* payload, unsigned int length);

public:
    MQTTManager();
    void begin();
    void loop();

    void publishTelemetry(const SensorMetrics& metrics);
    void publishHeartbeat();
    bool isConnected();
};

extern MQTTManager MqttManager;

#endif // MQTT_HANDLER_H
