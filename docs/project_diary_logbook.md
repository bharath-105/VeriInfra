# DAYANANDA SAGAR UNIVERSITY
## School of Engineering | Department of CSE (AI & ML)
### B.Tech Major Project Diary & Work Logbook (Capstone Review-2)

**Project Title:** VeriInfra: A Resilient Edge AI Digital Twin with Physical Safety Overrides for Smart Infrastructure Monitoring  
**Team Members:**  
1. **Bharath N Menon** (USN: `ENG23AM0113`)  
2. **Mohammad Yaseen Arafat** (USN: `ENG23AM0254`)  
**Project Guide:** Dr. Manikandan Moovendran, Associate Professor  
**Co-Guide:** Prof. Akhil Pratap Singh, Assistant Professor  

---

### WEEKLY LOGBOOK ENTRIES (WEEKS 1 – 10)

#### WEEK 1: Problem Formulation & Literature Survey
* **Dates:** 01/08/2026 – 07/08/2026
* **Tasks Undertaken:**
  * Studied IEEE papers on IoT building management, edge computing, and anomaly detection.
  * Identified three major limitations of current IoT systems: cloud outage blind spots, false alarms caused by sensor drift, and lack of deterministic safety overrides.
  * Formulated preliminary problem statement and finalized project title with guide.
* **Discussion with Guide (Dr. Manikandan Moovendran):**
  * Guide recommended incorporating physical safety overrides and avoiding purely simulated cloud dashboards.
* **Status:** Completed.

#### WEEK 2: System Architecture Design & Component Selection
* **Dates:** 08/08/2026 – 14/08/2026
* **Tasks Undertaken:**
  * Drafted 3-layer architecture: Edge Sensing & Actuation Layer, Edge Gateway Layer, and Presentation Layer.
  * Selected hardware components: ESP32 NodeMCU, DHT22, SCT-013, ACS712, ADXL345, MQ-135, water probe, and 5V optocoupler relays.
  * Designed safety circuit wiring with optocoupler isolation and industrial mushroom E-Stop button.
* **Discussion with Guide:**
  * Approved sensor selection; advised ensuring student safety by switching isolated DC loads (5V/12V fans) rather than high-voltage AC mains during prototyping.
* **Status:** Completed.

#### WEEK 3: ESP32 Firmware Development & FreeRTOS Implementation
* **Dates:** 15/08/2026 – 21/08/2026
* **Tasks Undertaken:**
  * Implemented modular C++ firmware using PlatformIO for ESP32.
  * Configured FreeRTOS multitasking model: Task 1 (High-freq current/vibration sampling @ 100Hz), Task 2 (Environmental sampling @ 1Hz), Task 3 (MQTT JSON publish @ 1Hz).
  * Implemented silicon-level hardware ISR on falling edge for mushroom E-Stop button.
* **Discussion with Guide:**
  * Tested ISR response; confirmed sub-millisecond trip execution.
* **Status:** Completed.

#### WEEK 4: Gateway Ingestion & Offline Resilience Queueing
* **Dates:** 22/08/2026 – 28/08/2026
* **Tasks Undertaken:**
  * Set up Eclipse Mosquitto MQTT broker on local Edge Gateway.
  * Implemented Python Paho-MQTT subscriber and asynchronous ingestion pipeline.
  * Developed SQLite circular queue buffer to guarantee 100% offline data preservation during network disruptions.
* **Discussion with Guide:**
  * Guide reviewed buffer eviction strategy and SQLite schema design.
* **Status:** Completed.

#### WEEK 5: Sensor-Trust Index Formulation ($S_{\text{trust}}$)
* **Dates:** 29/08/2026 – 04/09/2026
* **Tasks Undertaken:**
  * Formulated mathematical trust model: $S_{\text{trust}} = \min(T_{\text{range}}, T_{\text{flat}}, T_{\text{drift}}, T_{\text{missing}})$.
  * Implemented rolling variance checks for flatline/stuck ADC detection.
  * Implemented point-to-point rate-of-change checks for unrealistic calibration drift.
* **Discussion with Guide:**
  * Verified edge corner cases (e.g., thermal spikes vs. sensor noise).
* **Status:** Completed.

#### WEEK 6: Machine Learning Engine & Deep Learning Autoencoder
* **Dates:** 05/09/2026 – 11/09/2026
* **Tasks Undertaken:**
  * Implemented Isolation Forest for spatial multivariate anomaly detection.
  * Built PyTorch LSTM Autoencoder sequence model to detect temporal dynamics via reconstruction loss $\text{MSE}(X, \hat{X})$.
  * Formulated **Sensor-Trust Masking equation**: $S_{\text{ML\_masked}} = S_{\text{ML}} \cdot S_{\text{trust}}$ when $S_{\text{trust}} < 0.40$.
* **Discussion with Guide:**
  * Evaluated false-positive suppression; mathematical masking effectively blocked spurious alarms.
* **Status:** Completed.

#### WEEK 7: Digital Twin Dependency Graph & Root-Cause Analysis
* **Dates:** 12/09/2026 – 18/09/2026
* **Tasks Undertaken:**
  * Modeled smart campus assets as a NetworkX directed dependency graph $G=(V, E)$.
  * Formulated root-cause candidate probability ranking equation $P(C_i)$.
  * Implemented reverse topological traversal during cascading multi-node failures.
* **Discussion with Guide:**
  * Guide commended the graph twin representation and suggested verifying with 5 cascading scenarios.
* **Status:** Completed.

#### WEEK 8: Integration, FastAPI Backend & Streamlit Live Cockpit
* **Dates:** 19/09/2026 – 25/09/2026
* **Tasks Undertaken:**
  * Built FastAPI REST & WebSocket endpoints (`/telemetry`, `/trust`, `/digital-twin`, `/overrides`).
  * Created live Streamlit monitoring dashboard showing live asset graphs, gauges, and manual relay overrides.
  * Created unit test suites for all backend, gateway, and firmware modules (21/21 tests passing).
* **Discussion with Guide:**
  * Demonstrated live dashboard and simulated fault triggers to guide.
* **Status:** Completed.

#### WEEK 9: Controlled Fault Injection & Rigorous Benchmark Suite
* **Dates:** 26/09/2026 – 02/10/2026
* **Tasks Undertaken:**
  * Developed automated testbed (`simulator/run_experiments.py`) testing 5 fault scenarios:
    1. Sensor drift (+25°C jump).
    2. Thermal-electrical cascade overload (22.5A + 74°C).
    3. Water leak hazard.
    4. WAN network disconnect (100 frames).
    5. Manual hardware E-Stop press.
  * Verified empirical results: **5.68 ms trip latency**, **100% false-positive suppression**, **100% data preservation**.
* **Discussion with Guide:**
  * Guide verified experimental results against theoretical predictions.
* **Status:** Completed.

#### WEEK 10: Research Paper Writing, KSCST Proposal & Review-2 Readiness
* **Dates:** 03/10/2026 – Present
* **Tasks Undertaken:**
  * Drafted full 10-page IEEE conference paper with 20 citations (`docs/ieee_research_paper.tex`).
  * Prepared KSCST Student Project Programme proposal application (`docs/kscst_research_proposal.md`).
  * Prepared Capstone Review-2 presentation deck (`docs/review2_presentation_slides.md`).
  * Pushed verified codebase to GitHub: [https://github.com/bharath-105/VeriInfra](https://github.com/bharath-105/VeriInfra).
* **Discussion with Guide:**
  * Review-2 deliverables approved; paper finalized for conference/journal submission.
* **Status:** Ready for Review-2 evaluation.

---

### GUIDE VERIFICATION & SIGNATURES

| Role | Name | Signature | Date |
| :--- | :--- | :---: | :---: |
| **Project Guide** | Dr. Manikandan Moovendran | ________________ | ____________ |
| **Co-Guide** | Prof. Akhil Pratap Singh | ________________ | ____________ |
| **HOD (CSE AI&ML)** | Department Head | ________________ | ____________ |
