import streamlit as st
import pandas as pd
from modules.database import get_active_alerts, get_all_alerts, resolve_alert
import re

def render_html(html_str):
    cleaned_html = re.sub(r'^[ \t]+', '', html_str, flags=re.MULTILINE)
    st.markdown(cleaned_html, unsafe_allow_html=True)

def render():
    render_html("<h2 style='color:var(--text-secondary); font-size:0.85rem; padding-left: 8px;'>// SYSTEM ALERTS</h2>")
    
    active_alerts = get_active_alerts()
    all_alerts = get_all_alerts(limit=50)
    
    if not active_alerts.empty:
        render_html(f"<div style='color:var(--red); font-size:0.85rem; padding-left:8px; margin-bottom:12px;'>⚠️ {len(active_alerts)} ACTIVE ALERTS</div>")
        for _, alert in active_alerts.iterrows():
            render_html(f"""
            <div class='mc-panel' style='border-left:3px solid var(--red); margin-bottom:8px;'>
            <div style='display:flex; justify-content:space-between;'>
            <div class='mc-panel-title' style='color:var(--red);'>🚨 CRITICAL ALERT - {alert['metric'].upper()}</div>
            <div style='font-family:"JetBrains Mono"; font-size:0.75rem; color:var(--text-secondary);'>{alert['timestamp']}</div>
            </div>
            <div style='font-size:0.85rem; margin-top:4px;'>{alert['message']}</div>
            <div class='mc-insight-recommendation'>{alert['recommendation']}</div>
            </div>
            """)
            if st.button(f"ACKNOWLEDGE ALERT #{alert['id']}", key=f"ack_{alert['id']}"):
                resolve_alert(alert['id'])
                st.rerun()
    else:
        render_html("<div class='mc-panel'><div style='color:var(--green); font-size:0.85rem;'>✅ NO ACTIVE ALERTS</div></div>")
        
    render_html("<h2 style='color:var(--text-secondary); font-size:0.85rem; padding-left: 8px; margin-top:24px;'>// ALERT HISTORY</h2>")
    
    if not all_alerts.empty:
        history_df = all_alerts[['timestamp', 'metric', 'severity', 'message', 'status']]
        st.dataframe(history_df, use_container_width=True, hide_index=True)
    else:
        st.info("No alert history.")
