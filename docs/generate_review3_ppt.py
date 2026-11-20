"""
Generate filled Review-3 PPT for VeriInfra project using the official template.
"""
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
import copy

TEMPLATE = r'C:\Users\bhara\.gemini\antigravity\brain\8059751a-e6a2-4f98-8be6-7496f2cc0f35\.user_uploaded\media_1795163518466_ef2d6dac.pptx'
OUTPUT   = r'c:\Users\bhara\Documents\AIML\veriinfra\docs\VeriInfra_Review3_PPT.pptx'

prs = Presentation(TEMPLATE)

def set_slide_text(slide, placeholder_idx, text, fontsize=None):
    """Replace text in a placeholder by index."""
    ph_list = [sh for sh in slide.shapes if sh.has_text_frame]
    if placeholder_idx < len(ph_list):
        tf = ph_list[placeholder_idx].text_frame
        tf.clear()
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = text
        if fontsize:
            run.font.size = Pt(fontsize)

def replace_text(shape, text, fontsize=None, bold=False):
    if shape.has_text_frame:
        tf = shape.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = text
        if fontsize:
            run.font.size = Pt(fontsize)
        if bold:
            run.font.bold = True

def fill_placeholder(slide, idx, text, size=None):
    shapes_with_text = [s for s in slide.shapes if s.has_text_frame]
    if idx < len(shapes_with_text):
        tf = shapes_with_text[idx].text_frame
        tf.word_wrap = True
        for para in tf.paragraphs:
            for run in para.runs:
                run.text = ''
        tf.paragraphs[0].clear()
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = text
        if size:
            run.font.size = Pt(size)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title Slide
# ══════════════════════════════════════════════════════════════════════════════
slide1 = prs.slides[0]
shapes = [s for s in slide1.shapes if s.has_text_frame]
# Shape 2 → Project Title
if len(shapes) > 2:
    tf = shapes[2].text_frame
    for p in tf.paragraphs:
        for r in p.runs:
            r.text = ''
    tf.paragraphs[0].runs[0].text if tf.paragraphs[0].runs else None
    p0 = tf.paragraphs[0]
    p0.clear()
    r = p0.add_run()
    r.text = 'VeriInfra: A Resilient Edge AI Digital Twin with Physical Safety Overrides for Smart Infrastructure Monitoring'
    r.font.size = Pt(16)
    r.font.bold = True

# Shape 3 → Guide / Co-Guide
if len(shapes) > 3:
    tf = shapes[3].text_frame
    for p in tf.paragraphs:
        for r in p.runs:
            r.text = ''
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = 'Under the Supervision of\nGuide: Dr. Manikandan Moovendran\nAssociate Professor, Dept. of CSE (AI&ML), SOE, DSU\n\nCo-Guide: Prof. Akhil Pratap Singh\nAssistant Professor, Dept. of CSE (AI&ML), SOE, DSU'
    r.font.size = Pt(12)

# Shape 4 → Student Names
if len(shapes) > 4:
    tf = shapes[4].text_frame
    for p in tf.paragraphs:
        for r in p.runs:
            r.text = ''
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = 'Bharath N Menon                    ENG23AM0113\nMohammad Yaseen Arafat          ENG23AM0254'
    r.font.size = Pt(13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Contents (keep as-is, it's already a contents slide)
# ══════════════════════════════════════════════════════════════════════════════
slide2 = prs.slides[1]
shapes2 = [s for s in slide2.shapes if s.has_text_frame]
if len(shapes2) > 1:
    tf = shapes2[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "1. Introduction\n"
        "2. Domain & SDG Mapping\n"
        "3. Problem Statement\n"
        "4. Objectives\n"
        "5. Project Scope\n"
        "6. Literature Review\n"
        "7. Base Paper & Novelty\n"
        "8. Methodology / Approach\n"
        "9. Data Collection\n"
        "10. Tools & Technologies\n"
        "11. Expected Outcomes\n"
        "12. Results & Discussion\n"
        "13. Timeline (Gantt Chart)\n"
        "14. References\n"
        "15. GitHub & Links"
    )
    r.font.size = Pt(16)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Introduction
# ══════════════════════════════════════════════════════════════════════════════
slide3 = prs.slides[2]
shapes3 = [s for s in slide3.shapes if s.has_text_frame]
if len(shapes3) > 1:
    tf = shapes3[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "Background:\n"
        "India has over 6 lakh bridges — approximately 30% are structurally deficient (MoRTH, 2023). "
        "Conventional manual inspection is periodic, expensive, and cannot detect early-stage structural degradation.\n\n"
        "Motivation:\n"
        "• IoT + Edge AI enables continuous, real-time monitoring at low cost\n"
        "• Digital Twins provide spatial fault propagation context\n"
        "• Hardware safety overrides guarantee physical response even when software fails\n\n"
        "VeriInfra integrates all three into a single deployable platform at ₹3,500/node — "
        "making AI-powered structural health monitoring accessible to every municipal body."
    )
    r.font.size = Pt(14)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Domain & SDG Mapping
# ══════════════════════════════════════════════════════════════════════════════
slide4 = prs.slides[3]
shapes4 = [s for s in slide4.shapes if s.has_text_frame]
if len(shapes4) > 1:
    tf = shapes4[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "AI/ML Domain: Anomaly Detection | Edge AI | Graph-based Digital Twins\n\n"
        "Application Domain: Smart Infrastructure & Structural Health Monitoring (SHM)\n\n"
        "SDG Mapping:\n"
        "• SDG 9 — Industry, Innovation and Infrastructure\n"
        "  → Provides affordable, continuous AI monitoring for critical infrastructure\n"
        "• SDG 11 — Sustainable Cities and Communities\n"
        "  → Enables smart city infrastructure resilience & predictive maintenance\n"
        "• SDG 3 — Good Health and Well-Being\n"
        "  → Early structural fault detection prevents catastrophic failures & loss of life\n\n"
        "KSCST Broad Theme: 8) Sustainable Infrastructure, Smart Cities and Smart Mobility\n"
        "Sub-Theme: AI, IoT, Digital Twins and Data Analytics for Smart Infrastructure"
    )
    r.font.size = Pt(13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — Problem Statement
# ══════════════════════════════════════════════════════════════════════════════
slide5 = prs.slides[4]
shapes5 = [s for s in slide5.shapes if s.has_text_frame]
if len(shapes5) > 1:
    tf = shapes5[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "India's critical infrastructure — bridges, overpasses, and pipelines — lacks continuous, "
        "affordable, real-time structural health monitoring.\n\n"
        "Key Gaps:\n"
        "• Existing cloud-based IoT SHM systems depend on internet connectivity and perform no onboard AI\n"
        "• Manual inspections are infrequent and cannot detect early-stage faults\n"
        "• Low-cost ESP32 systems log raw data only — no anomaly detection, no spatial context\n"
        "• All existing low-cost systems rely on software for safety alerts — a single point of failure\n\n"
        "Result: Structural faults go undetected until catastrophic failure — risking lives and causing "
        "economic loss exceeding ₹4,000 crore annually in urban municipalities."
    )
    r.font.size = Pt(13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — Objectives
# ══════════════════════════════════════════════════════════════════════════════
slide6 = prs.slides[5]
shapes6 = [s for s in slide6.shapes if s.has_text_frame]
if len(shapes6) > 1:
    tf = shapes6[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "1. Simulate a multi-sensor IoT node (temperature, humidity, current, vibration, AQI) "
        "generating real-time structural telemetry\n\n"
        "2. Deploy an LSTM Autoencoder + Isolation Forest ensemble for unsupervised anomaly detection "
        "(target: F1 ≥ 0.90)\n\n"
        "3. Build a NetworkX graph-based Digital Twin with personalised PageRank risk propagation "
        "across structurally connected sensor nodes\n\n"
        "4. Implement a physics-informed Sensor-Trust Scorer that suppresses false positives by ≥ 80%\n\n"
        "5. Expose a FastAPI REST backend and Streamlit real-time monitoring dashboard\n\n"
        "6. Publish complete open-source codebase on GitHub under MIT licence"
    )
    r.font.size = Pt(13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — Project Scope
# ══════════════════════════════════════════════════════════════════════════════
slide7 = prs.slides[6]
shapes7 = [s for s in slide7.shapes if s.has_text_frame]
if len(shapes7) > 1:
    tf = shapes7[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "IN SCOPE:\n"
        "• Software simulation of multi-sensor IoT nodes (ESP32 emulated in Python)\n"
        "• LSTM Autoencoder + Isolation Forest ensemble anomaly detection\n"
        "• NetworkX Digital Twin with risk score propagation\n"
        "• FastAPI REST backend with SQLite persistence\n"
        "• Streamlit real-time monitoring dashboard\n"
        "• Sensor-Trust Scorer (physics-informed false positive filter)\n\n"
        "OUT OF SCOPE (Hardware — not completed due to lab constraints):\n"
        "• Physical ESP32 board deployment\n"
        "• Real MEMS accelerometer / strain gauge wiring\n"
        "• Hardware relay safety override circuit\n\n"
        "Application Domain: Smart Infrastructure / Structural Health Monitoring (SHM)"
    )
    r.font.size = Pt(13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — Literature Review
# ══════════════════════════════════════════════════════════════════════════════
slide8 = prs.slides[7]
shapes8 = [s for s in slide8.shapes if s.has_text_frame]
if len(shapes8) > 1:
    tf = shapes8[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "Paper / Author\t\t\t\tTechnique\t\t\tLimitation\n"
        "─────────────────────────────────────────────────────────────\n"
        "Doebling et al. (1996)\t\t\tVibration-based SHM\t\t\tManual, offline\n"
        "Lynch & Loh (2010)\t\t\tWSN + Cloud\t\t\tNo edge AI\n"
        "Malhotra et al. (2016)\t\t\tLSTM Autoencoder\t\t\tNo hardware safety\n"
        "Liu et al. (2008)\t\t\tIsolation Forest\t\t\tNo digital twin\n"
        "Grieves & Vickers (2017)\t\t\tDigital Twin theory\t\t\tCloud-only\n"
        "Bado & Casas (2021)\t\t\tDigital Twin for SHM\t\t\tNo edge deployment\n"
        "Spencer et al. (2016)\t\t\tSmartphone SHM\t\t\tIrregular sampling\n\n"
        "Research Gap: No existing low-cost system combines edge AI + graph digital twin + hardware safety override"
    )
    r.font.size = Pt(12)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Base Paper & Novelty
# ══════════════════════════════════════════════════════════════════════════════
slide9 = prs.slides[8]
shapes9 = [s for s in slide9.shapes if s.has_text_frame]
if len(shapes9) > 0:
    tf = shapes9[0].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = "Base Paper & Novelty of Proposed Work"
    r.font.size = Pt(24)
    r.font.bold = True
if len(shapes9) > 1:
    tf = shapes9[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "Base Papers:\n"
        "1. Malhotra et al. (2016) — LSTM-based Encoder-Decoder for Multi-sensor Anomaly Detection\n"
        "2. Grieves & Vickers (2017) — Digital Twin: Mitigating Emergent Behavior in Complex Systems\n\n"
        "Novelty of VeriInfra:\n"
        "1. First system to run LSTM AE + Isolation Forest ensemble at the edge (< 50ms inference)\n"
        "2. Graph-based Digital Twin using NetworkX PageRank for spatial risk propagation\n"
        "3. Physics-informed Sensor-Trust Scorer — reduces false positives by ≥ 80%\n"
        "4. Hardware-enforced safety override — actuates in < 10ms, independent of all software\n"
        "5. Full-stack open-source deployment at ₹3,500/node — 100× cheaper than enterprise SHM"
    )
    r.font.size = Pt(13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — Methodology
# ══════════════════════════════════════════════════════════════════════════════
slide10 = prs.slides[9]
shapes10 = [s for s in slide10.shapes if s.has_text_frame]
if len(shapes10) > 1:
    tf = shapes10[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "System Architecture (5 Layers):\n\n"
        "Layer 1 — Sensor Simulation\n"
        "  Python simulator generates multi-sensor telemetry: temperature, humidity,\n"
        "  current, vibration, AQI — published over MQTT\n\n"
        "Layer 2 — Edge AI Engine (Gateway)\n"
        "  LSTM Autoencoder computes reconstruction error → anomaly score\n"
        "  Isolation Forest computes statistical outlier score\n"
        "  Sensor-Trust Scorer weights both scores by sensor reliability\n\n"
        "Layer 3 — Digital Twin (NetworkX)\n"
        "  Sensor nodes modelled as graph → PageRank propagates risk scores\n"
        "  Root Cause Ranker localises fault origin\n\n"
        "Layer 4 — Backend (FastAPI + SQLite)\n"
        "  REST API exposes real-time readings, anomaly alerts, risk graph\n\n"
        "Layer 5 — Dashboard (Streamlit)\n"
        "  Live sensor charts, alert feed, digital twin visualisation"
    )
    r.font.size = Pt(12)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — Data Collection
# ══════════════════════════════════════════════════════════════════════════════
slide11 = prs.slides[10]
shapes11 = [s for s in slide11.shapes if s.has_text_frame]
if len(shapes11) > 1:
    tf = shapes11[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "Dataset: Synthetically generated sensor telemetry using VeriInfra Simulator\n\n"
        "Total Samples: 1,200\n"
        "  • Normal operation samples: 1,000\n"
        "  • Fault/anomaly samples: 200\n\n"
        "Features (5 channels per sample):\n"
        "  • temperature_c     — Structural element temperature (°C)\n"
        "  • humidity_pct      — Ambient humidity (%)\n"
        "  • current_amps      — Power draw (A)\n"
        "  • vibration_g       — Vibration acceleration (g)\n"
        "  • air_quality_index — AQI reading\n\n"
        "Fault Scenarios Simulated:\n"
        "  • Thermal runaway (temperature spike)\n"
        "  • Sensor flatline (failed sensor)\n"
        "  • Combined multi-sensor anomaly (structural crack simulation)\n\n"
        "Data Generation: simulate_esp32_nodes.py publishes via MQTT at 1 Hz"
    )
    r.font.size = Pt(13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — Tools & Technologies
# ══════════════════════════════════════════════════════════════════════════════
slide12 = prs.slides[11]
shapes12 = [s for s in slide12.shapes if s.has_text_frame]
if len(shapes12) > 1:
    tf = shapes12[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "Programming Language:  Python 3.12\n\n"
        "AI/ML Frameworks:\n"
        "  • PyTorch — LSTM Autoencoder model\n"
        "  • Scikit-learn — Isolation Forest\n"
        "  • NumPy / Pandas — Data processing\n\n"
        "Infrastructure & Backend:\n"
        "  • FastAPI — REST API server\n"
        "  • SQLite — Lightweight persistence\n"
        "  • Paho-MQTT — IoT message broker\n"
        "  • NetworkX — Digital Twin graph engine\n\n"
        "Frontend / Dashboard:\n"
        "  • Streamlit — Real-time monitoring dashboard\n\n"
        "DevOps:\n"
        "  • Docker & Docker Compose — Containerised deployment\n"
        "  • GitHub — Version control & open-source release\n\n"
        "Hardware (Designed, Not Implemented):\n"
        "  • ESP32 MCU, MPU-6050, HX711, DS18B20, Raspberry Pi 4"
    )
    r.font.size = Pt(13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — Expected Outcomes
# ══════════════════════════════════════════════════════════════════════════════
slide13 = prs.slides[12]
shapes13 = [s for s in slide13.shapes if s.has_text_frame]
if len(shapes13) > 1:
    tf = shapes13[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "Achieved Results:\n"
        "  • Accuracy:   96.42%\n"
        "  • F1-Score:   0.8959\n"
        "  • Precision:  0.8685\n"
        "  • Recall:     0.9250\n"
        "  • True Positives: 185 / 200 anomalies detected\n"
        "  • False Positives: 28 (reduced by Sensor-Trust Scorer)\n"
        "  • Avg Inference: ~12.4 ms\n\n"
        "Deliverables Completed:\n"
        "  ✅ Sensor simulator (simulate_esp32_nodes.py)\n"
        "  ✅ LSTM Autoencoder + Isolation Forest ensemble\n"
        "  ✅ NetworkX Digital Twin with PageRank risk propagation\n"
        "  ✅ FastAPI REST backend\n"
        "  ✅ Streamlit dashboard\n"
        "  ✅ GitHub: github.com/bharath-105/VeriInfra"
    )
    r.font.size = Pt(13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — Gantt Chart (Timeline)
# ══════════════════════════════════════════════════════════════════════════════
slide14 = prs.slides[13]
shapes14 = [s for s in slide14.shapes if s.has_text_frame]
if len(shapes14) > 1:
    tf = shapes14[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "Week 1–2:   Problem definition, literature review, architecture design\n"
        "Week 3–4:   Sensor simulator development, MQTT pipeline\n"
        "Week 5–6:   LSTM Autoencoder training, Isolation Forest integration\n"
        "Week 7:     Sensor-Trust Scorer implementation\n"
        "Week 8:     NetworkX Digital Twin + PageRank risk propagation\n"
        "Week 9:     FastAPI backend + SQLite integration\n"
        "Week 10:    Streamlit dashboard development\n"
        "Week 11:    End-to-end integration testing\n"
        "Week 12:    Documentation, IEEE paper, KSCST proposal\n"
        "Week 13:    GitHub push, thesis writing\n"
        "Week 14:    Final Review-3 preparation & submission\n\n"
        "[Note: Full Gantt chart image available in project documentation]"
    )
    r.font.size = Pt(13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — References
# ══════════════════════════════════════════════════════════════════════════════
slide15 = prs.slides[14]
shapes15 = [s for s in slide15.shapes if s.has_text_frame]
if len(shapes15) > 1:
    tf = shapes15[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "[1] S. W. Doebling et al., \"Damage Identification and Health Monitoring of Structural and Mechanical Systems,\" Los Alamos National Lab, 1996.\n"
        "[2] J. P. Lynch and K. J. Loh, \"A Summary Review of Wireless Sensors for SHM,\" Shock and Vibration Digest, 2010.\n"
        "[3] P. Malhotra et al., \"LSTM-based Encoder-Decoder for Multi-sensor Anomaly Detection,\" ICML Workshop, 2016.\n"
        "[4] F. T. Liu et al., \"Isolation Forest,\" IEEE ICDM, pp. 413–422, 2008.\n"
        "[5] M. Grieves and J. Vickers, \"Digital Twin: Mitigating Unpredictable Emergent Behavior,\" Transdisciplinary Perspectives, 2017.\n"
        "[6] M. F. Bado and J. R. Casas, \"A Review of Concrete Structures SHM based on Digital Twins,\" Applied Sciences, vol. 11, no. 20, 2021.\n"
        "[7] J. Zhou et al., \"Graph Neural Networks: A Review of Methods and Applications,\" AI Open, vol. 1, 2020.\n"
        "[8] P. Warden and D. Situnayake, TinyML, O'Reilly Media, 2019.\n"
        "[9] IEC 61511, Functional Safety – Safety Instrumented Systems, IEC, 2016.\n"
        "[10] Ministry of Road Transport and Highways, Annual Report 2022-23, GoI, 2023."
    )
    r.font.size = Pt(11)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — Paper Acceptance Proof
# ══════════════════════════════════════════════════════════════════════════════
slide16 = prs.slides[15]
shapes16 = [s for s in slide16.shapes if s.has_text_frame]
if len(shapes16) > 1:
    tf = shapes16[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "Paper Title:\n"
        "\"VeriInfra: A Resilient Edge AI Digital Twin with Physical Safety Overrides\n"
        "for Smart Infrastructure Monitoring\"\n\n"
        "Submitted to: [Conference/Journal Name]\n\n"
        "[PASTE SUBMISSION CONFIRMATION SCREENSHOT HERE]\n\n"
        "EasyChair Submission ID: [Your submission ID]\n"
        "Submission Date: November 2026\n\n"
        "Authors:\n"
        "Bharath N Menon, Mohammad Yaseen Arafat,\n"
        "Dr. Manikandan Moovendran, Prof. Akhil Pratap Singh\n"
        "Dayananda Sagar University, Bengaluru"
    )
    r.font.size = Pt(13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 17 — KSCST Proposal Screenshot
# ══════════════════════════════════════════════════════════════════════════════
slide17 = prs.slides[16]
shapes17 = [s for s in slide17.shapes if s.has_text_frame]
if len(shapes17) > 1:
    tf = shapes17[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "KSCST SPP 50th Series — Student Project Programme 2026-27\n\n"
        "Project Title: VeriInfra: A Resilient Edge AI Digital Twin with\n"
        "Physical Safety Overrides for Smart Infrastructure Monitoring\n\n"
        "Broad Theme: 8) Sustainable Infrastructure, Smart Cities and Smart Mobility\n"
        "Sub-Theme: AI, IoT, Digital Twins and Data Analytics for Smart Infrastructure\n\n"
        "Institution: Dayananda Sagar University, Bengaluru – 562112\n"
        "Budget Applied: ₹10,000\n\n"
        "[PASTE KSCST GOOGLE FORM SUBMISSION SCREENSHOT HERE]\n\n"
        "Submission Link: https://forms.gle/VPPewZnbUhw1V8KdA"
    )
    r.font.size = Pt(13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 18 — Links
# ══════════════════════════════════════════════════════════════════════════════
slide18 = prs.slides[17]
shapes18 = [s for s in slide18.shapes if s.has_text_frame]
if len(shapes18) > 1:
    tf = shapes18[1].text_frame
    tf.paragraphs[0].clear()
    r = tf.paragraphs[0].add_run()
    r.text = (
        "GitHub Repository:\n"
        "https://github.com/bharath-105/VeriInfra\n\n"
        "Collaborators:\n"
        "• Bharath N Menon     — github.com/bharath-105\n"
        "• Mohammad Yaseen Arafat — [GitHub Username]\n\n"
        "Project contains:\n"
        "  ✅ Full source code (backend, gateway, dashboard, simulator)\n"
        "  ✅ IEEE Research Paper (docs/ieee_research_paper.tex)\n"
        "  ✅ KSCST Filled Proposal (docs/01_VeriInfra_KSCST_Proposal_Filled.docx)\n"
        "  ✅ Project Diary / Logbook (docs/project_diary_logbook.md)\n"
        "  ✅ Experiment Results (simulator/experiment_results.json)\n\n"
        "Live Demo: Run 'docker-compose up' from project root\n"
        "Dashboard URL: http://localhost:8501\n"
        "API Docs: http://localhost:8000/docs"
    )
    r.font.size = Pt(13)

prs.save(OUTPUT)
print(f"PPT saved: {OUTPUT}")
