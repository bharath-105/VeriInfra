#ifndef SENSOR_DRIVERS_H
#define SENSOR_DRIVERS_H

#include <Arduino.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include "config.h"

// Sensor Data Structure
struct SensorMetrics {
    float temperature_c;
    float humidity_pct;
    float current_amps;
    float vibration_g;
    float air_quality_index;
    bool water_leak_detected;
    float water_flow_lpm;
    bool dht_valid;
    bool adxl_valid;
};

class SensorManager {
private:
    DHT dht;
    Adafruit_ADXL345_Unified accel;
    bool adxl_initialized;

    // Calibration Constants
    float current_calibration_factor; // Calibration coefficient for SCT-013 / ACS712

    float readRMSCurrent(uint16_t samples = 200);

public:
    SensorManager();
    void begin();
    SensorMetrics readAllSensors();
};

#endif // SENSOR_DRIVERS_H
