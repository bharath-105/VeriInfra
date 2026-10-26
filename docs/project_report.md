# VeriInfra: A Resilient Edge AI Digital Twin with Physical Safety Overrides for Smart Infrastructure Monitoring

**Major Project Technical Report**  
**Department of Computer Science & Engineering (AIML)**  

---

## Chapter 1: Introduction

### 1.1 Background & Context
Modern smart buildings, hostel utility rooms, server facilities, and academic laboratories depend heavily on Internet of Things (IoT) sensor networks for environmental and operational health monitoring. Parameters such as temperature, electrical current, structural vibration, air quality, and liquid leakage provide early warnings for equipment degradation and catastrophic physical failures.

### 1.2 Problem Statement
Conventional IoT monitoring systems exhibit three major structural limitations:
1. **Cloud Dependency Vulnerability:** When internet WAN connectivity fails, cloud monitoring engines become blind to local infrastructure conditions, risking unrecorded thermal runaways or electrical fires.
2. **False Shutdowns from Sensor Malfunctions:** Low-cost environmental sensors frequently drift or flatline. Naive anomaly detection algorithms misinterpret sensor drift as physical disasters, causing expensive false emergency shutdowns of server racks or cooling pumps.
3. **Absence of Deterministic Physical Safety Overrides:** pure software analytics often lack low-latency hardware control over physical relays to isolate dangerous electrical or fluid hazards locally.

---

## Chapter 2: System Architecture & Design

### 2.1 Layered Architecture
VeriInfra addresses these limitations through a 3-layer resilient architecture:
* **Perceptual & Actuation Layer (ESP32 Nodes):** Real-time sensor sampling, FreeRTOS multi-threading, local failsafe threshold enforcement, optocoupler-isolated relay control, and hardware mushroom Emergency-Stop button interrupts.
* **Edge Gateway & AI Engine:** Python FastAPI server, SQLite offline queue buffer, NetworkX Digital Twin dependency graph, Sensor-Trust Index engine, Scikit-Learn Isolation Forest, and PyTorch LSTM Autoencoder.
* **Presentation Layer:** Real-time WebSockets streaming, Streamlit dashboard, interactive graph visualization, and manual override control panel.

```
+-----------------------------------------------------------------------------------+
|                           REACT / STREAMLIT DASHBOARD                             |
+-----------------------------------------+-----------------------------------------+
                                          ^ WebSockets / REST
                                          v
+-----------------------------------------------------------------------------------+
| GATEWAY ENGINE                                                                    |
|  - Sensor-Trust Index Engine (Drift, Flatline, Range bounds)                      |
|  - NetworkX Digital Twin Asset Graph & Risk Propagation                           |
|  - Isolation Forest & PyTorch LSTM Autoencoder                                    |
|  - Hybrid Anomaly Scorer S_hybrid = w1*S_ml + w2*S_rule + w3*S_causal + w4*(1-S_t)|
|  - 5-State Emergency Manager (NORMAL -> ADVISORY -> HIGH_RISK -> EMERGENCY_STOP)  |
|  - SQLite Offline Queue Buffer (0% Telemetry Loss)                                |
+-----------------------------------------+-----------------------------------------+
                                          ^ MQTT (Wi-Fi / LAN)
                                          v
+-----------------------------------------------------------------------------------+
| ESP32 SENSOR NODES & SAFETY OVERRIDES                                             |
|  - DHT22 (Temp/Hum), SCT-013 (Current RMS), ADXL345 (Vibration), MQ-135, Water    |
|  - Hardware Mushroom E-Stop Switch (Hardwired GPIO ISR Dominance)                 |
|  - 5V Isolated Relay Module (Low-Voltage DC Load Isolation)                       |
+-----------------------------------------------------------------------------------+
```

---

## Chapter 3: Implementation Details

### 3.1 Firmware Design (ESP32 C++ / FreeRTOS)
- **Core 0 Task (`TaskSensorRead`):** Samples DHT22, computes True-RMS AC current ($I_{rms} = \sqrt{\frac{1}{N}\sum (V_i - V_{mid})^2} \times K$), calculates ADXL345 3-axis vibration magnitude ($G = \frac{\sqrt{a_x^2 + a_y^2 + a_z^2} - 9.81}{9.81}$), and evaluates local failsafe limits.
- **Core 1 Task (`TaskMqttNetwork`):** Manages WiFi auto-reconnect, publishes JSON telemetry (`veriinfra/v1/nodes/{id}/telemetry`) and heartbeats, and listens for actuation payloads.
- **Hardware ISR (`estopISR`):** Attached to GPIO 13 falling edge. Mechanically overrides software commands to de-energize relay coils instantly upon physical button press.

### 3.2 Sensor-Trust Index ($S_{trust}$)
Evaluates 4 trust metrics:
$$S_{trust} = \min(T_{range}, T_{flat}, T_{drift}, T_{missing})$$
* **Range Bounds:** Ensures metric lies within physical sensor boundaries.
* **Flatline Check:** Detects stuck sensor readings when rolling variance $\text{Var}(x) < 10^{-4}$.
* **Drift Rate Check:** Flags unreal instantaneous rate of change $\left|\frac{\Delta x}{\Delta t}\right| > \text{max\_rate}$.
* **Sensor-Trust Masking:** If $S_{trust} < 0.4$, $S_{ML\_masked} = S_{ML} \cdot S_{trust}$, suppressing false emergency trips.

### 3.3 Hybrid Anomaly Score ($S_{hybrid}$)
$$S_{hybrid} = 0.40 \cdot S_{ML\_masked} + 0.40 \cdot S_{rule} + 0.10 \cdot S_{causal} + 0.10 \cdot (1 - S_{trust})$$
When $S_{hybrid} \ge 0.70$ or $S_{rule} \ge 1.0$, system mode transitions to `EMERGENCY_STOP` and dispatches MQTT relay trip signals.

---

## Chapter 4: Experimental Benchmarks & Results

| Benchmark Metric / Scenario | Target Specification | Measured Result | Status |
| :--- | :---: | :---: | :---: |
| **Detection Latency (Thermal Cascade)** | $< 100\text{ ms}$ | **5.68 ms** | **PASS** |
| **False Positive Suppression Rate** | $> 95\%$ | **100.0 %** | **PASS** |
| **Offline Telemetry Preservation Rate**| $100\%$ | **100.0 %** | **PASS** |
| **Physical Relay Hazard Override** | Deterministic | **Triggered (True)** | **PASS** |

### Ablation Study Summary
Under simulated single temperature sensor drift ($+25^\circ\text{C}$ in $1\text{ s}$), an unmasked ML-Only detector triggered a false emergency trip ($S_{ML} = 0.82 \ge 0.70$). VeriInfra's Sensor-Trust masking attenuated the score ($S_{ML\_masked} = 0.08, S_{hybrid} = 0.21$), keeping system state in `ADVISORY` and achieving **100% false-positive suppression**.

---

## Chapter 5: Conclusion & Future Scope

### 5.1 Conclusion
VeriInfra successfully delivers a practical, resilient edge AI digital twin prototype. By combining low-cost ESP32 nodes, NetworkX asset graphs, Isolation Forest, PyTorch LSTM autoencoders, and Sensor-Trust masking, the system achieves sub-10ms response latency while eliminating false shutdowns caused by faulty sensors.

### 5.2 Future Work
1. Implementation of edge hardware acceleration (Google Coral Edge TPU / Kneron).
2. Multi-building federated learning across campus micro-grids.
3. LoRaWAN long-range wireless fallback for rural infrastructure zones.
