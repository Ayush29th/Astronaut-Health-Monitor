import streamlit as st
import os
import time
from modules.database import save_telemetry, save_environment

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'style.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def render_sidebar():
    load_css()
    
    # Initialize engine state if not present (defensive)
    if 'engine' not in st.session_state:
        from modules.telemetry_engine import TelemetryEngine
        st.session_state.engine = TelemetryEngine()
        
    with st.sidebar:
        st.markdown("<h3 style='color: #00f0ff; font-family: \"Share Tech Mono\", monospace;'>ASTRONAUT N-61</h3>", unsafe_allow_html=True)
        st.markdown("**Name:** Alex Carter")
        st.markdown("**Mission:** Artemis V")
        st.markdown("**MET:** 242:12:04")
        st.progress(0.65)
        
        st.markdown("<br><hr style='border-color: #2a2d34;'><br>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='font-family: \"Share Tech Mono\", monospace;'>DEMO CONTROL</h3>", unsafe_allow_html=True)
        
        if 'scenario' not in st.session_state:
            st.session_state.scenario = "Normal"
            
        scenario = st.selectbox(
            "SIMULATION SCENARIO",
            ["Normal", "High Fatigue", "Cardiac Stress", "Low Oxygen", "Environmental Anomaly"],
            index=["Normal", "High Fatigue", "Cardiac Stress", "Low Oxygen", "Environmental Anomaly"].index(st.session_state.scenario),
            key="scenario_selector"
        )
        
        if scenario != st.session_state.scenario:
            st.session_state.scenario = scenario
            st.rerun()
            
        if 'monitoring_active' not in st.session_state:
            st.session_state.monitoring_active = False
            
        if st.button("TOGGLE MONITORING", use_container_width=True):
            st.session_state.monitoring_active = not st.session_state.monitoring_active
            st.rerun()
            
        if st.session_state.monitoring_active:
            st.markdown("<div style='text-align:center; color:#00d26a; font-weight:bold; margin-top: 10px;'>● LIVE TELEMETRY ACTIVE</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; color:#ff9800; font-weight:bold; margin-top: 10px;'>⏸ SYSTEM PAUSED</div>", unsafe_allow_html=True)
            
        st.markdown("<br><hr style='border-color: #2a2d34;'><br>", unsafe_allow_html=True)
        if st.button("RESET DATABASE", use_container_width=True):
            from modules.database import clear_db
            clear_db()
            st.session_state.engine.reset_baselines()
            st.session_state.scenario = "Normal"
            st.rerun()

def process_tick():
    """Run one tick of the simulation loop if monitoring is active"""
    if st.session_state.get('monitoring_active', False):
        # Generate data
        engine = st.session_state.engine
        detector = st.session_state.detector
        analyzer = st.session_state.analyzer
        alert_manager = st.session_state.alert_manager
        
        telemetry = engine.generate_telemetry(st.session_state.scenario)
        env = engine.generate_environment(st.session_state.scenario)
        
        # Detect anomalies
        detector.add_telemetry(telemetry)
        anomalies = detector.check_anomalies(telemetry)
        
        # Analyze health
        analysis = analyzer.analyze_health(telemetry, anomalies)
        
        # Process alerts
        alert_manager.process_anomalies(anomalies)
        
        # Save to DB
        save_telemetry(telemetry)
        save_environment(env)
        
        # Store latest in session state for fast UI access
        st.session_state.latest_telemetry = telemetry
        st.session_state.latest_env = env
        st.session_state.latest_analysis = analysis
        st.session_state.latest_anomalies = anomalies
        
        # Control refresh rate
        time.sleep(1.0)
        st.rerun()
