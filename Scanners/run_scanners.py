import os
import json
from datetime import datetime

from Scanners.subdomain_scanner import run_sublist3r, resolve_subdomains
from Scanners.port_scanner import scan_ports, save_results as save_ports
from Scanners.ssl_checker import scan_subdomains as scan_ssl
from Scanners.tech_scanner import load_domains, detect_technologies, save_results as save_tech

def save_json(domain, prefix, data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/{domain}_{prefix}_{timestamp}.json"
    os.makedirs("data", exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[✓] Saved {prefix} results to {filename}")
    return filename

def run_all(domain):
    print(f"[•] Running all scanners for: {domain}")

    # --- Subdomain scan
    subdomains = run_sublist3r(domain)
    resolved = resolve_subdomains(subdomains)
    assets_file = save_json(domain, "assets", resolved)

    # --- Port scan
    port_results = scan_ports(resolved)
    ports_file = save_json(domain, "ports", port_results)

    # --- SSL scan
    ssl_results = scan_ssl(resolved)
    ssl_file = save_json(domain, "ssl_results", ssl_results)

    # --- Tech stack
    tech_results = detect_technologies([item['subdomain'] for item in resolved])
    tech_file = save_json(domain, "tech_stack", tech_results)

    print("\n[✓] All scans complete.")
    print(f" - Assets: {assets_file}")
    print(f" - Ports: {ports_file}")
    print(f" - SSL: {ssl_file}")
    print(f" - Tech Stack: {tech_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run all scanners for a target domain.")
    parser.add_argument("--domain", required=True, help="Target root domain (e.g. example.com)")
    args = parser.parse_args()

    run_all(args.domain)
