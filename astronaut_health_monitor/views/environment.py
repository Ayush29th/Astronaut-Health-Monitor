import streamlit as st
import plotly.express as px
from modules.database import get_recent_environment
import re

def render_html(html_str):
    cleaned_html = re.sub(r'^[ \t]+', '', html_str, flags=re.MULTILINE)
    st.markdown(cleaned_html, unsafe_allow_html=True)

def render():
    render_html("<h2 style='color:var(--text-secondary); font-size:0.85rem; padding-left: 8px;'>// CABIN ENVIRONMENT</h2>")
    
    df = get_recent_environment(minutes=60)
    
    if df.empty:
        st.info("No environment data available.")
        return
        
    latest = df.iloc[-1]
    
    render_html("<div class='mc-row'>")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_html(f"""
        <div class='mc-panel'>
        <div class='mc-panel-title'>OXYGEN LEVEL</div>
        <div class='mc-value-large'>{latest['oxygen_level']:.1f}<span class='mc-unit'>%</span></div>
        <div class='mc-status {'nominal' if latest['oxygen_level'] > 20 else 'warning'}'>● {'NOMINAL' if latest['oxygen_level'] > 20 else 'WARNING'}</div>
        </div>
        """)
    with c2:
        render_html(f"""
        <div class='mc-panel'>
        <div class='mc-panel-title'>CO2 LEVEL</div>
        <div class='mc-value-large'>{latest['co2']:.0f}<span class='mc-unit'>ppm</span></div>
        <div class='mc-status {'nominal' if latest['co2'] < 800 else 'warning'}'>● {'NOMINAL' if latest['co2'] < 800 else 'WARNING'}</div>
        </div>
        """)
    with c3:
        render_html(f"""
        <div class='mc-panel'>
        <div class='mc-panel-title'>CABIN PRESSURE</div>
        <div class='mc-value-large'>{latest['cabin_pressure']:.1f}<span class='mc-unit'>kPa</span></div>
        <div class='mc-status {'nominal' if 14.2 <= latest['cabin_pressure'] <= 14.9 else 'warning'}'>● {'NOMINAL' if 14.2 <= latest['cabin_pressure'] <= 14.9 else 'WARNING'}</div>
        </div>
        """)
    with c4:
        render_html(f"""
        <div class='mc-panel'>
        <div class='mc-panel-title'>TEMPERATURE</div>
        <div class='mc-value-large'>{latest['temperature']:.1f}<span class='mc-unit'>°C</span></div>
        <div class='mc-status {'nominal' if 19 < latest['temperature'] < 25 else 'warning'}'>● {'NOMINAL' if 19 < latest['temperature'] < 25 else 'WARNING'}</div>
        </div>
        """)
    render_html("</div>")
    
    render_html("<div class='mc-panel' style='margin: 8px;'>")
    metric = st.selectbox("SELECT METRIC", 
                          ['oxygen_level', 'co2', 'cabin_pressure', 'temperature', 'humidity', 'radiation'],
                          format_func=lambda x: x.replace('_', ' ').upper())
    
    fig = px.line(df, x='timestamp', y=metric, color_discrete_sequence=["#10b981"])
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
    fig.update_traces(fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.1)', line=dict(width=2))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    render_html("</div>")
