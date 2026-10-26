#ifndef SAFETY_OVERRIDE_H
#define SAFETY_OVERRIDE_H

#include <Arduino.h>
#include "config.h"

enum SystemHealthState {
    STATE_NORMAL,
    STATE_ADVISORY,
    STATE_HIGH_RISK,
    STATE_EMERGENCY_STOP
};

class SafetyOverrideManager {
private:
    volatile bool estop_flag;
    bool auto_mode_active;
    bool relay_1_state;
    bool relay_2_state;
    bool buzzer_state;
    SystemHealthState current_state;

public:
    SafetyOverrideManager();
    void begin();

    // Hardware ISR callback
    void handleEStopInterrupt();

    // State getters & updates
    bool isEstopPressed();
    bool isAutoMode();
    bool getRelay1State();
    bool getRelay2State();
    bool getBuzzerState();
    SystemHealthState getHealthState();

    void setRelay(uint8_t relay_id, bool enable, const char* source);
    void setBuzzer(bool enable);
    void setHealthState(SystemHealthState state);

    // Failsafe local threshold check
    void evaluateLocalFailsafe(float temp_c, float current_amps);
    void updateHardwareOutputs();
};

extern SafetyOverrideManager SafetyManager;

#endif // SAFETY_OVERRIDE_H
