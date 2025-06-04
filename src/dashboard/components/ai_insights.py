import streamlit as st
import json
import pandas as pd
import os
 
st.title("🤖 AI Risk Model Insights")
 
risk_file = st.text_input("Enter path to risk scores file", "data/risk_scores.json")
 
if os.path.exists(risk_file):
    with open(risk_file) as f:
        scores = json.load(f)
    df = pd.DataFrame(scores)
    st.metric("Domains Scored", len(df))
    st.dataframe(df)
 
    st.subheader("📊 High Risk Domains")
    st.write(df[df['risk_score'] >= 80])
else:
    st.warning("Risk score file not found")