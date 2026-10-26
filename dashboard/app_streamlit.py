"""
VeriInfra Streamlit Live Dashboard & Digital Twin Visualizer.

Run with:
    streamlit run dashboard/app_streamlit.py
"""

import time
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="VeriInfra | Edge AI Digital Twin",
    page_icon="🛡️",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        color: white;
    }
    .status-normal { color: #22c55e; font-weight: bold; }
    .status-advisory { color: #eab308; font-weight: bold; }
    .status-emergency { color: #ef4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ VeriInfra: Resilient Edge AI Digital Twin Dashboard")
st.subheader("Smart Infrastructure Monitoring & Physical Safety Override System")

# Sidebar - Node Selection & System Controls
st.sidebar.header("🕹️ Gateway Controls")

@st.cache_data(ttl=5)
def fetch_nodes():
    try:
        r = requests.get(f"{API_BASE}/nodes", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return [{"node_id": "node_esp32_01", "name": "Server Room Rack 01"}]

nodes = fetch_nodes()
node_ids = [n["node_id"] for n in nodes]
selected_node = st.sidebar.selectbox("Select Hardware Node", node_ids)

auto_refresh = st.sidebar.checkbox("Auto-Refresh Data (2s)", value=True)

st.sidebar.divider()
st.sidebar.header("🚨 Manual Physical Overrides")
relay_action = st.sidebar.radio("Relay 1 Action", ["ON (Energize Load)", "OFF (Trip Relay)"])
if st.sidebar.button("Execute Override Command", type="primary"):
    target_state = (relay_action == "ON (Energize Load)")
    payload = {
        "node_id": selected_node,
        "action": "TRIP_RELAY",
        "relay_id": 1,
        "target_state": target_state,
        "reason": "STREAMLIT_DASHBOARD_MANUAL"
    }
    try:
        r = requests.post(f"{API_BASE}/override/actuate", json=payload, timeout=3)
        if r.status_code == 200 and r.json().get("success"):
            st.sidebar.success(f"Command sent to {selected_node}: Relay 1 -> {target_state}")
        else:
            st.sidebar.error("Failed to execute override command.")
    except Exception as e:
        st.sidebar.error(f"Error connecting to backend: {e}")

# Fetch Telemetry Data
def fetch_latest_telemetry(node_id):
    try:
        r = requests.get(f"{API_BASE}/telemetry/live/{node_id}", timeout=2)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def fetch_telemetry_history(node_id):
    try:
        r = requests.get(f"{API_BASE}/telemetry/history?node_id={node_id}&limit=50", timeout=2)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def fetch_digital_twin_topology():
    try:
        r = requests.get(f"{API_BASE}/digital-twin/topology", timeout=2)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

telemetry = fetch_latest_telemetry(selected_node)
history = fetch_telemetry_history(selected_node)
topology = fetch_digital_twin_topology()

# Tab Layout
tab1, tab2, tab3 = st.tabs(["📊 Live Telemetry & Metrics", "🌐 Digital Twin Asset Graph", "📈 Historical Charts"])

with tab1:
    if telemetry:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Temperature", f"{telemetry.get('temperature_c', 0.0)} °C")
        with col2:
            st.metric("AC Current Load", f"{telemetry.get('current_amps', 0.0)} A")
        with col3:
            st.metric("Vibration", f"{telemetry.get('vibration_g', 0.0)} g")
        with col4:
            st.metric("Air Quality (AQI)", f"{telemetry.get('air_quality_index', 0.0)}")
        with col5:
            leak = telemetry.get("water_leak_detected", False)
            st.metric("Water Leak", "DETECTED 🚨" if leak else "CLEAR ✅")

        st.divider()

        # Gauge Charts
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_temp = go.Figure(go.Indicator(
                mode="gauge+number",
                value=telemetry.get("temperature_c", 0.0),
                title={'text': "Thermal Monitoring (°C)"},
                gauge={
                    'axis': {'range': [0, 80]},
                    'bar': {'color': "#3b82f6"},
                    'steps': [
                        {'range': [0, 35], 'color': "#1e293b"},
                        {'range': [35, 50], 'color': "#eab308"},
                        {'range': [50, 80], 'color': "#ef4444"}
                    ]
                }
            ))
            st.plotly_chart(fig_temp, use_container_width=True)

        with col_g2:
            fig_curr = go.Figure(go.Indicator(
                mode="gauge+number",
                value=telemetry.get("current_amps", 0.0),
                title={'text': "Electrical Current Load (Amps)"},
                gauge={
                    'axis': {'range': [0, 20]},
                    'bar': {'color': "#10b981"},
                    'steps': [
                        {'range': [0, 10], 'color': "#1e293b"},
                        {'range': [10, 15], 'color': "#eab308"},
                        {'range': [15, 20], 'color': "#ef4444"}
                    ]
                }
            ))
            st.plotly_chart(fig_curr, use_container_width=True)

    else:
        st.warning("Waiting for live telemetry stream from Gateway... Make sure simulator or backend is running.")

with tab2:
    st.subheader("🌐 NetworkX Digital Twin Topology & Risk Propagation Graph")
    if topology:
        nodes_df = pd.DataFrame(topology.get("nodes", []))
        st.dataframe(nodes_df, use_container_width=True)
        
        # Simple Network Graph Plot using Plotly
        edges = topology.get("edges", [])
        st.info(f"Digital Twin contains {topology.get('num_nodes')} assets and {topology.get('num_edges')} active dependency connections.")
    else:
        st.warning("Could not connect to Digital Twin topology endpoint.")

with tab3:
    st.subheader("📈 Time-Series Sensor Telemetry")
    if history:
        df = pd.DataFrame(history)
        fig_line = px.line(
            df, 
            x="timestamp", 
            y=["temperature_c", "current_amps", "air_quality_index"],
            title="Real-Time Sensor Time-Series Metrics"
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No historical logs recorded yet.")

if auto_refresh:
    time.sleep(2)
    st.rerun()
