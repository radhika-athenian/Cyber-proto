import streamlit as st
import json
import pandas as pd
import os
 
st.title("🕵️ Leak Intelligence")
 
leak_file = st.text_input("Enter path to classified leaks file", "data/classified_leaks.json")
 
if os.path.exists(leak_file):
    with open(leak_file) as f:
        leaks = json.load(f)
    df = pd.DataFrame(leaks)
    st.metric("Total Leaks", len(df))
    st.metric("Sensitive Leaks", df[df['label'] == 'sensitive'].shape[0])
 
    label_filter = st.selectbox("Filter by Label", ["all", "sensitive", "benign"])
    if label_filter != "all":
        df = df[df['label'] == label_filter]
    st.dataframe(df[["source", "label", "text"]])
else:
    st.warning("Leak file not found")