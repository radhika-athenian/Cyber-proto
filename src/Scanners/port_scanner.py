# scanners/port_scanner.py

import nmap
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

OUTPUT_DIR = "data"

def _scan_host(asset, ports, timeout):
    ip = asset.get("ip")
    if not ip:
        return {"subdomain": asset.get("subdomain"), "ip": ip, "ports": []}
    try:
        print(f"[+] Scanning ports on {ip} ({asset['subdomain']})...")
        scanner = nmap.PortScanner()
        scanner.scan(ip, ports, arguments=f"--max-retries 2 --host-timeout {timeout}s")
        ports_found = []
        for proto in scanner[ip].all_protocols():
            lport = scanner[ip][proto].keys()
            for port in sorted(lport):
                state = scanner[ip][proto][port]['state']
                ports_found.append({"port": port, "protocol": proto, "state": state})
        return {"subdomain": asset["subdomain"], "ip": ip, "ports": ports_found}
    except Exception as e:
        print(f"[!] Error scanning {ip}: {e}")
        return {
            "subdomain": asset.get("subdomain"),
            "ip": ip,
            "ports": [],
            "error": str(e),
        }


def scan_ports(asset_list, ports="1-1000", workers: int = 4, timeout: int = 60):
    """Scan open ports on a list of assets in parallel."""
    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_scan_host, asset, ports, timeout) for asset in asset_list]
        for future in as_completed(futures):
            results.append(future.result())
    return results

def save_results(domain, data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"{domain}_ports_{timestamp}.json")
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Port scan results saved to {output_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Port Scanner")
    parser.add_argument("--domain", required=True, help="Target domain")
    parser.add_argument("--input", required=True, help="Path to resolved subdomain JSON")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        assets = json.load(f)

    results = scan_ports(assets)
    save_results(args.domain, results)
