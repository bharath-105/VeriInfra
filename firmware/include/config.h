#ifndef VERIINFRA_CONFIG_H
#define VERIINFRA_CONFIG_H

#include <Arduino.h>

// ==========================================
// 1. Device Identification & Network Credentials
// ==========================================
#define NODE_ID "node_esp32_01"
#define NODE_NAME "Server Room Rack 01"
#define NODE_LOCATION "building_a_floor_2_server_room"
#define FIRMWARE_VERSION "1.0.4-edge"

// Wi-Fi Configuration (Override via environment or router credentials)
#define WIFI_SSID "VeriInfra_AP"
#define WIFI_PASSWORD "SecurePass123"

// MQTT Broker Configuration
#define MQTT_BROKER_IP "192.168.1.100"  // IP address of Raspberry Pi / Gateway PC
#define MQTT_BROKER_PORT 1883
#define MQTT_CLIENT_ID "veriinfra_esp32_01"
#define MQTT_TOPIC_PREFIX "veriinfra/v1"

// Telemetry Intervals (Milliseconds)
#define TELEMETRY_PUBLISH_INTERVAL_MS 1000
#define HEARTBEAT_PUBLISH_INTERVAL_MS 10000

// ==========================================
// 2. Hardware Pin Assignments (ESP32 WROOM-32)
// ==========================================
// Sensors
#define PIN_DHT22 4            // Digital: DHT22 Temp & Humidity Sensor
#define PIN_CURRENT_ADC 34     // Analog: SCT-013 or ACS712 Current Sensor (ADC1_CH6)
#define PIN_AIR_QUALITY_ADC 35 // Analog: MQ-135 Air Quality / Gas (ADC1_CH7)
#define PIN_WATER_LEAK 17      // Digital: Water Leak Transistor Switch Probe
#define PIN_I2C_SDA 21         // I2C SDA for ADXL345 Accelerometer
#define PIN_I2C_SCL 22         // I2C SCL for ADXL345 Accelerometer

// Actuators & Indicators
#define PIN_RELAY_1 25         // Digital Output: 5V Relay Ch 1 (Active LOW / HIGH)
#define PIN_RELAY_2 27         // Digital Output: 5V Relay Ch 2
#define PIN_BUZZER 26          // Digital Output: Active Piezo Buzzer Alarm
#define PIN_LED_GREEN 18       // Digital Output: System OK Status LED
#define PIN_LED_YELLOW 19      // Digital Output: Warning / Advisory LED
#define PIN_LED_RED 23         // Digital Output: Emergency Trip LED

// Physical Overrides & Switches
#define PIN_ESTOP_BUTTON 13    // Digital Input: Hardware E-Stop (Hardwired ISR)
#define PIN_AUTO_MANUAL_SW 14  // Digital Input: Auto/Manual Mode Selector Switch

// ==========================================
// 3. Failsafe Local Thresholds (Gateway Offline Fallback)
// ==========================================
#define FAILSAFE_TEMP_MAX_C 60.0f      // Emergency trip if Temp > 60°C
#define FAILSAFE_CURRENT_MAX_A 15.0f   // Emergency trip if Current > 15A
#define FAILSAFE_AIR_QUALITY_MAX 300.0f// Warning flag if AQI > 300

#endif // VERIINFRA_CONFIG_H
