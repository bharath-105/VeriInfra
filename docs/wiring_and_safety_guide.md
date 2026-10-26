# VeriInfra Hardware Schematic & Safety Override Wiring Guide

> [!CAUTION]
> **SAFETY RESTRICTION & ISOLATION MANDATE:**
> Under no circumstances should high-voltage mains (110V/230V AC) be wired directly into prototype breadboards or relay modules by student developers without professional electrical supervision. All physical actuation in this project must strictly control **isolated low-voltage demonstrator circuits** (e.g. 5V/12V DC cooling fan, LED indicators, or active piezobuzzers).

---

## 1. ESP32 Node Pin Assignment (Node 01: Server Room Rack Monitor)

| Sensor / Module | Signal Type | ESP32 GPIO Pin | Power Supply | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **DHT22 / AM2302** | Digital (1-Wire) | `GPIO 4` | 3.3V / 5V | Temperature & Humidity Sensor (Pull-up 10k resistor) |
| **SCT-013-000 CT Sensor** | Analog | `GPIO 34` (ADC1_CH6)| 3.3V biased | Non-invasive current sensor via voltage divider + DC bias (1.65V) |
| **ACS712 5A (Alternative)**| Analog | `GPIO 34` | 5V VCC / ADC | Low-voltage DC/AC demonstrator current module |
| **ADXL345 Accelerometer** | I2C (SDA/SCL) | `SDA: GPIO 21`, `SCL: GPIO 22` | 3.3V | Fan/Motor vibration monitoring |
| **SW-420 (Alternative)** | Digital | `GPIO 16` | 3.3V | Vibration switch digital trigger |
| **MQ-135 Gas / Air Quality**| Analog | `GPIO 35` (ADC1_CH7)| 5V | Smoke / Air quality proxy sensor |
| **Water Leak Probe** | Digital | `GPIO 17` | 3.3V | Rain/Leak probe transistor switch |
| **5V Relay Module (Ch 1)** | Digital Output | `GPIO 25` | 5V VCC (Opto)| Controls demonstrator fan power line (Active LOW) |
| **Active Piezo Buzzer** | Digital Output | `GPIO 26` | 3.3V / 5V | Acoustic emergency alarm |
| **Status LEDs (Red/Yel/Grn)**| Digital Outputs | `Grn: 18`, `Yel: 19`, `Red: 23` | 3.3V (220Ω resistor)| System health indicators |
| **Physical Emergency Stop**| Hardware Interrupt| `GPIO 13` | Internal Pullup| Mushroom button, hardwired hardware interrupt |
| **Auto/Manual Selector Switch**| Digital Input | `GPIO 14` | Internal Pullup| SPDT Toggle switch for physical mode dominance |

---

## 2. Hardware Physical Safety Override Dominance

```
                          +-----------------------------------+
                          |  Hardware E-Stop Push Button      |
                          |  (Normally Closed, NC Switch)     |
                          +-----------------+-----------------+
                                            |
                                            v (Hardwired VCC Cutoff)
  +-----------------------+       +-------------------+       +-----------------------+
  | ESP32 GPIO 25 Output  | ----> | Relay Driver Coil | ----> | Low-Voltage Load      |
  | (Software Command)    |       | (5V Optocoupler)  |       | (5V DC Fan / Motor)   |
  +-----------------------+       +-------------------+       +-----------------------+
                                            ^
                                            | (Hardware Master Bypass)
                          +-----------------+-----------------+
                          | Auto/Manual Selector Switch       |
                          | (Position 1: Auto, Position 2: Man)|
                          +-----------------------------------+
```

### Safety Dominance Rules:
1. **Hardware Dominance (Highest Priority):** Pressing the physical Emergency-Stop button mechanically breaks the 5V power line to the relay optocoupler coil, **instantly de-energizing the relay**, regardless of what the ESP32 code or Cloud gateway commands.
2. **Manual Selector Mode:** When the Auto/Manual toggle switch is set to `MANUAL`, the ESP32 software relay commands are bypassed, allowing direct manual toggle of demonstrator circuits via physical buttons.
3. **Software Emergency Mode (Automatic Override):** When set to `AUTO`, if the Edge Gateway calculates $S_{hybrid} \ge 0.85$, the software issues an immediate low-latency MQTT trip message to set `GPIO 25 = HIGH` (relay open) and triggers the piezo buzzer on `GPIO 26`.

---

## 3. Safe DC Demonstrator Circuit Setup

To safely demonstrate physical load tripping without touching mains voltage:
* Connect a **12V DC Power Adapter** to a **12V DC Brushless Fan** (simulating server cooling pump/fan).
* Wire the positive 12V wire through the `Common (COM)` and `Normally Open (NO)` terminals of Channel 1 on the 5V Isolated Relay module.
* Connect the Relay VCC and GND to the ESP32 breadboard rail.
* When the system detects an anomaly, the relay trips, physically cutting power to the 12V DC fan, demonstrating safe hardware shutdown in an IEEE viva presentation!
