# VeriInfra: A Resilient Edge AI Digital Twin with Physical Safety Overrides for Smart Infrastructure Monitoring

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FreeRTOS](https://img.shields.io/badge/ESP32-FreeRTOS-orange.svg)](https://www.espressif.com/)
[![Tests](https://img.shields.io/badge/Tests-Passing%20(21%2F21)-brightgreen.svg)](#testing)

An edge-native Cyber-Physical Digital Twin framework engineered to eliminate false-alarm emergency trips caused by drifting or faulty sensors while guaranteeing deterministic, sub-millisecond physical override protection during genuine electrical, thermal, and liquid hazards.

---

## 🏛️ Authors & Affiliation

* **Bharath N Menon** (`eng23am0113@dsu.edu.in`)
* **Mohammad Yaseen Arafat** (`eng23am0254@dsu.edu.in`)
* **Dr. Manikandan Moovendran** (`manikandan-aiml@dsu.edu.in`)
* **Prof. Akhil Pratap Singh** (`akhilpratap-aimla@dsu.edu.in`)

*Department of Computer Science & Engineering (AI & ML), Dayananda Sagar University, Bengaluru, India*

---

## 🚀 Key Highlights & Benchmarks

* **Sub-10ms Trip Latency**: Empirical mean trip latency of **5.68 ms** (17.6× faster than the 100 ms theoretical target).
* **100% False-Positive Suppression**: Novel **Sensor-Trust Index ($S_{\text{trust}}$)** masks AI anomaly scores during hardware sensor flatline or drift, completely preventing unwarranted power trips.
* **100% Offline Telemetry Preservation**: Gateway circular SQLite queue guarantees zero telemetry drops during WAN/cloud outages.
* **Hardware E-Stop Interrupt Dominance**: Silicon-level GPIO hardware ISR trips physical relays in **0.84 ms**, overriding any software hangs.
* **Top-1 Root-Cause Ranking**: Precision@1 of **100.0%** across cascading asset failure topologies using NetworkX directed dependency graphs.

---

## 📁 Repository Structure

```
veriinfra/
├── backend/                  # FastAPI REST & WebSocket Server
│   ├── app/
│   │   ├── api/v1/           # Telemetry, trust, override, and digital twin endpoints
│   │   ├── core/             # Configuration & DB connection
│   │   └── models/           # SQLAlchemy DB models & Pydantic schemas
│   └── tests/                # Backend API unit tests
├── dashboard/                # Streamlit live operational cockpit
│   └── app_streamlit.py
├── docker/                   # Docker deployment configurations (Mosquitto, etc.)
│   └── mosquitto.conf
├── docs/                     # Research papers and technical documentation
│   ├── ieee_research_paper.tex   # Full 10-page IEEE conference paper (LaTeX)
│   ├── project_report.md         # Comprehensive B.Tech project report
│   ├── viva_qa_and_demo_script.md# Evaluation defense guide & demo runbook
│   └── wiring_and_safety_guide.md# ESP32 pinouts & hardware wiring
├── firmware/                 # ESP32 C++ FreeRTOS Firmware (PlatformIO)
│   ├── include/              # Header files (drivers, overrides, mqtt)
│   ├── src/                  # Sensor acquisition, ISR, and relay control
│   └── platformio.ini        # PlatformIO configuration
├── gateway/                  # Edge Gateway Core & Hybrid AI Engine
│   ├── models/               # Pre-trained models (Isolation Forest)
│   ├── src/
│   │   ├── digital_twin/     # NetworkX asset graph & root-cause ranker
│   │   ├── ingestion/        # MQTT subscriber & SQLite offline buffer
│   │   ├── ml_engine/        # Isolation Forest + PyTorch LSTM Autoencoder
│   │   ├── safety/           # Deterministic 4-state Finite State Machine
│   │   └── trust_engine/     # Sensor-Trust Index calculator
│   └── tests/                # Gateway & AI unit test suite
└── simulator/                # Multi-node ESP32 & fault injection testbed
    ├── inject_faults.py      # Dynamic fault injection (drift, flatline, spike)
    ├── run_experiments.py    # Automated 5-scenario benchmark suite
    └── simulate_esp32_nodes.py
```

---

## 🛠️ Quick Start

### 1. Prerequisites
* Python 3.10+ (Recommended: 3.12)
* Eclipse Mosquitto MQTT Broker (or run via Docker)

### 2. Setup Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run Automated Experiments & Benchmarks
```bash
python simulator/run_experiments.py
```

### 4. Run Test Suites
```bash
# Run Gateway & AI Unit Tests
python -m unittest discover -s gateway/tests

# Run Simulator Unit Tests
python -m unittest discover -s simulator/tests

# Run Backend API Unit Tests
python -m unittest discover -s backend/tests
```

### 5. Launch the Live Streamlit Dashboard
```bash
streamlit run dashboard/app_streamlit.py
```

---

## 📄 IEEE Conference Research Paper

The complete, peer-review-formatted IEEE conference research paper (10-page equivalent double-column format with 20 citations and mathematical formulations) is available in [docs/ieee_research_paper.tex](docs/ieee_research_paper.tex).

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
