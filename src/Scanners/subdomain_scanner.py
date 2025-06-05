# scanners/subdomain_scanner.py

import subprocess
import socket
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

OUTPUT_DIR = "data"
DOMAIN = "example.com"  # Replace or pass as argument

<<<<<<< HEAD:Scanners/subdomain_scanner.py
def run_sublist3r(domain, timeout: int = 60):
=======
def run_sublist3r(domain, timeout: int = 300):
>>>>>>> origin/main:src/Scanners/subdomain_scanner.py
    """Runs Sublist3r to find subdomains."""
    print(f"[+] Scanning subdomains for: {domain}")
    try:
        result = subprocess.run(
            ["sublist3r", "-d", domain, "-o", f"{OUTPUT_DIR}/{domain}_subdomains.txt"],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        print("[+] Sublist3r scan complete.")
    except subprocess.CalledProcessError as e:
        print("[!] Sublist3r failed:", e.stderr)
        return []

    with open(f"{OUTPUT_DIR}/{domain}_subdomains.txt", "r") as file:
        subdomains = [line.strip() for line in file if line.strip()]
    
    return subdomains

def _resolve_one(subdomain: str, timeout: float = 5.0):
    """Resolve a single subdomain to an IP address."""
    try:
        ip = socket.gethostbyname(subdomain)
        return {"subdomain": subdomain, "ip": ip}
    except socket.gaierror:
        return {"subdomain": subdomain, "ip": None}


def resolve_subdomains(subdomains, workers: int = 10):
    """Resolve subdomains in parallel."""
    resolved = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for result in executor.map(_resolve_one, subdomains):
            resolved.append(result)
    return resolved

def save_results(domain, data):
    """Saves results as a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"{domain}_assets_{timestamp}.json")
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Results saved to {output_file}")

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
