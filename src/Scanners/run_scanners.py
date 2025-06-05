import os
import json
from datetime import datetime

from Scanners.subdomain_scanner import run_sublist3r, resolve_subdomains
from Scanners.port_scanner import scan_ports, save_results as save_ports
from Scanners.ssl_checker import scan_subdomains as scan_ssl
from Scanners.tech_scanner import load_domains, detect_technologies, save_results as save_tech
from concurrent.futures import ThreadPoolExecutor

def save_json(domain, prefix, data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/{domain}_{prefix}_{timestamp}.json"
    os.makedirs("data", exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[✓] Saved {prefix} results to {filename}")
    return filename

<<<<<<< HEAD
<<<<<<<< HEAD:src/Scanners/run_scanners.py
def run_all(domain, ports: str = "1-1000", workers: int = 4):
========
def run_all(domain, ports: str = "1-100", workers: int = 100):
>>>>>>>> origin/lpxcmz-codex/debug-scripts-and-create-streamlit-dashboard:Scanners/run_scanners.py
=======
<<<<<<< HEAD:Scanners/run_scanners.py
def run_all(domain, ports: str = "1-100", workers: int = 100):
=======
def run_all(domain, ports: str = "1-1000", workers: int = 4):
>>>>>>> origin/main:src/Scanners/run_scanners.py
>>>>>>> origin/lpxcmz-codex/debug-scripts-and-create-streamlit-dashboard
    print(f"[•] Running all scanners for: {domain}")

    # --- Subdomain scan
    subdomains = run_sublist3r(domain)
    resolved = resolve_subdomains(subdomains)
    assets_file = save_json(domain, "assets", resolved)

    # Run other scanners concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_ports = executor.submit(scan_ports, resolved, ports=ports, workers=workers)
        future_ssl = executor.submit(scan_ssl, resolved, workers=workers)
        future_tech = executor.submit(detect_technologies, [item['subdomain'] for item in resolved], workers=workers)

        port_results = future_ports.result()
        ssl_results = future_ssl.result()
        tech_results = future_tech.result()

    ports_file = save_json(domain, "ports", port_results)
    ssl_file = save_json(domain, "ssl_results", ssl_results)
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
<<<<<<< HEAD
<<<<<<<< HEAD:src/Scanners/run_scanners.py
    parser.add_argument("--ports", default="1-1000", help="Port range for nmap")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker threads")
========
    parser.add_argument("--ports", default="1-100", help="Port range (default: 1-100)")
    parser.add_argument("--workers", type=int, default=100, help="Concurrent connections")
>>>>>>>> origin/lpxcmz-codex/debug-scripts-and-create-streamlit-dashboard:Scanners/run_scanners.py
=======
<<<<<<< HEAD:Scanners/run_scanners.py
    parser.add_argument("--ports", default="1-100", help="Port range (default: 1-100)")
    parser.add_argument("--workers", type=int, default=100, help="Concurrent connections")
=======
    parser.add_argument("--ports", default="1-1000", help="Port range for nmap")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker threads")
>>>>>>> origin/main:src/Scanners/run_scanners.py
>>>>>>> origin/lpxcmz-codex/debug-scripts-and-create-streamlit-dashboard
    args = parser.parse_args()

    run_all(args.domain, ports=args.ports, workers=args.workers)
