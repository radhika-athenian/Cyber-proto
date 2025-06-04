import streamlit as st
 
# Import tabs
from src.dashboard.components import overview, scanners, leaks, ai_insights, config_logs
 
st.set_page_config(
    page_title="Cybersecurity Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
st.sidebar.title("🔐 Navigation")
tab = st.sidebar.radio("Go to", [
    "📊 Overview",
    "🔍 Asset Scanners",
    "🕵️ Leaks",
    "🤖 AI Insights",
    "⚙ Config & Logs"
])
 
if tab == "📊 Overview":
    overview.render_overview()
elif tab == "🔍 Asset Scanners":
    scanners.scanner_tab()
elif tab == "🕵️ Leaks":
    leaks
elif tab == "🤖 AI Insights":
    ai_insights
elif tab == "⚙ Config & Logs":
    config_logs