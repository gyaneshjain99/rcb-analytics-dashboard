import streamlit as st
import os

def add_rcb_theme():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #121212 0%, #1a0505 100%) !important;
        }
        .stApp, .stMetric, .stMarkdown, .stText, p, div, span, table {
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] {
            background-color: #1a1a1a !important;
            border-right: 2px solid #f72c2c !important;
        }
        h1, h2, h3 {
            color: #f72c2c !important;
        }
        .stTable {
            background-color: #262626 !important;
            border: 1px solid #444444 !important;
        }
        .stTable td, .stTable th {
            color: #ffffff !important;
            background-color: #262626 !important;
            border-bottom: 1px solid #444444 !important;
        }
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
            color: #ffffff !important;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def show_banner():
    # Dynamically resolve the assets folder path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    banner_path = os.path.join(base_dir, "assets", "banner.jpg")
    
    if os.path.exists(banner_path):
        st.image(banner_path, use_container_width=True)
    else:
        st.error(f"Please place 'banner.jpg' in the 'assets' folder. Looked in: {banner_path}")