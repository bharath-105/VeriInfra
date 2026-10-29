# KARNATAKA STATE COUNCIL FOR SCIENCE AND TECHNOLOGY (KSCST)
## Indian Institute of Science Campus, Bengaluru - 560012
### 47th / 48th SERIES OF STUDENT PROJECT PROGRAMME (SPP)
#### PROJECT PROPOSAL APPLICATION FORM (ENGINEERING STREAM)

---

### PART A: GENERAL INFORMATION

1. **Title of the Project:**  
   **VeriInfra: A Resilient Edge AI Digital Twin with Physical Safety Overrides for Smart Infrastructure Monitoring**

2. **Project Category / Area:**  
   Computer Science & Engineering / Artificial Intelligence & Machine Learning / IoT & Smart Infrastructure / Cyber-Physical Systems (CPS)

3. **Name of the Institution:**  
   Dayananda Sagar University (DSU)  
   School of Engineering, Devarakaggalahalli, Kanakapura Road, Bengaluru, Karnataka - 562112

4. **Name of the Department:**  
   Department of Computer Science & Engineering (Artificial Intelligence & Machine Learning)

5. **Details of Project Students:**
   * **Student 1 (Team Leader):**
     * Name: **Bharath N Menon**
     * USN / Roll No: `ENG23AM0113`
     * Email: `eng23am0113@dsu.edu.in` / `bharathmenon105@gmail.com`
     * Semester & Branch: 7th/8th Semester, B.Tech CSE (AI & ML)
   * **Student 2:**
     * Name: **Mohammad Yaseen Arafat**
     * USN / Roll No: `ENG23AM0254`
     * Email: `eng23am0254@dsu.edu.in`
     * Semester & Branch: 7th/8th Semester, B.Tech CSE (AI & ML)

6. **Details of Project Guide(s):**
   * **Project Guide:**
     * Name: **Dr. Manikandan Moovendran**
     * Designation: Associate Professor / Faculty Guide
     * Department: Dept. of CSE (AI & ML), Dayananda Sagar University
     * Email: `manikandan-aiml@dsu.edu.in`
   * **Co-Guide:**
     * Name: **Prof. Akhil Pratap Singh**
     * Designation: Assistant Professor
     * Department: Dept. of CSE (AI & ML), Dayananda Sagar University
     * Email: `akhilpratap-aimla@dsu.edu.in`

---

### PART B: TECHNICAL DETAILS OF THE PROJECT

#### 1. Introduction & Background:
Educational institutions, student hostels, research laboratories, and server server rooms across Karnataka face critical challenges in monitoring ambient environmental conditions, electrical safety, and utility integrity. Existing commercial building management systems (BMS) are prohibitively expensive for localized deployment, rely heavily on constant cloud Internet connectivity, and frequently trigger costly false emergency shutdowns due to low-cost sensor drift or noise spikes. 

**VeriInfra** addresses this challenge by providing an affordable, edge-native Cyber-Physical Digital Twin architecture that couples distributed low-power microcontrollers (ESP32) with localized machine learning (Isolation Forest + LSTM Autoencoder) and a deterministic hardware safety override mechanism.

#### 2. Need for the Project & Societal Relevance in Karnataka:
* **Prevention of Electrical & Fire Hazards in Academic/Hostel Buildings:** Academic hostels, laboratories, and computer server rooms in Karnataka house high electrical loads. Electrical short-circuits, water leakages near electrical panels, and thermal overloads represent severe fire hazards.
* **Resilience During Power / Internet Outages:** Standard cloud IoT systems fail during heavy rainfall, monsoons, or network disruptions common in semi-urban and rural Karnataka campuses. VeriInfra's local edge architecture guarantees 100% data preservation and continuous physical safety protection without Internet.
* **Elimination of False-Alarm Losses:** Cheap sensors degrade quickly in tropical climates. VeriInfra's novel **Sensor-Trust Index ($S_{\text{trust}}$)** prevents false power cuts, ensuring uninterrupted academic operations.

#### 3. Objectives of the Project:
1. To engineer a resilient, edge-native Cyber-Physical Digital Twin monitoring system using distributed ESP32 microcontrollers and a local edge gateway.
2. To formulate a multi-factor mathematical **Sensor-Trust Index ($S_{\text{trust}}$)** evaluating physical range bounds, rolling variance flatlines, rate-of-change drift, and packet timeliness to distinguish faulty hardware from real hazards.
3. To develop a dual-stage hybrid AI anomaly detection pipeline combining **Isolation Forest** (spatial isolation) and **PyTorch LSTM Autoencoder** (temporal reconstruction error) with dynamic Sensor-Trust Masking.
4. To model campus asset dependency topology using a **NetworkX directed graph ($G=(V, E)$)** capable of automated candidate root-cause ranking ($P(C_i)$) during cascading utility failures.
5. To implement deterministic hardware interrupt dominance via physical optocoupler relays and an emergency mushroom switch ($<1\text{ ms}$ response time), overriding software states.

#### 4. Methodology & Implementation Plan:
1. **Sensor & Actuation Layer:** ESP32 nodes running FreeRTOS collect telemetry from DHT22 (temp/humidity), SCT-013/ACS712 (AC current), ADXL345 (vibration), MQ-135 (air quality/smoke), and resistive water leak probes.
2. **Communication & Offline Queueing:** Nodes stream telemetry via lightweight MQTT over local Wi-Fi. An edge gateway running an SQLite circular buffer preserves telemetry during network disconnections.
3. **Sensor-Trust Scorer:** Computes $S_{\text{trust}} = \min(T_{\text{range}}, T_{\text{flat}}, T_{\text{drift}}, T_{\text{missing}})$. If a sensor fails, its trust index collapses.
4. **Hybrid Anomaly Scoring:** Evaluates $S_{\text{hybrid}} = 0.40 S_{\text{ML\_masked}} + 0.40 S_{\text{rule}} + 0.10 S_{\text{causal}} + 0.10 (1 - S_{\text{trust}})$. When $S_{\text{trust}} < 0.40$, Sensor-Trust Masking attenuates ML anomaly scores, suppressing false alarms.
5. **Digital Twin Root-Cause Localization:** Computes $P(C_i) \propto \text{criticality}_i \cdot S_{\text{anomaly\_i}} \cdot \prod w_{\text{dep}}(e)$ using reverse topological graph traversal.

#### 5. Tangible Outcomes & Measurable Deliverables:
* Fully working prototype deployed on ESP32 hardware and local Edge Gateway.
* Web-based live monitoring cockpit developed in Streamlit & FastAPI.
* Verified benchmark results:
  * Mean trip latency: **5.68 ms** (exceeding 100 ms target).
  * False-positive suppression rate: **100.0%**.
  * Offline data preservation: **100.0%** across 100 consecutive frames.
* Published/Submitted IEEE Conference Research Paper: *VeriInfra: A Resilient Edge AI Digital Twin with Physical Safety Overrides for Smart Infrastructure Monitoring*.
* Open-source repository: [https://github.com/bharath-105/VeriInfra](https://github.com/bharath-105/VeriInfra).

---

### PART C: ESTIMATED BUDGET & BREAKDOWN

| Sl. No. | Component / Item Description | Quantity | Estimated Cost (INR) |
| :---: | :--- | :---: | :---: |
| 1 | ESP32 NodeMCU-32S Microcontroller Development Boards | 2 Nos. | ₹1,600 |
| 2 | Non-Invasive AC Current Transformers (SCT-013-000) & ACS712 Modules | 2 Nos. | ₹1,400 |
| 3 | DHT22 High-Precision Temperature & Humidity Sensors | 2 Nos. | ₹800 |
| 4 | ADXL345 3-Axis Digital Accelerometers (I2C) | 2 Nos. | ₹700 |
| 5 | MQ-135 Air Quality & Hazardous Gas Sensing Modules | 2 Nos. | ₹600 |
| 6 | Resistive Grid Water Leak Probes & Comparator Modules | 2 Nos. | ₹400 |
| 7 | Optocoupler-Isolated 5V Relay Modules (10A 250VAC) | 2 Nos. | ₹500 |
| 8 | Industrial Mushroom Latching Emergency-Stop (E-Stop) Switch | 1 No. | ₹650 |
| 9 | Prototyping Chassis, Acrylic Enclosure, DC Fans, Terminal Blocks & Wiring | 1 Set | ₹2,500 |
| 10 | IEEE Conference / Journal Paper Registration Assistance & Printing | - | ₹3,350 |
| | **TOTAL ESTIMATED BUDGET REQUESTED:** | | **₹12,500** |

---

### PART D: DECLARATION & ENDORSEMENTS

**Declaration by the Students:**  
We hereby declare that the project proposal entitled *"VeriInfra: A Resilient Edge AI Digital Twin with Physical Safety Overrides for Smart Infrastructure Monitoring"* is an original work undertaken by our team under the guidance of Dr. Manikandan Moovendran and Prof. Akhil Pratap Singh.

* **Bharath N Menon (ENG23AM0113)** — Signature: __________________  
* **Mohammad Yaseen Arafat (ENG23AM0254)** — Signature: __________________

**Endorsement by the Project Guide & Head of Department:**  
This is to certify that the project proposal submitted by the students has been reviewed, aligns with the departmental research thrust in Cyber-Physical Systems and Edge AI, and is recommended for submission under the KSCST Student Project Programme.

* **Dr. Manikandan Moovendran** (Project Guide) — Signature: __________________  
* **Prof. Akhil Pratap Singh** (Co-Guide) — Signature: __________________  
* **Head of Department (CSE AI&ML)** — Signature & Seal: __________________  
