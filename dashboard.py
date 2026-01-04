
import streamlit as st
import pandas as pd
import numpy as np
import time

# Import our system modules
# We need to ensure the path is correct or just import as is if in the same dir
from controllers.mamdani import MamdaniController
from controllers.sugeno import SugenoController
from simulation import GreenhouseSimulation
from model.plants import ALL_PLANTS

st.set_page_config(page_title="Smart Greenhouse", layout="wide", initial_sidebar_state="expanded")

# --- APPLE-STYLE CSS INJECTION ---
st.markdown("""
<style>
    /* 1. Global Typography & Reset */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        background-color: #F5F5F7 !important; /* Apple Light Gray Background */
        color: #1D1D1F;
        scroll-behavior: smooth;
    }

    /* 2. Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Apply animation to main containers with staggered delays */
    .block-container > div {
        animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }
    
    /* 3. Headers */
    h1, h2, h3 {
        color: #1D1D1F;
        font-weight: 600;
        letter-spacing: -0.025em; /* Tight Apple tracking */
    }
    
    h1 { font-size: 44px !important; margin-bottom: 0.5rem; }
    h2 { font-size: 28px !important; margin-top: 2rem; font-weight: 600; }
    h3 { font-size: 20px !important; font-weight: 500; opacity: 0.8; }
    
    /* 4. Sidebar Styles */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(20px); /* Frosted Glass */
        border-right: 1px solid rgba(0,0,0,0.05);
    }
    
    /* Sidebar Text Visibility Fix */
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #1D1D1F !important; 
    }
    
    /* 5. Apple-style Buttons */
    .stButton > button {
        background: #0071E3 !important; /* System Blue */
        color: white !important;
        border: none !important;
        border-radius: 980px !important;
        padding: 0.6rem 1.8rem !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 6px rgba(0, 113, 227, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.03);
        box-shadow: 0 6px 12px rgba(0, 113, 227, 0.3);
    }
    
    .stButton > button:active {
        transform: scale(0.97);
    }
    
    /* Fix Button Text in Sidebar */
    [data-testid="stSidebar"] button div { color: white !important; }

    /* 6. Card Containers */
    /* We use a custom class 'apple-card' injected via markdown for specific sections */
    .apple-card {
        background: white;
        border-radius: 24px;
        padding: 30px;
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
        animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }
    
    .apple-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 50px -10px rgba(0,0,0,0.1);
    }
    
    /* Metric styling override */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 600;
    }

    /* Remove Streamlit Clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# Header Section with Animation Wrapper
st.markdown("""
<div style='text-align: center; padding: 40px 0; animation: fadeInUp 1s ease;'>
    <h1 style='margin-bottom: 10px;'>Smart Greenhouse</h1>
    <h3 style='opacity: 0.6;'>Advanced Fuzzy Logic Control System</h3>
</div>
""", unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.markdown("## Control Center")
st.sidebar.markdown("Configure your simulation parameters.")
num_tests = st.sidebar.slider("Number of Random Tests", min_value=1, max_value=50, value=20)
steps_per_test = st.sidebar.slider("Steps per Test", min_value=10, max_value=100, value=50)

st.sidebar.markdown("---")

if st.sidebar.button("Run Simulation", use_container_width=True):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner("Processing Logic..."):
        mamdani = MamdaniController()
        sugeno = SugenoController()
        sim = GreenhouseSimulation(mamdani, sugeno)
        progress_bar.progress(30)
        time.sleep(0.3)
    
    with st.spinner("Running stochastic cycles..."):
        metrics = sim.run_random_tests(num_tests=num_tests, steps_per_test=steps_per_test)
        progress_bar.progress(100)
        time.sleep(0.5)
        status_text.empty()
        progress_bar.empty()
        
    st.markdown("<div style='text-align: center; color: #34C759; font-weight: 600; margin-bottom: 20px;'>Simulation Successfully Completed</div>", unsafe_allow_html=True)
    
    # 1. Comparison Table
    st.markdown("## Performance Metrics")
    
    data = {
        "Metric": ["Average Response Time (ms)", "Average Error", "Energy Usage", "Smoothness Score"],
        "Mamdani": [
            metrics['Mamdani']['avg_response'] * 1000,
            metrics['Mamdani']['avg_error'],
            metrics['Mamdani']['avg_energy'],
            metrics['Mamdani']['avg_smoothness']
        ],
        "Sugeno": [
            metrics['Sugeno']['avg_response'] * 1000,
            metrics['Sugeno']['avg_error'],
            metrics['Sugeno']['avg_energy'],
            metrics['Sugeno']['avg_smoothness']
        ]
    }
    df = pd.DataFrame(data)
    
    # Render Table in Card
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. Visualization
    st.markdown("## Visual Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        st.markdown("**Avg Error**")
        st.caption("Lower is better")
        st.bar_chart(df.set_index("Metric").loc["Average Error"], color="#FF3B30") # Apple Red
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
         st.markdown('<div class="apple-card">', unsafe_allow_html=True)
         st.markdown("**Energy Usage**")
         st.caption("Lower is better")
         st.bar_chart(df.set_index("Metric").loc["Energy Usage"], color="#34C759") # Apple Green
         st.markdown('</div>', unsafe_allow_html=True)

    with col3:
         st.markdown('<div class="apple-card">', unsafe_allow_html=True)
         st.markdown("**Response Time**")
         st.caption("Lower is better")
         st.bar_chart(df.set_index("Metric").loc["Average Response Time (ms)"], color="#0071E3") # Apple Blue
         st.markdown('</div>', unsafe_allow_html=True)
    
else:
    # Empty State with Animation
    st.markdown("""
    <div class="apple-card" style='text-align: center; padding: 60px 20px;'>
        <h2 style='margin-top: 0;'>Ready to Start</h2>
        <p style='color: #86868b; font-size: 18px; margin-bottom: 30px;'>Initiate the control system simulation to analyze performance.</p>
        <div style='font-size: 40px;'>🚀</div>
    </div>
    """, unsafe_allow_html=True)

# 3. Report
st.markdown("## Analysis Report")
st.markdown('<div class="apple-card">', unsafe_allow_html=True)

try:
    with open("/Users/sandaluthushan/.gemini/antigravity/brain/7ea606e8-b02b-481f-be3d-825c1d167647/report.md", "r") as f:
        report_content = f.read()
    st.markdown(report_content)
except FileNotFoundError:
    st.warning("Report file not found.")

st.markdown("</div>", unsafe_allow_html=True)
