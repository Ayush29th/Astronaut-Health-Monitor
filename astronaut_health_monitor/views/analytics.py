import streamlit as st
import plotly.express as px
from modules.database import get_all_telemetry
import re

def render_html(html_str):
    cleaned_html = re.sub(r'^[ \t]+', '', html_str, flags=re.MULTILINE)
    st.markdown(cleaned_html, unsafe_allow_html=True)

def render():
    render_html("<h2 style='color:var(--text-secondary); font-size:0.85rem; padding-left: 8px;'>// HISTORICAL ANALYTICS</h2>")
    
    df = get_all_telemetry(limit=2000)
    
    if df.empty:
        st.info("No historical data available. Start monitoring to generate data.")
    else:
        render_html("<div class='mc-panel'>")
        c1, c2 = st.columns([1, 4])
        
        with c1:
            metric = st.selectbox("SELECT METRIC", 
                                  ['heart_rate', 'spo2', 'stress', 'fatigue', 'respiratory_rate', 'sleep_score'],
                                  format_func=lambda x: x.replace('_', ' ').upper())
                                  
            time_range = st.selectbox("TIME RANGE", ["Last 1 Hour", "Last 6 Hours", "Last 24 Hours", "All Data"])
            
        with c2:
            fig = px.line(df, x='timestamp', y=metric, 
                          color_discrete_sequence=["#06b6d4"])
            fig.update_layout(
                title=dict(text=f"{metric.replace('_', ' ').upper()} TREND", font=dict(family="Inter", color="#94a3b8", size=10)),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="JetBrains Mono", color="#94a3b8", size=10),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="TIME"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="VALUE"),
                height=300,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            fig.update_traces(fill='tozeroy', fillcolor='rgba(6, 182, 212, 0.1)', line=dict(width=2))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        render_html("</div>")
