import streamlit as st
import os
import json
 
st.title("⚙ Configuration & Logs")
 
log_file = st.text_input("Path to log file (optional)", "ssl_check.log")
if os.path.exists(log_file):
    with open(log_file) as f:
        logs = f.read()
    st.text_area("Log Output", logs, height=300)
else:
    st.info("Log file not found or not yet generated.")
 
st.subheader("Upload Custom JSON File")
uploaded_file = st.file_uploader("Upload a JSON config or result file", type="json")
if uploaded_file:
    st.success("File uploaded. Contents previewed below:")
    st.json(json.load(uploaded_file))