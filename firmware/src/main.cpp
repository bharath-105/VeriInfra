#include <Arduino.h>
#include "config.h"
#include "sensor_drivers.h"
#include "safety_override.h"
#include "mqtt_handler.h"

// Global Manager Instances
SensorManager Sensors;

// FreeRTOS Task Handles
TaskHandle_t TaskSensorHandle = NULL;
TaskHandle_t TaskMqttHandle = NULL;

// FreeRTOS Core 0 Task: Sensor Reading & Local Failsafe Evaluation
void TaskSensorRead(void* pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(TELEMETRY_PUBLISH_INTERVAL_MS);

    for (;;) {
        // 1. Read All Physical Sensors
        SensorMetrics metrics = Sensors.readAllSensors();

        // 2. Evaluate Local Failsafe Rules (Autonomous protection)
        SafetyManager.evaluateLocalFailsafe(metrics.temperature_c, metrics.current_amps);

        // 3. Publish Telemetry via MQTT if connected
        MqttManager.publishTelemetry(metrics);

        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}

// FreeRTOS Core 1 Task: WiFi Connection & MQTT Event Loop
void TaskMqttNetwork(void* pvParameters) {
    unsigned long last_heartbeat = 0;

    for (;;) {
        // Maintain WiFi/MQTT Loop
        MqttManager.loop();

        // Periodic Heartbeat
        if (millis() - last_heartbeat >= HEARTBEAT_PUBLISH_INTERVAL_MS) {
            MqttManager.publishHeartbeat();
            last_heartbeat = millis();
        }

        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\n==========================================");
    Serial.println("  VeriInfra ESP32 Node Firmware starting  ");
    Serial.println("==========================================");

    // 1. Initialize Safety Manager & GPIO Interrupts
    SafetyManager.begin();
    Serial.println("[SYSTEM] Safety Manager & E-Stop ISR initialized.");

    // 2. Initialize Sensors & Drivers
    Sensors.begin();
    Serial.println("[SYSTEM] Sensor drivers initialized.");

    // 3. Initialize MQTT & Wi-Fi Network
    MqttManager.begin();
    Serial.println("[SYSTEM] MQTT Network Manager initialized.");

    // 4. Create FreeRTOS Tasks pinned to specific cores
    xTaskCreatePinnedToCore(
        TaskSensorRead,
        "TaskSensorRead",
        8192,
        NULL,
        2,  // High Priority for safety & timing
        &TaskSensorHandle,
        0   // Core 0
    );

    xTaskCreatePinnedToCore(
        TaskMqttNetwork,
        "TaskMqttNetwork",
        8192,
        NULL,
        1,  // Medium Priority
        &TaskMqttHandle,
        1   // Core 1
    );

    Serial.println("[SYSTEM] FreeRTOS tasks launched on Core 0 & Core 1.");
}

void loop() {
    // Empty main loop - execution handled by FreeRTOS tasks
    vTaskDelay(pdMS_TO_TICKS(1000));
}
