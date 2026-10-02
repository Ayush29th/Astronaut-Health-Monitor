import streamlit as st
import plotly.graph_objects as go
from modules.database import get_recent_telemetry, get_active_alerts
import pandas as pd
import re

def render_html(html_str):
    """Strips all leading whitespace from every line to prevent Markdown code blocks."""
    cleaned_html = re.sub(r'^[ \t]+', '', html_str, flags=re.MULTILINE)
    st.markdown(cleaned_html, unsafe_allow_html=True)

def render():
    render_html("<div class='mc-row'>")
    
    analysis = st.session_state.latest_analysis
    telemetry = st.session_state.latest_telemetry
    env = st.session_state.latest_env
    active_alerts_df = get_active_alerts()
    num_alerts = len(active_alerts_df)
    
    # ROW 1: MISSION OVERVIEW
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1:
        render_html(f"""
        <div class='mc-panel'>
        <div class='mc-panel-title'>HEALTH SCORE</div>
        <div class='mc-value'>{analysis['health_score']}<span>/100</span></div>
        <div class='mc-status {'nominal' if analysis['risk_level'] == 'LOW' else 'critical'}'>● {'NOMINAL' if analysis['risk_level'] == 'LOW' else analysis['risk_level']}</div>
        </div>
        """)
    with r1c2:
        status_color = 'nominal' if num_alerts == 0 else 'warning'
        status_text = 'ALL CLEAR' if num_alerts == 0 else f'{num_alerts} ACTIVE'
        render_html(f"""
        <div class='mc-panel'>
        <div class='mc-panel-title'>ACTIVE ALERTS</div>
        <div class='mc-value'>{num_alerts:02d}</div>
        <div class='mc-status {status_color}'>● {status_text}</div>
        </div>
        """)
    with r1c3:
        render_html("""
        <div class='mc-panel'>
        <div class='mc-panel-title'>MISSION</div>
        <div class='mc-value'>DAY 242</div>
        <div style='color:var(--text-secondary); font-size:0.75rem; font-family:"JetBrains Mono",monospace;'>Progress: <span style='color:var(--cyan);'>████████░░</span> 67%</div>
        </div>
        """)
    with r1c4:
        render_html("""
        <div class='mc-panel'>
        <div class='mc-panel-title'>TELEMETRY</div>
        <div class='mc-value' style='color:var(--green);'>LIVE</div>
        <div style='color:var(--text-secondary); font-size:0.75rem; font-family:"Inter",sans-serif;'>Last update: <span style='color:var(--text-primary); font-family:"JetBrains Mono",monospace;'>00:01 ago</span></div>
        </div>
        """)
        
    render_html("</div><div class='mc-row'>")

    # ROW 2: LIVE VITALS
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    
    def render_vital(label, value, unit, is_warn, is_crit, baseline_diff):
        status = "NORMAL"
        color_class = "nominal"
        if is_crit:
            status = "CRITICAL"
            color_class = "critical"
        elif is_warn:
            status = "WARNING"
            color_class = "warning"
            
        arrow = "↑" if baseline_diff > 0 else "↓"
        if abs(baseline_diff) < 0.1: arrow = "≈"
        
        return f"""
        <div class='mc-panel'>
        <div class='mc-panel-title'>{label}</div>
        <div class='mc-value-large'>{value:.1f}<span class='mc-unit'>{unit}</span></div>
        <div style='display:flex; justify-content:space-between; align-items:center; margin-top:10px;'>
        <div style='font-size:0.7rem; color:var(--text-secondary); font-family:"JetBrains Mono",monospace;'>{arrow} {abs(baseline_diff):.1f}% from baseline</div>
        <div class='mc-status {color_class}'>● {status}</div>
        </div>
        </div>
        """
        
    with r2c1:
        render_html(render_vital("HEART RATE", telemetry['heart_rate'], "BPM", telemetry['heart_rate']>90, telemetry['heart_rate']>110, (telemetry['heart_rate']-72.0)/72.0*100))
    with r2c2:
        render_html(render_vital("BLOOD OXYGEN", telemetry['spo2'], "%", telemetry['spo2']<95, telemetry['spo2']<92, (telemetry['spo2']-98.5)/98.5*100))
    with r2c3:
        render_html(render_vital("RESPIRATORY RATE", telemetry['respiratory_rate'], "/min", telemetry['respiratory_rate']>20, telemetry['respiratory_rate']>25, (telemetry['respiratory_rate']-14.0)/14.0*100))
    with r2c4:
        render_html(render_vital("BODY TEMPERATURE", telemetry['temperature'], "°C", telemetry['temperature']>37.5, telemetry['temperature']>38.5, (telemetry['temperature']-36.8)/36.8*100))
        
    render_html("</div><div class='mc-row'>")

    # ROW 3: TELEMETRY & AI
    r3c1, r3c2 = st.columns([7, 3])
    
    with r3c1:
        render_html("<div class='mc-panel'>")
        
        tc1, tc2 = st.columns([3, 1])
        with tc1:
            render_html("<div class='mc-panel-title' style='border:none; margin-bottom:0;'>LIVE TELEMETRY</div>")
        with tc2:
            metric_display = st.selectbox("Metric", ["Heart Rate", "SpO2", "Stress"], label_visibility="collapsed", key="telemetry_selector")
            
        metric_col_map = {"Heart Rate": "heart_rate", "SpO2": "spo2", "Stress": "stress"}
        metric_col = metric_col_map[metric_display]
            
        df = get_recent_telemetry(minutes=15)
        if not df.empty:
            fig = go.Figure()
            
            if metric_display == "Heart Rate":
                fig.add_shape(type="rect", x0=df['timestamp'].min(), y0=60, x1=df['timestamp'].max(), y1=100, fillcolor="rgba(16,185,129,0.05)", line=dict(width=0), layer="below")
                fig.add_shape(type="line", x0=df['timestamp'].min(), y0=110, x1=df['timestamp'].max(), y1=110, line=dict(color="rgba(245,158,11,0.5)", width=1, dash="dash"))
                y_range = [40, 150]
            elif metric_display == "SpO2":
                fig.add_shape(type="rect", x0=df['timestamp'].min(), y0=95, x1=df['timestamp'].max(), y1=100, fillcolor="rgba(16,185,129,0.05)", line=dict(width=0), layer="below")
                fig.add_shape(type="line", x0=df['timestamp'].min(), y0=92, x1=df['timestamp'].max(), y1=92, line=dict(color="rgba(239,68,68,0.5)", width=1, dash="dash"))
                y_range = [85, 100]
            else: # Stress
                fig.add_shape(type="rect", x0=df['timestamp'].min(), y0=0, x1=df['timestamp'].max(), y1=40, fillcolor="rgba(16,185,129,0.05)", line=dict(width=0), layer="below")
                fig.add_shape(type="line", x0=df['timestamp'].min(), y0=80, x1=df['timestamp'].max(), y1=80, line=dict(color="rgba(239,68,68,0.5)", width=1, dash="dash"))
                y_range = [0, 100]
            
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df[metric_col],
                mode='lines',
                line=dict(color="#06b6d4", width=2, shape='spline'),
                fill='tozeroy',
                fillcolor='rgba(6, 182, 212, 0.1)'
            ))
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", color="#94a3b8", range=y_range, tickfont=dict(family="JetBrains Mono")),
                height=150
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        render_html("</div>")
        
    with r3c2:
        if num_alerts > 0:
            latest_alert = active_alerts_df.iloc[0]
            rec = latest_alert['recommendation']
        elif analysis['risk_level'] == "LOW":
            rec = "Continue normal mission activity. No intervention required."
        else:
            rec = "Assess physiological parameters and consider workload reduction."

        render_html(f"""
        <div class='mc-panel' style='display:flex; flex-direction:column; justify-content:space-between;'>
        <div>
        <div class='mc-panel-title'>AI HEALTH ANALYSIS <span class='live-indicator' style='float:right;'>● ACTIVE</span></div>
        <div style='display:flex; justify-content:space-between; margin-bottom:12px; margin-top:8px;'>
        <div>
        <div style='font-size:0.7rem; color:var(--text-secondary); margin-bottom:4px;'>HEALTH RISK</div>
        <div style='font-family:"JetBrains Mono",monospace; font-size:1.1rem; font-weight:600; color:{"var(--red)" if analysis['risk_level']=="CRITICAL" else "var(--green)"};'>{analysis['risk_level']}</div>
        </div>
        <div style='text-align:right;'>
        <div style='font-size:0.7rem; color:var(--text-secondary); margin-bottom:4px;'>CONFIDENCE</div>
        <div style='font-family:"JetBrains Mono",monospace; font-size:1.1rem; font-weight:500; color:var(--text-primary);'>94%</div>
        </div>
        </div>
        <div style='display:flex; justify-content:space-between; margin-bottom:12px; padding-bottom:12px; border-bottom:1px solid var(--border);'>
        <div>
        <div style='font-size:0.7rem; color:var(--text-secondary); margin-bottom:4px;'>FATIGUE</div>
        <div style='font-family:"JetBrains Mono",monospace; font-size:1rem; color:var(--text-primary);'>{analysis['fatigue_probability']}%</div>
        </div>
        <div style='text-align:right;'>
        <div style='font-size:0.7rem; color:var(--text-secondary); margin-bottom:4px;'>STRESS</div>
        <div style='font-family:"JetBrains Mono",monospace; font-size:1rem; color:var(--text-primary);'>{analysis['stress_level']}%</div>
        </div>
        </div>
        <div style='font-size:0.7rem; color:var(--text-secondary); margin-bottom:6px; text-transform:uppercase;'>AI INSIGHT</div>
        <div class='mc-insight-text'>{analysis['explanation']}</div>
        </div>
        <div class='mc-insight-recommendation'>
        <strong style='font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; color:var(--cyan);'>RECOMMENDATION</strong><br>
        <div style='margin-top:2px;'>{rec}</div>
        </div>
        </div>
        """)

    render_html("</div>")
    
    # ROW 4: ENVIRONMENT & ALERTS
    render_html(f"""
    <div class='env-strip'>
    <div class='env-item'>
    <div class='env-label'>CABIN PRESSURE</div>
    <div class='env-val'>{env['cabin_pressure']} <span style='font-size:0.75rem;color:var(--text-secondary);'>kPa</span></div>
    <div class='mc-status {'nominal' if 14.2 <= env['cabin_pressure'] <= 14.9 else 'warning'}' style='font-size:0.65rem;margin-top:2px;'>● {'NORMAL' if 14.2 <= env['cabin_pressure'] <= 14.9 else 'WARNING'}</div>
    </div>
    <div class='env-item'>
    <div class='env-label'>CO₂</div>
    <div class='env-val'>{env['co2']} <span style='font-size:0.75rem;color:var(--text-secondary);'>ppm</span></div>
    <div class='mc-status {'nominal' if env['co2'] < 800 else 'warning'}' style='font-size:0.65rem;margin-top:2px;'>● {'NORMAL' if env['co2'] < 800 else 'WARNING'}</div>
    </div>
    <div class='env-item'>
    <div class='env-label'>O₂</div>
    <div class='env-val'>{env['oxygen_level']} <span style='font-size:0.75rem;color:var(--text-secondary);'>%</span></div>
    <div class='mc-status {'nominal' if env['oxygen_level'] > 20 else 'warning'}' style='font-size:0.65rem;margin-top:2px;'>● {'NORMAL' if env['oxygen_level'] > 20 else 'WARNING'}</div>
    </div>
    <div class='env-item'>
    <div class='env-label'>RADIATION</div>
    <div class='env-val'>{env['radiation']} <span style='font-size:0.75rem;color:var(--text-secondary);'>mSv</span></div>
    <div class='mc-status nominal' style='font-size:0.65rem;margin-top:2px;'>● SAFE</div>
    </div>
    <div class='env-item'>
    <div class='env-label'>TEMPERATURE</div>
    <div class='env-val'>{env['temperature']} <span style='font-size:0.75rem;color:var(--text-secondary);'>°C</span></div>
    <div class='mc-status {'nominal' if 19 < env['temperature'] < 25 else 'warning'}' style='font-size:0.65rem;margin-top:2px;'>● {'NORMAL' if 19 < env['temperature'] < 25 else 'WARNING'}</div>
    </div>
    </div>
    """)
