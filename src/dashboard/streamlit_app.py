"""Streamlit dashboard for running scanners and visualizing risk scores."""

import json
import os

import pandas as pd
import plotly.express as px
import streamlit as st

from src.Scanners.subdomain_scanner import run_sublist3r, resolve_subdomains
from src.Scanners.port_scanner import scan_ports
from src.Scanners.ssl_checker import scan_subdomains as scan_ssl
from src.Scanners.tech_scanner import detect_technologies

DATA_DIR = "data"


def load_risk_scores(file_obj=None):
    """Load risk scores from an uploaded file or the default path."""
    if file_obj is not None:
        return json.load(file_obj)

    path = os.path.join(DATA_DIR, "risk_scores.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []


def render_overview():
    """Display risk score metrics and charts."""
    st.title("🔐 Security Risk Overview")

    uploaded = st.file_uploader("Upload risk_scores.json", type="json")
    risk_data = load_risk_scores(uploaded)

    if not risk_data:
        st.warning(
            "No risk score data available. Upload a JSON file or place one in /data/risk_scores.json"
        )
        return

    df = pd.DataFrame(risk_data)
    df["risk_score"] = df["risk_score"].astype(int)

    high_risk_count = (df["risk_score"] >= 80).sum()
    med_risk_count = ((df["risk_score"] >= 50) & (df["risk_score"] < 80)).sum()
    low_risk_count = (df["risk_score"] < 50).sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("🚨 High Risk", high_risk_count)
    col2.metric("⚠️ Medium Risk", med_risk_count)
    col3.metric("✅ Low Risk", low_risk_count)

    st.subheader("📊 Risk Score by Subdomain")
    fig = px.bar(
        df.sort_values(by="risk_score", ascending=False),
        x="subdomain",
        y="risk_score",
        color="risk_score",
        color_continuous_scale="reds",
        title="Risk Scores per Subdomain",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Risk Details Table")
    st.dataframe(df)


def render_scanners():
    """UI to run all scanning modules."""
    st.title("🔍 Asset Scanners")

    with st.form("scanner_form"):
        domain = st.text_input("Enter domain to scan (e.g., example.com):")
        submit = st.form_submit_button("Run Scanners")

    if submit:
        if not domain:
            st.error("Please enter a valid domain.")
            return

        st.info("Running Subdomain Scanner...")
        subdomains = run_sublist3r(domain)
        resolved_subdomains = resolve_subdomains(subdomains)
        st.success(f"Found {len(resolved_subdomains)} resolved subdomains")
        st.json(resolved_subdomains)

        st.info("Running Port Scanner...")
        ports = scan_ports(resolved_subdomains)
        st.success("Port scanning complete")
        st.json(ports)

        st.info("Running SSL Checker...")
        ssl_results = scan_ssl(resolved_subdomains)
        st.success("SSL scan complete")
        st.json(ssl_results)

        st.info("Detecting Technologies...")
        tech_stack = detect_technologies(
            [item["subdomain"] for item in resolved_subdomains]
        )
        st.success("Technology fingerprinting complete")
        st.json(tech_stack)

        if st.checkbox("💾 Save all results to /data"):
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs(DATA_DIR, exist_ok=True)

            with open(f"{DATA_DIR}/{domain}_assets_{timestamp}.json", "w") as f:
                json.dump(resolved_subdomains, f, indent=2)
            with open(f"{DATA_DIR}/{domain}_ports_{timestamp}.json", "w") as f:
                json.dump(ports, f, indent=2)
            with open(f"{DATA_DIR}/{domain}_ssl_results_{timestamp}.json", "w") as f:
                json.dump(ssl_results, f, indent=2)
            with open(f"{DATA_DIR}/{domain}_tech_stack_{timestamp}.json", "w") as f:
                json.dump(tech_stack, f, indent=2)

            st.success("All results saved to /data folder")


def main() -> None:
    """Launch the dashboard with a simple sidebar navigation."""
    st.set_page_config(page_title="UpGuard Prototype", layout="wide")

    page = st.sidebar.selectbox(
        "Navigation", ["Risk Overview", "Run Scanners"], index=0
    )

    if page == "Risk Overview":
        render_overview()
    else:
        render_scanners()


if __name__ == "__main__":
    main()