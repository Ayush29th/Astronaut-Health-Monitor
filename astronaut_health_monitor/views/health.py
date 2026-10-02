import streamlit as st
import plotly.graph_objects as go
from modules.database import get_recent_telemetry
import re

def render_html(html_str):
    cleaned_html = re.sub(r'^[ \t]+', '', html_str, flags=re.MULTILINE)
    st.markdown(cleaned_html, unsafe_allow_html=True)

def render():
    render_html("<h2 style='color:var(--text-secondary); font-size:0.85rem; padding-left: 8px;'>// HEALTH MONITORING</h2>")
    
    df = get_recent_telemetry(minutes=15)
    
    if df.empty:
        st.info("No telemetry data available yet.")
        return
    
    def create_chart(df, y_col, title, y_min=None, y_max=None, color="#00f0ff"):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df[y_col],
            mode='lines',
            line=dict(color=color, width=2, shape='spline'),
            fill='tozeroy',
            fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15)'
        ))
        
        if y_min is None: y_min = df[y_col].min() * 0.95
        if y_max is None: y_max = df[y_col].max() * 1.05
        
        fig.update_layout(
            title=dict(text=title, font=dict(family="Inter", size=10, color="#94a3b8")),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#94a3b8", range=[y_min, y_max], tickfont=dict(family="JetBrains Mono", size=10)),
            height=200
        )
        return fig
    
    c1, c2 = st.columns(2)
    with c1:
        render_html("<div class='mc-panel'>")
        st.plotly_chart(create_chart(df, 'heart_rate', 'HEART RATE (BPM)', 40, 140, "#ef4444"), use_container_width=True, config={'displayModeBar': False})
        render_html("</div><div class='mc-panel'>")
        st.plotly_chart(create_chart(df, 'stress', 'PHYSIOLOGICAL STRESS (/100)', 0, 100, "#f59e0b"), use_container_width=True, config={'displayModeBar': False})
        render_html("</div>")
    
    with c2:
        render_html("<div class='mc-panel'>")
        st.plotly_chart(create_chart(df, 'spo2', 'BLOOD OXYGEN SpO2 (%)', 85, 100, "#06b6d4"), use_container_width=True, config={'displayModeBar': False})
        render_html("</div><div class='mc-panel'>")
        st.plotly_chart(create_chart(df, 'respiratory_rate', 'RESPIRATORY RATE (BPM)', 5, 35, "#10b981"), use_container_width=True, config={'displayModeBar': False})
        render_html("</div>")
