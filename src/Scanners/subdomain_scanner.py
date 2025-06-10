# scanners/subdomain_scanner.py
import subprocess
import socket
import os
from datetime import datetime

from src.utils import config, helpers
from src.utils.logger import get_logger

logger = get_logger(__name__)
OUTPUT_DIR = str(config.DATA_DIR)

def run_sublist3r(domain):
    """Runs Sublist3r to find subdomains."""
    logger.info(f"Scanning subdomains for: {domain}")
    try:
        result = subprocess.run(
            ["sublist3r", "-d", domain, "-o", f"{OUTPUT_DIR}/{domain}_subdomains.txt"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("Sublist3r scan complete.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Sublist3r failed: {e.stderr}")
        return []

    with open(f"{OUTPUT_DIR}/{domain}_subdomains.txt", "r") as file:
        subdomains = [line.strip() for line in file if line.strip()]
    
    return subdomains

def resolve_subdomains(subdomains):
    """Resolves subdomains to IP addresses."""
    resolved = []
    for sub in subdomains:
        try:
            ip = socket.gethostbyname(sub)
            resolved.append({"subdomain": sub, "ip": ip})
        except socket.gaierror:
            logger.warning(f"Unable to resolve {sub}")
            resolved.append({"subdomain": sub, "ip": None})
    return resolved

def save_results(domain, data):
    """Saves results as a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"{domain}_assets_{timestamp}.json")
    helpers.save_json(data, output_file)
    logger.info(f"Results saved to {output_file}")

def main(domain):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    subdomains = run_sublist3r(domain)
    resolved = resolve_subdomains(subdomains)
    save_results(domain, resolved)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Subdomain Scanner")
    parser.add_argument("--domain", required=True, help="Target domain (e.g., example.com)")
    args = parser.parse_args()

    main(args.domain)
