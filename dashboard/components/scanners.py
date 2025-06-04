import streamlit as st
import json
import os
from Scanners.subdomain_scanner import run_sublist3r, resolve_subdomains
from Scanners.port_scanner import scan_ports
from Scanners.ssl_checker import scan_subdomains as scan_ssl
from Scanners.tech_scanner import detect_technologies

st.title("🔍 Asset Scanners")

with st.form("scanner_form"):
    domain = st.text_input("Enter domain to scan (e.g., example.com):")
    submit = st.form_submit_button("Run Scanners")

if submit:
    if not domain:
        st.error("Please enter a valid domain.")
    else:
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
        tech_stack = detect_technologies([item['subdomain'] for item in resolved_subdomains])
        st.success("Technology fingerprinting complete")
        st.json(tech_stack)

        if st.checkbox("💾 Save all results to /data"):
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("data", exist_ok=True)

            with open(f"data/{domain}_assets_{timestamp}.json", "w") as f:
                json.dump(resolved_subdomains, f, indent=2)
            with open(f"data/{domain}_ports_{timestamp}.json", "w") as f:
                json.dump(ports, f, indent=2)
            with open(f"data/{domain}_ssl_results_{timestamp}.json", "w") as f:
                json.dump(ssl_results, f, indent=2)
            with open(f"data/{domain}_tech_stack_{timestamp}.json", "w") as f:
                json.dump(tech_stack, f, indent=2)

            st.success("All results saved to /data folder")
