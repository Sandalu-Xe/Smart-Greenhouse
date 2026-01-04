
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
    /* Global Settings */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol" !important;
        background-color: #F5F5F7 !important;
        color: #1D1D1F;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1D1D1F;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    h1 { font-size: 48px !important; margin-bottom: 0.5rem; }
    h2 { font-size: 32px !important; margin-top: 1.5rem; }
    h3 { font-size: 24px !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E5E5;
    }
    
    /* Force all text in sidebar to be dark (fixes white-on-white issue) */
    [data-testid="stSidebar"] div, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span {
        color: #1D1D1F !important;
    }
    
    /* Headers in Sidebar */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #1D1D1F !important;
    }
    
    /* Fix Button Text Color in Sidebar (Keep it White) */
    [data-testid="stSidebar"] button div {
        color: white !important;
    }
    
    /* Buttons (Apple Blue) */
    .stButton > button {
        background-color: #0071E3 !important;
        color: white !important;
        border: none !important;
        border-radius: 980px !important; /* Pill shape */
        padding: 0.6rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 16px !important;
        transition: all 0.2s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background-color: #0077ED !important;
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Metric Cards / Dataframes */
    [data-testid="stTable"] {
        background: white;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    /* General Cards for Layout using st.container mimics (approx) */
    .css-1r6slb0, .css-12oz5g7 { 
        background-color: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }

    /* Remove Streamlit branding slightly */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("# Smart Greenhouse")
st.markdown("<h3 style='font-weight: 400; color: #86868b; margin-top: -15px;'>Fuzzy Logic Control System • Mamdani vs Sugeno</h3>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar Controls
st.sidebar.markdown("## Control Center")
st.sidebar.markdown("Configure your simulation parameters below.")
num_tests = st.sidebar.slider("Number of Random Tests", min_value=1, max_value=50, value=20)
steps_per_test = st.sidebar.slider("Steps per Test", min_value=10, max_value=100, value=50)

st.sidebar.markdown("---")
st.sidebar.info("Click **Run Simulation** to execute the Python simulation engine.")

if st.sidebar.button("Run Simulation", use_container_width=True):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner("Initializing Controllers..."):
        status_text.text("Booting fuzzy logic kernels...")
        mamdani = MamdaniController()
        sugeno = SugenoController()
        sim = GreenhouseSimulation(mamdani, sugeno)
        progress_bar.progress(30)
    
    with st.spinner(f"Running {num_tests} Tests..."):
        status_text.text(f"Executing {num_tests} stochastic simulation cycles...")
        metrics = sim.run_random_tests(num_tests=num_tests, steps_per_test=steps_per_test)
        progress_bar.progress(100)
        time.sleep(0.5)
        status_text.empty()
        progress_bar.empty()
        
    st.success("Simulation Complete")
    
    # 1. Comparison Table
    st.markdown("## Performance Analysis")
    
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
    
    # Custom styling for dataframe
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 2. Visualization
    st.markdown("## Visual Insight")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div style='background: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;'>", unsafe_allow_html=True)
        st.markdown("#### Avg Error")
        st.caption("Lower is better")
        st.bar_chart(df.set_index("Metric").loc["Average Error"], color="#FF3B30") # Apple Red
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
         st.markdown("<div style='background: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;'>", unsafe_allow_html=True)
         st.markdown("#### Energy Usage")
         st.caption("Lower is better")
         st.bar_chart(df.set_index("Metric").loc["Energy Usage"], color="#34C759") # Apple Green
         st.markdown("</div>", unsafe_allow_html=True)

    with col3:
         st.markdown("<div style='background: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;'>", unsafe_allow_html=True)
         st.markdown("#### Response Time")
         st.caption("Lower is better")
         st.bar_chart(df.set_index("Metric").loc["Average Response Time (ms)"], color="#0071E3") # Apple Blue
         st.markdown("</div>", unsafe_allow_html=True)
    
else:
    st.markdown("""
    <div style='background: white; padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-top: 50px;'>
        <h2 style='color: #1D1D1F; margin-top: 0;'>Ready to Simulate</h2>
        <p style='color: #86868b; font-size: 18px;'>Configure your parameters in the sidebar and press "Run Simulation" to begin the fuzzy logic comparison.</p>
    </div>
    """, unsafe_allow_html=True)

# 3. Report
st.markdown("## Competency Report")
st.markdown("<div style='background: white; padding: 40px; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)

try:
    with open("/Users/sandaluthushan/.gemini/antigravity/brain/7ea606e8-b02b-481f-be3d-825c1d167647/report.md", "r") as f:
        report_content = f.read()
    st.markdown(report_content)
except FileNotFoundError:
    st.warning("Report file not found.")

st.markdown("</div>", unsafe_allow_html=True)
