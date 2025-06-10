# scanners/port_scanner.py
import nmap
import os
from datetime import datetime

from src.utils import config, helpers
from src.utils.logger import get_logger

logger = get_logger(__name__)
OUTPUT_DIR = str(config.DATA_DIR)

def scan_ports(asset_list, ports="1-1000"):
    """Scans open ports on a list of assets with Nmap."""
    scanner = nmap.PortScanner()
    results = []

    for asset in asset_list:
        ip = asset.get("ip")
        if not ip:
            continue
        try:
            logger.info(f"Scanning ports on {ip} ({asset['subdomain']})")
            scanner.scan(ip, ports)
            ports_found = []

            for proto in scanner[ip].all_protocols():
                lport = scanner[ip][proto].keys()
                for port in sorted(lport):
                    state = scanner[ip][proto][port]["state"]
                    ports_found.append({
                        "port": port,
                        "protocol": proto,
                        "state": state
                    })

            results.append({
                "subdomain": asset["subdomain"],
                "ip": ip,
                "ports": ports_found
            })

        except Exception as e:
            logger.error(f"Error scanning {ip}: {e}")
            results.append({
                "subdomain": asset["subdomain"],
                "ip": ip,
                "ports": [],
                "error": str(e)
            })

    return results

def save_results(domain, data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"{domain}_ports_{timestamp}.json")
    helpers.save_json(data, output_file)
    logger.info(f"Port scan results saved to {output_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Port Scanner")
    parser.add_argument("--domain", required=True, help="Target domain")
    parser.add_argument("--input", required=True, help="Path to resolved subdomain JSON")
    args = parser.parse_args()

    assets = helpers.load_json(args.input, default=[])

    results = scan_ports(assets)
    save_results(args.domain, results)
