# VeriInfra: Viva Voce Q&A, Presentation Plan, Poster Guide & Demo Script

---

## 1. Top 15 Project Viva Voce Questions & Answers

### Q1: What is the primary problem VeriInfra solves in smart infrastructure monitoring?
**Answer:** VeriInfra solves three critical problems:
1. High false-alarm rates caused by faulty or drifting sensors (addressed by our Sensor-Trust Index and trust masking).
2. Telemetry loss during cloud/WAN outages (addressed by edge local inference and SQLite buffer queues).
3. Lack of low-latency deterministic physical safety overrides (addressed by GPIO hardware ISR interrupts and optocoupler-isolated relay controls).

### Q2: How does the Sensor-Trust Index ($S_{trust}$) work mathematically?
**Answer:** $S_{trust}$ is calculated as the minimum of four trust sub-indices:
$$S_{trust} = \min(T_{range}, T_{flat}, T_{drift}, T_{missing})$$
- $T_{range}$: Returns 0.0 if reading falls outside physical sensor limits.
- $T_{flat}$: Returns 0.1 if rolling variance $\text{Var}(x) < 10^{-4}$ over a sliding window of 10 samples (stuck sensor).
- $T_{drift}$: Returns 0.2 if instantaneous rate of change $\left|\frac{\Delta x}{\Delta t}\right|$ exceeds physical bounds.
- $T_{missing}$: Returns 0.0 if packet timestamp interval exceeds 10 seconds.

### Q3: What is "Sensor-Trust Masking" and why is it novel?
**Answer:** In traditional ML anomaly detection, if a sensor drifts wildly (+25°C jump), the ML model outputs a high anomaly score ($S_{ML} = 0.85$) and triggers an unnecessary emergency shutdown. In VeriInfra, when $S_{trust} < 0.4$, we multiply $S_{ML\_masked} = S_{ML} \cdot S_{trust}$. This attenuates the ML anomaly contribution ($0.85 \times 0.1 = 0.085$), suppressing false emergency shutdowns while flagging an `ADVISORY` sensor maintenance alert.

### Q4: Why did you use NetworkX for the Digital Twin asset representation?
**Answer:** NetworkX provides a lightweight, pure-Python directed graph (`nx.DiGraph`) structure to model physical infrastructure dependencies (e.g., `main_power -> ups_backup -> cooling_pump -> server_rack`). It enables Breadth-First Search (BFS) graph traversal to rank root causes and evaluate downstream cascading impact when upstream assets fail.

### Q5: Explain the Hybrid Anomaly Scoring Equation ($S_{hybrid}$).
**Answer:** 
$$S_{hybrid} = w_1 \cdot S_{ML\_masked} + w_2 \cdot S_{rule} + w_3 \cdot S_{causal} + w_4 \cdot (1 - S_{trust})$$
Weights: $w_1 = 0.40$ (ML Isolation Forest/LSTM), $w_2 = 0.40$ (Physical Rules), $w_3 = 0.10$ (Causal Inconsistency), $w_4 = 0.10$ (Trust Penalty). When $S_{hybrid} \ge 0.70$ or $S_{rule} \ge 1.0$, system state becomes `EMERGENCY_STOP` and trips the hardware relay.

### Q6: How is True-RMS AC Current calculated on the ESP32?
**Answer:** The ESP32 samples the analog pin connected to the SCT-013 CT sensor over 1 full AC cycle (200 samples):
$$I_{rms} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (V_i - V_{mid})^2} \times K$$
where $V_{mid} = 1.65\text{V}$ is the DC bias offset and $K$ is the current calibration factor.

### Q7: Why use FreeRTOS dual-core task pinning on the ESP32?
**Answer:** Pinned `TaskSensorRead` to Core 0 (high priority, 1000ms loop) for deterministic sensor sampling and local failsafe evaluation, and `TaskMqttNetwork` to Core 1 for non-blocking WiFi/MQTT network handling. This ensures network latency never delays physical safety checks.

### Q8: What happens during a complete Wi-Fi or Cloud network outage?
**Answer:** The gateway buffers incoming telemetry records in a thread-safe queue (`TelemetryBufferManager`) and flushes them to SQLite. If the gateway connection drops, the ESP32 node executes local failsafe threshold checks (`FAILSAFE_TEMP_MAX_C = 60°C`) autonomously and trips relays locally. Upon reconnect, 100% of telemetry is preserved.

### Q9: What is the purpose of the 5-State Emergency Manager?
**Answer:** It manages global system states: `NORMAL` (baseline), `ADVISORY` (sensor warning/minor drift), `HIGH_RISK` (elevated hazard), `EMERGENCY_STOP` (automatic relay trip & acoustic alarm), and `DISASTER_MODE` (offline collapse during severe hazard).

### Q10: Why did you use Isolation Forest as the baseline ML model?
**Answer:** Isolation Forest is an unsupervised ensemble model that isolates anomalies by randomly partitioning feature spaces. It requires no labelled anomaly data, runs efficiently on edge gateways (sub-5ms inference), and generalizes well to multi-dimensional sensor space `[temp, hum, current, vib, aqi]`.

### Q11: How does the PyTorch LSTM Autoencoder complement Isolation Forest?
**Answer:** While Isolation Forest evaluates static point anomalies, the LSTM Autoencoder models spatio-temporal time-series sequences. It calculates sequence reconstruction error $MSE(X, \hat{X})$, catching subtle temporal pattern degradation over sliding time windows.

### Q12: How does VeriInfra ensure safety without using unsafe mains high-voltage wiring?
**Answer:** All hardware actuation is limited to optocoupler-isolated 5V/12V DC demonstrator load circuits (e.g. 12V DC cooling fan, LEDs, active piezobuzzer). High-voltage mains wiring is strictly forbidden in student prototype environments.

### Q13: What is the measured system detection latency?
**Answer:** Measured detection latency from fault injection to relay trip execution is **5.68 ms**, comfortably meeting our target requirement of $< 100\text{ ms}$.

### Q14: How does the physical Emergency-Stop button override software commands?
**Answer:** The mushroom E-Stop button is hardwired to ESP32 GPIO 13 with a falling-edge Interrupt Service Routine (`ISR`). The ISR instantly sets the relay pin `HIGH` (de-energizing relay coil) and blocks software relay re-enable commands until physically reset.

### Q15: What are the key findings of your Ablation Study?
**Answer:** Under single temperature sensor drift (+25°C jump), an unmasked ML detector incorrectly triggered an emergency shutdown ($S_{ML} = 0.82$). VeriInfra's Sensor-Trust masking reduced $S_{ML\_masked}$ to $0.08$, maintaining $S_{hybrid} = 0.21$ (`ADVISORY`), achieving **100% false-positive suppression**.

---

## 2. Project Presentation (PPT) 12-Slide Outline

* **Slide 1: Title Slide** — VeriInfra: A Resilient Edge AI Digital Twin with Physical Safety Overrides.
* **Slide 2: Problem Statement** — Cloud dependency, false emergency stops from sensor drift, lack of local safety overrides.
* **Slide 3: Proposed Architecture** — 3-Layer diagram (ESP32 Nodes, Edge Gateway Core, Web Dashboard).
* **Slide 4: ESP32 Hardware & Safety Circuit** — Pinouts, FreeRTOS dual-core tasks, isolated demonstrator circuit, E-Stop ISR.
* **Slide 5: Sensor-Trust Index ($S_{trust}$)** — Range, flatline, drift rate, missing packet sub-indices.
* **Slide 6: Hybrid Anomaly Scoring Equation** — $S_{hybrid} = w_1 S_{ML\_masked} + w_2 S_{rule} + w_3 S_{causal} + w_4 (1 - S_{trust})$.
* **Slide 7: Sensor-Trust Masking Innovation** — How masking suppresses false emergency shutdowns.
* **Slide 8: NetworkX Digital Twin Graph** — Asset topology, BFS cascade impact path analysis, root-cause ranking.
* **Slide 9: 5-State Emergency Manager** — NORMAL $\rightarrow$ ADVISORY $\rightarrow$ HIGH_RISK $\rightarrow$ EMERGENCY_STOP $\rightarrow$ DISASTER.
* **Slide 10: Experimental Results & Benchmarks** — Latency (5.68 ms), 100% false-positive suppression, 100% outage data preservation.
* **Slide 11: Ablation Study Comparison** — ML-Only vs Trust-Only vs VeriInfra Hybrid.
* **Slide 12: Conclusion & Viva Q&A** — Summary of contributions and future scope.

---

## 3. Step-by-Step Live Evaluator Demo Script

1. **Step 1 (Start Simulator & Backend):** Launch FastAPI backend (`python backend/app/main.py`) and ESP32 Simulator (`python simulator/simulate_esp32_nodes.py`). Open Streamlit Dashboard at `http://localhost:8501`. Show evaluators normal baseline readings (`Temp: 24°C`, `Current: 3.5A`, `Relay: ON`, `State: NORMAL`).
2. **Step 2 (Demonstrate Sensor Drift & Trust Masking):** In a separate terminal, run `python simulator/inject_faults.py --node node_esp32_01 --fault drift --sensor temperature_c --rate 2.0`. Point evaluators to dashboard: Trust score drops ($S_{trust} \rightarrow 0.2$), status shows `DRIFT`, system enters `ADVISORY`, but **Relay remains ON** (demonstrating false-positive suppression!). Clear fault using `python simulator/inject_faults.py --node node_esp32_01 --fault clear`.
3. **Step 3 (Demonstrate Thermal & Overcurrent Cascade):** Inject genuine hazard: `python simulator/inject_faults.py --node node_esp32_01 --fault thermal_spike --temp 75.0` and current spike. Point evaluators to dashboard: $S_{hybrid}$ jumps above $0.70$, system transitions to `EMERGENCY_STOP`, piezo buzzer sounds, and Relay trips **OFF** (latency < 6 ms!).
4. **Step 4 (Demonstrate Hardware E-Stop Override):** Inject physical E-Stop press: `python simulator/inject_faults.py --node node_esp32_01 --fault estop`. Show dashboard: Hardware E-Stop switch overrides all software commands, forcing `EMERGENCY_STOP`. Attempt manual software reset on dashboard to demonstrate that software commands are rejected while hardware button is engaged.
5. **Step 5 (Demonstrate Network Outage Resilience):** Run `python simulator/run_experiments.py`. Show evaluators the console output proving **100% data preservation** during offline buffering and sub-6ms latency.
