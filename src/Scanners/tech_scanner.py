import argparse
import json
import os
import re
import requests
from Wappalyzer import Wappalyzer, WebPage
from concurrent.futures import ThreadPoolExecutor, as_completed


def is_valid_hostname(hostname):
    """Validate if hostname is a valid domain"""
    if ' ' in hostname or not hostname or len(hostname) > 253:
        return False
    return re.match(r"^(?!-)[A-Za-z0-9.-]+(?<!-)$", hostname) is not None


def load_domains(asset_file):
    """Load and validate subdomains from JSON asset file"""
    with open(asset_file, 'r') as f:
        data = json.load(f)
    domains = [entry['subdomain'].strip() for entry in data if 'subdomain' in entry]
    return [d for d in domains if is_valid_hostname(d)]


def _scan_domain(domain: str, wappalyzer, timeout: int) -> dict:
    url = f"https://{domain}"
    print(f"[+] Scanning {url}")
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        webpage = WebPage.new_from_response(response)
        tech = wappalyzer.analyze(webpage)
        if isinstance(tech, set):
            tech = list(tech)
    except Exception as e:
        print(f"[-] Failed to scan {domain}: {e}")
        tech = []
    return {"subdomain": domain, "technologies": tech}


def detect_technologies(domains, workers: int = 50, timeout: int = 3):
    """Use Wappalyzer to detect tech stack on domains in parallel."""
    wappalyzer = Wappalyzer.latest()
    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_scan_domain, d, wappalyzer, timeout) for d in domains]
        for future in as_completed(futures):
            results.append(future.result())
    return results


def save_results(results, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Saved technology scan results to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Technology scanner using Wappalyzer")
    parser.add_argument("--input", required=True, help="Path to asset JSON file")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    args = parser.parse_args()

    try:
        domains = load_domains(args.input)
        results = detect_technologies(domains)
        save_results(results, args.output)
    except Exception as e:
        print(f"[✗] Fatal error: {e}")