"""
IPL Analytics Pro - Cached Data Loader
Provides cached loading functions for matches and ball-by-ball parquet datasets.
"""

import os
import streamlit as st
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

@st.cache_data(show_spinner="Loading verified IPL match records...")
def load_matches_data():
    """Loads cleaned match-level dataset."""
    path = os.path.join(PROCESSED_DIR, "matches_cleaned.csv")
    if not os.path.exists(path):
        st.error(f"Dataset not found at {path}. Please run scripts/clean_data.py first.")
        st.stop()
    df = pd.read_csv(path)
    return df

@st.cache_data(show_spinner="Loading verified ball-by-ball deliveries...")
def load_deliveries_data():
    """Loads cleaned deliveries dataset from high-performance Parquet format."""
    parquet_path = os.path.join(PROCESSED_DIR, "deliveries_cleaned.parquet")
    csv_path = os.path.join(PROCESSED_DIR, "deliveries_cleaned.csv")
    
    if os.path.exists(parquet_path):
        df = pd.read_parquet(parquet_path)
    elif os.path.exists(csv_path):
        df = pd.read_csv(csv_path, low_memory=False)
    else:
        st.error("Deliveries dataset not found. Please run scripts/clean_data.py first.")
        st.stop()
    return df
