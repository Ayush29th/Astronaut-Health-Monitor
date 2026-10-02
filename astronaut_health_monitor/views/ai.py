import streamlit as st
import re

def render_html(html_str):
    cleaned_html = re.sub(r'^[ \t]+', '', html_str, flags=re.MULTILINE)
    st.markdown(cleaned_html, unsafe_allow_html=True)

def render():
    render_html("<h2 style='color:var(--text-secondary); font-size:0.85rem; padding-left: 8px;'>// AI HEALTH ANALYSIS</h2>")
    analysis = st.session_state.latest_analysis
    
    render_html("<div class='mc-row'>")
    c1, c2, c3 = st.columns(3)
    with c1:
        render_html(f"""
        <div class='mc-panel'>
        <div class='mc-panel-title'>OVERALL HEALTH</div>
        <div class='mc-value'>{analysis['health_score']}<span>/100</span></div>
        </div>
        """)
    with c2:
        render_html(f"""
        <div class='mc-panel'>
        <div class='mc-panel-title'>CARDIOVASCULAR RISK</div>
        <div class='mc-value'>{analysis['cardiovascular_risk']}<span>%</span></div>
        </div>
        """)
    with c3:
        render_html(f"""
        <div class='mc-panel'>
        <div class='mc-panel-title'>RESPIRATORY RISK</div>
        <div class='mc-value'>{analysis['respiratory_risk']}<span>%</span></div>
        </div>
        """)
    render_html("</div>")
        
    render_html("<div class='mc-row'>")
    c4, c5, c6 = st.columns(3)
    with c4:
        render_html(f"""
        <div class='mc-panel'>
        <div class='mc-panel-title'>PREDICTED FATIGUE</div>
        <div class='mc-value'>{analysis['fatigue_probability']}<span>%</span></div>
        </div>
        """)
    with c5:
        render_html(f"""
        <div class='mc-panel'>
        <div class='mc-panel-title'>STRESS LEVEL</div>
        <div class='mc-value'>{analysis['stress_level']}<span>/100</span></div>
        </div>
        """)
    with c6:
        render_html(f"""
        <div class='mc-panel'>
        <div class='mc-panel-title'>RECOVERY SCORE</div>
        <div class='mc-value'>{analysis['recovery_score']}<span>/100</span></div>
        </div>
        """)
    render_html("</div>")
        
    render_html(f"""
    <div class='mc-row'>
    <div class='mc-panel' style='border-left: 3px solid var(--cyan);'>
    <div class='mc-panel-title'>SYSTEM DIAGNOSIS</div>
    <div class='mc-insight-text' style='font-size: 0.95rem;'>{analysis['explanation']}</div>
    </div>
    </div>
    """)
    
    factors_html = "<div class='mc-row'><div class='mc-panel'><div class='mc-panel-title'>CONTRIBUTING FACTORS</div>"
    for factor in analysis['contributing_factors']:
        color = "var(--green)" if "nominal" in factor else "var(--amber)"
        factors_html += f"<div style='margin-bottom: 6px; font-size: 0.85rem; color:var(--text-primary);'><span style='color: {color}; margin-right: 8px;'>▶</span> {factor}</div>"
    factors_html += "</div></div>"
    render_html(factors_html)
