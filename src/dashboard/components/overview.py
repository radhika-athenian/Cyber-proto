import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

DATA_DIR = "data"

# ---------- Load Risk Data ---------- #
def load_risk_scores():
    path = os.path.join(DATA_DIR, "risk_scores.json")
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []

# ---------- Render Overview Tab ---------- #
def render_overview():
    st.title("🔐 Security Risk Overview")

    risk_data = load_risk_scores()

    if not risk_data:
        st.warning("No risk score data found in /data/risk_scores.json")
        return

    df = pd.DataFrame(risk_data)
    df['risk_score'] = df['risk_score'].astype(int)

    # ----------- Metrics ----------- #
    high_risk_count = (df['risk_score'] >= 80).sum()
    med_risk_count = ((df['risk_score'] >= 50) & (df['risk_score'] < 80)).sum()
    low_risk_count = (df['risk_score'] < 50).sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("🚨 High Risk", high_risk_count)
    col2.metric("⚠️ Medium Risk", med_risk_count)
    col3.metric("✅ Low Risk", low_risk_count)

    # ----------- Risk Score Bar Chart ----------- #
    st.subheader("📊 Risk Score by Subdomain")
    fig = px.bar(df.sort_values(by="risk_score", ascending=False),
                 x="subdomain", y="risk_score",
                 color="risk_score",
                 color_continuous_scale="reds",
                 title="Risk Scores per Subdomain")
    st.plotly_chart(fig, use_container_width=True)

    # ----------- Detailed Table ----------- #
    st.subheader("📋 Risk Details Table")
    st.dataframe(df)


if __name__ == "__main__":
    render_overview()
