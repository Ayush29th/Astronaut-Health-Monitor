import streamlit as st
import os
import time
import re
from modules.database import init_db, save_telemetry, save_environment
from modules.telemetry_engine import TelemetryEngine
from modules.anomaly_detector import AnomalyDetector
from modules.ai_analyzer import AIAnalyzer
from modules.alert_manager import AlertManager

st.set_page_config(
    page_title="Astronaut Health Monitor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_html(html_str):
    cleaned_html = re.sub(r'^[ \t]+', '', html_str, flags=re.MULTILINE)
    st.markdown(cleaned_html, unsafe_allow_html=True)

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'assets', 'style.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            render_html(f'<style>{f.read()}</style>')

def init_app():
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'data', 'astronaut_health.db')):
        init_db()
    else:
        init_db()

    if 'engine' not in st.session_state: st.session_state.engine = TelemetryEngine()
    if 'detector' not in st.session_state: st.session_state.detector = AnomalyDetector()
    if 'analyzer' not in st.session_state: st.session_state.analyzer = AIAnalyzer()
    if 'alert_manager' not in st.session_state: st.session_state.alert_manager = AlertManager()
        
    if 'current_page' not in st.session_state: st.session_state.current_page = 'Overview'
    if 'monitoring_active' not in st.session_state: st.session_state.monitoring_active = True
    if 'scenario' not in st.session_state: st.session_state.scenario = "Normal"
        
    if 'latest_telemetry' not in st.session_state:
        st.session_state.latest_telemetry = st.session_state.engine.generate_telemetry("Normal")
        st.session_state.latest_env = st.session_state.engine.generate_environment("Normal")
        st.session_state.latest_analysis = st.session_state.analyzer.analyze_health(st.session_state.latest_telemetry, [])
        st.session_state.latest_anomalies = []

def process_tick():
    if st.session_state.get('monitoring_active', False):
        engine = st.session_state.engine
        detector = st.session_state.detector
        analyzer = st.session_state.analyzer
        alert_manager = st.session_state.alert_manager
        
        telemetry = engine.generate_telemetry(st.session_state.scenario)
        env = engine.generate_environment(st.session_state.scenario)
        
        detector.add_telemetry(telemetry)
        anomalies = detector.check_anomalies(telemetry)
        analysis = analyzer.analyze_health(telemetry, anomalies)
        alert_manager.process_anomalies(anomalies)
        
        save_telemetry(telemetry)
        save_environment(env)
        
        st.session_state.latest_telemetry = telemetry
        st.session_state.latest_env = env
        st.session_state.latest_analysis = analysis
        st.session_state.latest_anomalies = anomalies
        
        time.sleep(1.0)
        st.rerun()

def render_sidebar():
    with st.sidebar:
        render_html("""
        <div class='sidebar-header'>
        <div class='sidebar-avatar'>👨‍🚀</div>
        <div style='color:var(--text-secondary); font-size:0.65rem; letter-spacing:1px; margin-bottom:2px;'>ASTRONAUT</div>
        <div style='color:var(--text-primary); font-size:0.9rem; font-weight:600;'>HEALTH MONITOR</div>
        <div style='display:flex; justify-content:space-between; margin-top:10px; font-size:0.75rem; text-align:left;'>
        <div><span style='color:var(--text-secondary);'>Mission:</span><br><span style='color:var(--text-primary); font-family: "JetBrains Mono", monospace;'>N-61</span></div>
        <div style='text-align:right;'><span style='color:var(--text-secondary);'>Astronaut:</span><br><span style='color:var(--text-primary); font-family: "JetBrains Mono", monospace;'>A-01</span></div>
        </div>
        </div>
        """)
        
        pages = {
            "Overview": "▦",
            "Health Monitoring": "♡",
            "AI Analysis": "⌁",
            "Alerts": "⚠",
            "Analytics": "◫",
            "Environment": "◉"
        }
        
        for p, icon in pages.items():
            is_active = st.session_state.current_page == p
            cls = "sidebar-nav-item-active" if is_active else "sidebar-nav-item"
            if st.button(f"{icon} &nbsp;&nbsp; {p}", key=f"nav_{p}"):
                st.session_state.current_page = p
                st.rerun()
        
        render_html("<div style='margin-top:24px; padding: 0 4px;'>")
        render_html("<div style='font-size:0.65rem; color:var(--text-secondary); margin-bottom:4px; text-transform:uppercase;'>Scenario</div>")
        
        scenario = st.selectbox(
            "SCENARIO",
            ["Normal", "High Fatigue", "Cardiac Stress", "Low Oxygen", "Environmental Anomaly"],
            index=["Normal", "High Fatigue", "Cardiac Stress", "Low Oxygen", "Environmental Anomaly"].index(st.session_state.scenario),
            key="scenario_select"
        )
        if scenario != st.session_state.scenario:
            st.session_state.scenario = scenario
            st.rerun()
            
        render_html(f"""
        <div style='margin-top: 12px; font-size:0.65rem; color:var(--text-secondary);'>
        STATUS: <span class='live-indicator'>● {'LIVE' if st.session_state.monitoring_active else 'PAUSED'}</span>
        </div>
        """)
        render_html("</div>")

def main():
    load_css()
    init_app()
    render_sidebar()
    
    render_html("""
    <div class='mc-header'>
    <div class='mc-header-left'>ASTRONAUT HEALTH MONITOR</div>
    <div class='mc-header-center'>
    <div><span class='live-indicator'>●</span> MISSION ACTIVE</div>
    <div>MET: 242:12:04</div>
    </div>
    <div class='mc-header-right'>
    ASTRONAUT A-01 <div class='header-avatar'>👨‍🚀</div>
    </div>
    </div>
    """)

    from views import overview, health, ai, alerts, analytics, environment
    
    if st.session_state.current_page == "Overview":
        overview.render()
    elif st.session_state.current_page == "Health Monitoring":
        health.render()
    elif st.session_state.current_page == "AI Analysis":
        ai.render()
    elif st.session_state.current_page == "Alerts":
        alerts.render()
    elif st.session_state.current_page == "Analytics":
        analytics.render()
    elif st.session_state.current_page == "Environment":
        environment.render()
        
    process_tick()

if __name__ == "__main__":
    main()
