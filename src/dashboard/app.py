"""Streamlit dashboard for running scanners and viewing risk scores."""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from pathlib import Path
import streamlit as st

from src.Scanners.run_scanners import run_all
from src.ML.risk_model import calculate_risk_scores


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "ML" / "models" / "risk_model.pkl"


def display_scores(scores):
    if not scores:
        st.warning("No scores to display")
        return

    st.subheader("Risk Scores")
    st.table([{"Subdomain": s["subdomain"], "Score": s["risk_score"]} for s in scores])


def main():
    st.title("Athenian Tech Dashboard")

    if "scan_files" not in st.session_state:
        st.session_state["scan_files"] = {}
    if "risk_scores" not in st.session_state:
        st.session_state["risk_scores"] = []

    st.sidebar.header("Run Scanners")
    domain = st.sidebar.text_input("Target Domain")
    ports = st.sidebar.text_input("Port Range", "1-100")
    workers = st.sidebar.number_input("Workers", min_value=1, max_value=500, value=100)
    leaks_file = st.sidebar.text_input(
        "Leaks JSON",
        "data/classified_leaks.json",
        key="initial_leaks_json",
    )

    if st.sidebar.button("Start Scans"):
        if domain:
            files = run_all(domain, ports=ports, workers=workers)
            st.session_state["scan_files"] = files
            scores = calculate_risk_scores(
                files["assets"],
                files["ports"],
                files["ssl"],
                leaks_file,
                str(MODEL_PATH),
            )
            st.session_state["risk_scores"] = scores
        else:
            st.sidebar.error("Please provide a domain")

    st.sidebar.header("Recompute Risk Scores")
    recompute_assets = st.sidebar.text_input(
        "Assets JSON", st.session_state["scan_files"].get("assets", "")
    )
    recompute_ports = st.sidebar.text_input(
        "Ports JSON", st.session_state["scan_files"].get("ports", "")
    )
    recompute_ssl = st.sidebar.text_input(
        "SSL JSON", st.session_state["scan_files"].get("ssl", "")
    )
    recompute_leaks = st.sidebar.text_input(
        "Leaks JSON",
        leaks_file,
        key="recompute_leaks_json",
    )

    if st.sidebar.button("Recompute"):
        if all([recompute_assets, recompute_ports, recompute_ssl, recompute_leaks]):
            scores = calculate_risk_scores(
                recompute_assets,
                recompute_ports,
                recompute_ssl,
                recompute_leaks,
                str(MODEL_PATH),
            )
            st.session_state["risk_scores"] = scores
        else:
            st.sidebar.error("Please provide all result paths")

    display_scores(st.session_state["risk_scores"])


if __name__ == "__main__":
    main()

