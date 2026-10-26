#include "safety_override.h"

SafetyOverrideManager SafetyManager;

// Static ISR function for GPIO interrupt
void IRAM_ATTR estopISR() {
    SafetyManager.handleEStopInterrupt();
}

SafetyOverrideManager::SafetyOverrideManager()
    : estop_flag(false),
      auto_mode_active(true),
      relay_1_state(true),  // Relay 1 ON by default (normal load energized)
      relay_2_state(false),
      buzzer_state(false),
      current_state(STATE_NORMAL) {}

void SafetyOverrideManager::begin() {
    // 1. Configure Pin Modes for Outputs
    pinMode(PIN_RELAY_1, OUTPUT);
    pinMode(PIN_RELAY_2, OUTPUT);
    pinMode(PIN_BUZZER, OUTPUT);
    pinMode(PIN_LED_GREEN, OUTPUT);
    pinMode(PIN_LED_YELLOW, OUTPUT);
    pinMode(PIN_LED_RED, OUTPUT);

    // Initial output states
    digitalWrite(PIN_RELAY_1, LOW); // Active LOW relay (LOW = ON)
    digitalWrite(PIN_RELAY_2, HIGH);
    digitalWrite(PIN_BUZZER, LOW);
    digitalWrite(PIN_LED_GREEN, HIGH);
    digitalWrite(PIN_LED_YELLOW, LOW);
    digitalWrite(PIN_LED_RED, LOW);

    // 2. Configure Input Switches with Internal Pull-Ups
    pinMode(PIN_ESTOP_BUTTON, INPUT_PULLUP);
    pinMode(PIN_AUTO_MANUAL_SW, INPUT_PULLUP);

    // 3. Attach Hardware Interrupt for E-Stop Button (Triggers on FALLING edge)
    attachInterrupt(digitalPinToInterrupt(PIN_ESTOP_BUTTON), estopISR, FALLING);
}

void SafetyOverrideManager::handleEStopInterrupt() {
    // Hardware Interrupt Service Routine - HARDWARE DOMINANCE
    estop_flag = true;
    relay_1_state = false; // Immediately trip Relay 1!
    digitalWrite(PIN_RELAY_1, HIGH); // De-energize relay coil (OFF)
    digitalWrite(PIN_BUZZER, HIGH);  // Instant acoustic warning
    digitalWrite(PIN_LED_RED, HIGH);
    digitalWrite(PIN_LED_GREEN, LOW);
    current_state = STATE_EMERGENCY_STOP;
}

bool SafetyOverrideManager::isEstopPressed() {
    // Double check hardware pin reading + ISR flag
    if (digitalRead(PIN_ESTOP_BUTTON) == LOW) {
        estop_flag = true;
    }
    return estop_flag;
}

bool SafetyOverrideManager::isAutoMode() {
    auto_mode_active = (digitalRead(PIN_AUTO_MANUAL_SW) == HIGH);
    return auto_mode_active;
}

bool SafetyOverrideManager::getRelay1State() { return relay_1_state; }
bool SafetyOverrideManager::getRelay2State() { return relay_2_state; }
bool SafetyOverrideManager::getBuzzerState() { return buzzer_state; }
SystemHealthState SafetyOverrideManager::getHealthState() { return current_state; }

void SafetyOverrideManager::setRelay(uint8_t relay_id, bool enable, const char* source) {
    // HARDWARE SAFETY DOMINANCE RULE:
    // If physical E-Stop is pressed, ignore software actuation commands!
    if (isEstopPressed()) {
        Serial.println("[SAFETY] COMMAND REJECTED: Hardware E-Stop button is mechanically engaged!");
        return;
    }

    if (relay_id == 1) {
        relay_1_state = enable;
        digitalWrite(PIN_RELAY_1, enable ? LOW : HIGH); // Active LOW logic
        Serial.printf("[SAFETY] Relay 1 set to %s by %s\n", enable ? "CLOSED/ON" : "TRIPPED/OFF", source);
    } else if (relay_id == 2) {
        relay_2_state = enable;
        digitalWrite(PIN_RELAY_2, enable ? LOW : HIGH);
    }
}

void SafetyOverrideManager::setBuzzer(bool enable) {
    if (!estop_flag) { // E-Stop forces buzzer ON
        buzzer_state = enable;
        digitalWrite(PIN_BUZZER, enable ? HIGH : LOW);
    }
}

void SafetyOverrideManager::setHealthState(SystemHealthState state) {
    if (estop_flag) {
        current_state = STATE_EMERGENCY_STOP;
        return;
    }
    current_state = state;
    updateHardwareOutputs();
}

void SafetyOverrideManager::evaluateLocalFailsafe(float temp_c, float current_amps) {
    // Local autonomous protection logic when Gateway is unreachable or disconnected
    if (temp_c > FAILSAFE_TEMP_MAX_C || current_amps > FAILSAFE_CURRENT_MAX_A) {
        Serial.println("[SAFETY] LOCAL FAILSAFE TRIP! Extreme threshold exceeded locally.");
        setRelay(1, false, "LOCAL_FAILSAFE_TRIP");
        setBuzzer(true);
        setHealthState(STATE_EMERGENCY_STOP);
    }
}

void SafetyOverrideManager::updateHardwareOutputs() {
    if (estop_flag || current_state == STATE_EMERGENCY_STOP) {
        digitalWrite(PIN_LED_GREEN, LOW);
        digitalWrite(PIN_LED_YELLOW, LOW);
        digitalWrite(PIN_LED_RED, HIGH);
        digitalWrite(PIN_BUZZER, HIGH);
    } else if (current_state == STATE_HIGH_RISK) {
        digitalWrite(PIN_LED_GREEN, LOW);
        digitalWrite(PIN_LED_YELLOW, HIGH);
        digitalWrite(PIN_LED_RED, HIGH);
        digitalWrite(PIN_BUZZER, HIGH);
    } else if (current_state == STATE_ADVISORY) {
        digitalWrite(PIN_LED_GREEN, HIGH);
        digitalWrite(PIN_LED_YELLOW, HIGH);
        digitalWrite(PIN_LED_RED, LOW);
        digitalWrite(PIN_BUZZER, LOW);
    } else { // NORMAL
        digitalWrite(PIN_LED_GREEN, HIGH);
        digitalWrite(PIN_LED_YELLOW, LOW);
        digitalWrite(PIN_LED_RED, LOW);
        digitalWrite(PIN_BUZZER, buzzer_state ? HIGH : LOW);
    }
}
