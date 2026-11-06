"""
RR TalentIQ - Machine Learning Intelligence & Archetype Discovery
Unsupervised K-Means clustering, PCA latent space projections,
silhouette validation, and z-score feature attribution for domestic talents.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ML Intelligence | RR TalentIQ", page_icon="🤖", layout="wide")

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

from auth.authentication import require_auth
from components.sidebar import render_sidebar
from components.scouting_components import style_scouting_fig, plot_pca_cluster_landscape
from analytics.domestic_data_loader import DomesticDataLoader
from scouting.player_ranker import PlayerRanker
from ml.clustering import PlayerClusteringEngine
from ml.player_model import PlayerPCAModel
from ml.explainability import MLExplainabilityEngine

require_auth()
render_sidebar()

# Load Data & Rank
loader = DomesticDataLoader()
raw_df = loader.load_unified_scouting_data(include_synthetic=False)
ranker = PlayerRanker()
scored_df = ranker.rank_players(raw_df)

# Run ML Pipelines
cluster_engine = PlayerClusteringEngine(n_clusters=4, random_state=42)
clustered_df, cluster_meta = cluster_engine.fit_predict_archetypes(scored_df)

pca_engine = PlayerPCAModel(n_components=2)
projected_df, pca_meta = pca_engine.fit_transform_projection(clustered_df)

# Header
st.markdown("""
<div class="main-header">
    <div>
        <h1>Machine Learning Intelligence & Archetypes</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            Unsupervised K-Means clustering, PCA dimensionality reduction, and z-score feature explainability
        </div>
    </div>
    <div>
        <span class="rr-badge">SCIKIT-LEARN ML ENGINE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Top ML Quality Metrics Bar
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Discovered Archetypes</div>
        <div class="kpi-value" style="color: #ffffff;">{cluster_meta['n_clusters']}</div>
        <div class="kpi-sub">K-Means Clusters</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Silhouette Separation</div>
        <div class="kpi-value" style="color: #2ecc71;">{cluster_meta['silhouette_score']:.3f}</div>
        <div class="kpi-sub">Cluster Quality Score</div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">PCA Retained Variance</div>
        <div class="kpi-value" style="color: #48cae4;">{pca_meta['cumulative_variance_pct']:.1f}%</div>
        <div class="kpi-sub">2D Latent Representation</div>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Information Loss</div>
        <div class="kpi-value" style="color: #ffb703;">{pca_meta['information_loss_pct']:.1f}%</div>
        <div class="kpi-sub">Residual Unmapped Variance</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Main View: PCA Latent Space & Archetype Explanations
col_pca, col_loadings = st.columns([1.2, 0.8])

with col_pca:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🗺️ Latent Player Landscape (PCA Projection)</div>', unsafe_allow_html=True)
    fig_pca = plot_pca_cluster_landscape(projected_df)
    st.plotly_chart(fig_pca, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_loadings:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📐 Principal Component Axes</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.6; margin-bottom: 0.8rem;">
        <b>PC1 ({pca_meta['explained_variance_pct'][0]:.1f}% Variance):</b> Captures aggressive boundary striking vs baseline volume.
        <br><b>PC2 ({pca_meta['explained_variance_pct'][1]:.1f}% Variance):</b> Captures bowling containment vs economy leakage.
    </div>
    """, unsafe_allow_html=True)
    
    # Loadings Table
    pc1_top = list(pca_meta["component_loadings"]["PC1"].items())[:4]
    pc2_top = list(pca_meta["component_loadings"]["PC2"].items())[:4]
    
    st.markdown("<b style='color: #ff2a85; font-size: 0.85rem;'>PC1 Primary Feature Weights:</b>", unsafe_allow_html=True)
    for feat, weight in pc1_top:
        st.markdown(f"<div style='font-size: 0.8rem; color: #94a3b8;'>&bull; {feat}: <b style='color: #ffffff;'>{weight:+.3f}</b></div>", unsafe_allow_html=True)
        
    st.markdown("<b style='color: #00b4d8; font-size: 0.85rem; margin-top: 0.5rem; display: block;'>PC2 Primary Feature Weights:</b>", unsafe_allow_html=True)
    for feat, weight in pc2_top:
        st.markdown(f"<div style='font-size: 0.8rem; color: #94a3b8;'>&bull; {feat}: <b style='color: #ffffff;'>{weight:+.3f}</b></div>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# Individual Player Feature Explainability Deep Dive
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔍 Individual Player Explainability & Z-Score Attribution</div>', unsafe_allow_html=True)

p_select = st.selectbox(
    "Select Player to Inspect Attribution Drivers:",
    options=projected_df["player_name"].tolist(),
    index=0
)

explanation = MLExplainabilityEngine.explain_player_features(p_select, projected_df)

c_exp1, c_exp2 = st.columns(2)
with c_exp1:
    st.markdown(f"**Discovered Archetype:** <span class='priority-tag'>{explanation['cluster_archetype']}</span>", unsafe_allow_html=True)
    st.markdown(f"**Data Completeness:** `{explanation['data_coverage_pct']}%` verified", unsafe_allow_html=True)
    
    st.markdown("<b style='color: #2ecc71; margin-top: 0.5rem; display: block;'>Positive Cohort Deviations (&ge; +0.75&sigma;):</b>", unsafe_allow_html=True)
    for pos in explanation["positive_drivers"]:
        st.markdown(f"<div style='font-size: 0.83rem; color: #cbd5e1; margin-bottom: 0.2rem;'>✔️ {pos}</div>", unsafe_allow_html=True)

with c_exp2:
    st.markdown("<b style='color: #e74c3c; display: block;'>Negative / Vulnerability Deviations (&le; -0.75&sigma;):</b>", unsafe_allow_html=True)
    for neg in explanation["negative_drivers"]:
        st.markdown(f"<div style='font-size: 0.83rem; color: #cbd5e1; margin-bottom: 0.2rem;'>⚠️ {neg}</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

