"""
IPL Analytics Pro - About Page
Architecture, engineering philosophy, technology stack, and GitHub repository guidance.
"""

import os
import streamlit as st

st.set_page_config(page_title="About | IPL Analytics Pro", page_icon="ℹ️", layout="wide")

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

from auth.authentication import require_auth
from components.sidebar import render_sidebar

require_auth()
render_sidebar()

st.markdown("""
<div class="main-header">
    <div>
        <h1>About IPL Analytics Pro</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            Architecture, engineering methodology, technology stack, and reproducibility
        </div>
    </div>
    <div>
        <span class="badge">PROJECT ARCHITECTURE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Overview Card
st.markdown("""
<div class="content-box">
    <div class="section-title">📌 Project Mission & Engineering Principles</div>
    <div style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.7;">
        <b>IPL Analytics Pro</b> is an enterprise-grade cricket analytics and intelligence dashboard engineered to deliver rigorous, audit-compliant historical insights from the Indian Premier League spanning <b>2008 through 2026</b>.
        <br><br>
        Built on genuine match records obtained from <b>Cricsheet</b>, the system strictly forbids fabricated data, enforces ICC cricket scoring laws (such as proper extra attribution under Law 21), isolates non-regulation play (Super Overs), and employs production-ready authentication and modular analytical engines.
    </div>
</div>
""", unsafe_allow_html=True)

col_tech, col_arch = st.columns(2)

with col_tech:
    st.markdown("""
    <div class="content-box">
        <div class="section-title">🛠️ Technology Stack</div>
        <div style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.7;">
            <ul>
                <li><b>Framework:</b> Streamlit 1.63+ (Multi-page App Architecture)</li>
                <li><b>Visualizations:</b> Plotly Express & Plotly Graph Objects (Interactive GPU-accelerated charts)</li>
                <li><b>Data Processing:</b> Pandas 3.0+ & NumPy 2.5+</li>
                <li><b>Storage:</b> Apache Parquet (Fast ball-by-ball queries) & CSV</li>
                <li><b>Authentication:</b> SQLite 3 with <code>bcrypt</code> salt hashing (Rounds: 12)</li>
                <li><b>Testing & QA:</b> Pytest test suites covering data cleaning, analytics, and auth</li>
                <li><b>Design System:</b> Vanilla CSS with custom glassmorphism and IPL color palette</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_arch:
    st.markdown("""
    <div class="content-box">
        <div class="section-title">📁 Project Structure</div>
        <div style="color: #cbd5e1; font-size: 0.85rem; line-height: 1.6; font-family: monospace;">
            ipl-analytics-pro/<br>
            ├── app.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Portal & Overview Dashboard<br>
            ├── pages/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Multi-page analytics views<br>
            ├── analytics/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Reusable statistical engines<br>
            ├── auth/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# SQLite & bcrypt authentication<br>
            ├── components/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# UI cards, filters, and Plotly charts<br>
            ├── data/raw/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Immutable raw Cricsheet data<br>
            ├── data/processed/ &nbsp;&nbsp;&nbsp;&nbsp;# Cleaned matches & parquet deliveries<br>
            ├── scripts/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Automated download, clean, validate pipelines<br>
            ├── reports/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Data quality, acquisition & EDA reports<br>
            ├── tests/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Pytest test suites<br>
            └── assets/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Design system stylesheet & figures
        </div>
    </div>
    """, unsafe_allow_html=True)

# Future Roadmap & Known Limitations
st.markdown("""
<div class="content-box">
    <div class="section-title">🔮 Limitations & Future Roadmap</div>
    <div style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6;">
        <b>Current Scope:</b>
        <ul>
            <li>Excludes unofficial warm-up fixtures or post-match super-over runs from regular career batting averages.</li>
            <li>Rain-shortened matches (19 matches under DLS) utilize actual runs scored; projected runs are not substituted for real data.</li>
        </ul>
        <b>Planned Roadmap:</b>
        <ul>
            <li>Live ball-by-ball streaming via Cricsheet Webhook API integrations.</li>
            <li>Machine Learning Win-Probability Predictor (WPA) real-time model integration.</li>
            <li>Fantasy Cricket Points calculator and team builder optimizer.</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)
