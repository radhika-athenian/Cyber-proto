import ssl
import socket
import json
import os
import argparse
import logging
import asyncio
from datetime import datetime
from dateutil import parser as date_parser
import pytz

from src.utils import config, helpers
from src.utils.logger import get_logger

logger = get_logger(__name__)

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

async def get_ssl_certificate_async(domain):
    """Asynchronous version of get_ssl_certificate using asyncio connections."""
    try:
        context = ssl.create_default_context()
        reader, writer = await asyncio.open_connection(domain, 443, ssl=context)
        cert = writer.get_extra_info("ssl_object").getpeercert()
        writer.close()
        await writer.wait_closed()
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

def scan_subdomains(subdomains, workers: int = 100):
    """Scan subdomains concurrently for SSL certificates."""

    async def worker(item):
        domain = item["subdomain"]
        logger.info(f"Checking SSL for {domain}")
        cert = await get_ssl_certificate_async(domain)
        cert_info = parse_certificate_info(cert)
        cert_info["subdomain"] = domain
        return cert_info

    async def run_all():
        sem = asyncio.Semaphore(workers)

        async def sem_worker(item):
            async with sem:
                return await worker(item)

        tasks = [asyncio.create_task(sem_worker(item)) for item in subdomains]
        return await asyncio.gather(*tasks)

    return asyncio.run(run_all())

def save_results(domain, results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(config.DATA_DIR, f"{domain}_ssl_results_{timestamp}.json")
    os.makedirs(config.DATA_DIR, exist_ok=True)
    helpers.save_json(results, output_path)
    logger.info(f"SSL scan results saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SSL Certificate Checker")
    parser.add_argument("--domain", required=True, help="Target domain")
    parser.add_argument("--input", required=True, help="Path to resolved subdomains JSON")
    parser.add_argument("--workers", type=int, default=100, help="Concurrent connections")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        logger.error(f"Input file {args.input} not found.")
        exit(1)

    subdomains = helpers.load_json(args.input, default=[])

    results = scan_subdomains(subdomains, workers=args.workers)
    save_results(args.domain, results)
