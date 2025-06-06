import ssl
import socket
import json
import os
import argparse
from datetime import datetime
from dateutil import parser as date_parser
import pytz
import logging

# Set up logging
logging.basicConfig(filename='ssl_check.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

def get_ssl_certificate(domain):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return cert
    except Exception as e:
        logging.error(f"Error retrieving SSL certificate for {domain}: {e}")
        return {"error": str(e)}

def parse_certificate_info(cert):
    if "error" in cert:
        return cert

    try:
        expiry_date = date_parser.parse(cert['notAfter'])
        current_time = datetime.now(pytz.utc)
        days_to_expiry = (expiry_date - current_time).days

        info = {
            "Issuer": dict(x[0] for x in cert['issuer']),
            "Subject": dict(x[0] for x in cert['subject']),
            "Serial Number": cert['serialNumber'],
            "Version": cert['version'],
            "Not Before": cert['notBefore'],
            "Not After": cert['notAfter'],
            "Days to Expiry": days_to_expiry,
            "is_expired": days_to_expiry < 0
        }
        return info
    except Exception as e:
        return {"error": f"Parsing error: {e}"}

def scan_subdomains(subdomains):
    results = []
    for item in subdomains:
        domain = item["subdomain"]
        print(f"[+] Checking SSL for {domain}")
        cert = get_ssl_certificate(domain)
        cert_info = parse_certificate_info(cert)
        cert_info["subdomain"] = domain
        results.append(cert_info)
    return results

def save_results(domain, results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"data/{domain}_ssl_results_{timestamp}.json"
    os.makedirs("data", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[✓] SSL scan results saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SSL Certificate Checker")
    parser.add_argument("--domain", required=True, help="Target domain")
    parser.add_argument("--input", required=True, help="Path to resolved subdomains JSON")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[!] Input file {args.input} not found.")
        exit(1)

    with open(args.input, "r") as f:
        subdomains = json.load(f)

    results = scan_subdomains(subdomains)
    save_results(args.domain, results)
