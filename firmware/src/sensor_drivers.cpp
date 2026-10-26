#include "sensor_drivers.h"

SensorManager::SensorManager() 
    : dht(PIN_DHT22, DHT22), 
      accel(12345), 
      adxl_initialized(false), 
      current_calibration_factor(30.0f) {}

void SensorManager::begin() {
    // 1. Initialize DHT22
    dht.begin();

    // 2. Initialize Pin Modes for Analog & Digital Sensors
    pinMode(PIN_CURRENT_ADC, INPUT);
    pinMode(PIN_AIR_QUALITY_ADC, INPUT);
    pinMode(PIN_WATER_LEAK, INPUT_PULLUP);

    // 3. Initialize I2C and ADXL345 Accelerometer
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
    if (accel.begin()) {
        accel.setRange(ADXL345_RANGE_4_G);
        adxl_initialized = true;
    } else {
        adxl_initialized = false;
    }
}

float SensorManager::readRMSCurrent(uint16_t samples) {
    // True RMS AC Current Sampling over 1 full AC cycle (20ms for 50Hz)
    double sum_squared_diff = 0.0;
    const float VREF = 3.3f;
    const float ADC_RESOLUTION = 4095.0f;
    const float MID_POINT_VOLTS = 1.65f; // DC Bias voltage offset

    for (uint16_t i = 0; i < samples; i++) {
        int raw_adc = analogRead(PIN_CURRENT_ADC);
        float voltage = (raw_adc / ADC_RESOLUTION) * VREF;
        float diff = voltage - MID_POINT_VOLTS;
        sum_squared_diff += (diff * diff);
        delayMicroseconds(100);
    }

    double mean_square = sum_squared_diff / samples;
    double rms_voltage = sqrt(mean_square);
    float rms_current = rms_voltage * current_calibration_factor;

    // Apply low noise cutoff threshold
    if (rms_current < 0.15f) {
        rms_current = 0.0f;
    }

    return rms_current;
}

SensorMetrics SensorManager::readAllSensors() {
    SensorMetrics metrics;

    // 1. Read DHT22 Temperature & Humidity
    float t = dht.readTemperature();
    float h = dht.readHumidity();

    if (isnan(t) || isnan(h)) {
        metrics.temperature_c = 25.0f; // Baseline fallback if sensor disconnected
        metrics.humidity_pct = 50.0f;
        metrics.dht_valid = false;
    } else {
        metrics.temperature_c = t;
        metrics.humidity_pct = h;
        metrics.dht_valid = true;
    }

    // 2. Read RMS Current
    metrics.current_amps = readRMSCurrent(100);

    // 3. Read ADXL345 Vibration
    if (adxl_initialized) {
        sensors_event_t event;
        accel.getEvent(&event);
        // Calculate resultant vibration magnitude: sqrt(ax^2 + ay^2 + az^2) / g
        float total_accel = sqrt(event.acceleration.x * event.acceleration.x +
                                 event.acceleration.y * event.acceleration.y +
                                 event.acceleration.z * event.acceleration.z);
        // Normalize against Earth gravity (9.81 m/s^2)
        metrics.vibration_g = abs(total_accel - 9.81f) / 9.81f;
        metrics.adxl_valid = true;
    } else {
        metrics.vibration_g = 0.02f;
        metrics.adxl_valid = false;
    }

    // 4. Read MQ-135 Air Quality ADC
    int raw_aqi_adc = analogRead(PIN_AIR_QUALITY_ADC);
    metrics.air_quality_index = (raw_aqi_adc / 4095.0f) * 500.0f;

    // 5. Read Water Leak Digital Probe (Active LOW when water connects probe contacts)
    int water_val = digitalRead(PIN_WATER_LEAK);
    metrics.water_leak_detected = (water_val == LOW);

    metrics.water_flow_lpm = 0.0f;

    return metrics;
}
