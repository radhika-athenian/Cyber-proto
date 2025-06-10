import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from src.Scanners.subdomain_scanner import run_sublist3r, resolve_subdomains
from src.Scanners.port_scanner import scan_ports
from src.Scanners.ssl_checker import scan_subdomains as scan_ssl
from src.Scanners.tech_scanner import detect_technologies


def save_json(domain, prefix, data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/{domain}_{prefix}_{timestamp}.json"
    os.makedirs("data", exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[✓] Saved {prefix} results to {filename}")
    return filename


def run_all(domain, ports: str = "1-100", workers: int = 100):
    print(f"[•] Running all scanners for: {domain}")

    # --- Subdomain scan
    subdomains = run_sublist3r(domain)
    resolved = resolve_subdomains(subdomains)
    assets_file = save_json(domain, "assets", resolved)

    # Run other scanners concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_ports = executor.submit(scan_ports, resolved, ports=ports)
        future_ssl = executor.submit(scan_ssl, resolved)
        future_tech = executor.submit(
            detect_technologies,
            [item["subdomain"] for item in resolved],
            workers=workers,
        )

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

    return {
        "assets": assets_file,
        "ports": ports_file,
        "ssl": ssl_file,
        "tech": tech_file,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run all scanners for a target domain.")
    parser.add_argument("--domain", required=True, help="Target root domain (e.g. example.com)")
    parser.add_argument("--ports", default="1-100", help="Port range (default: 1-100)")
    parser.add_argument("--workers", type=int, default=100, help="Concurrent connections")
    args = parser.parse_args()

    run_all(args.domain, ports=args.ports, workers=args.workers)
