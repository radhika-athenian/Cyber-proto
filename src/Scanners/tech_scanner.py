import argparse
import os
import re
import requests
import asyncio
import aiohttp
from Wappalyzer import Wappalyzer, WebPage

from src.utils import helpers
from src.utils.logger import get_logger

logger = get_logger(__name__)


def is_valid_hostname(hostname):
    """Validate if hostname is a valid domain"""
    if ' ' in hostname or not hostname or len(hostname) > 253:
        return False
    return re.match(r"^(?!-)[A-Za-z0-9.-]+(?<!-)$", hostname) is not None


def load_domains(asset_file):
    """Load and validate subdomains from JSON asset file"""
    data = helpers.load_json(asset_file, default=[])
    domains = [entry['subdomain'].strip() for entry in data if 'subdomain' in entry]
    return [d for d in domains if is_valid_hostname(d)]


async def _scan_domain_async(session, domain: str, wappalyzer, timeout: int) -> dict:
    url = f"https://{domain}"
    logger.info(f"Scanning {url}")
    try:
        async with session.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"}) as response:
            text = await response.text()
            r = requests.Response()
            r.status_code = response.status
            r._content = text.encode()
            r.headers = response.headers
            r.url = str(response.url)
            webpage = WebPage.new_from_response(r)
            tech = wappalyzer.analyze(webpage)
            if isinstance(tech, set):
                tech = list(tech)
    except Exception as e:
        logger.error(f"Failed to scan {domain}: {e}")
        tech = []
    return {"subdomain": domain, "technologies": tech}


def detect_technologies(domains, workers: int = 50, timeout: int = 3):
    """Use Wappalyzer to detect tech stack on domains asynchronously."""

    async def run_all():
        wappalyzer = Wappalyzer.latest()
        connector = aiohttp.TCPConnector(limit=workers, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [_scan_domain_async(session, d, wappalyzer, timeout) for d in domains]
            return await asyncio.gather(*tasks)

    return asyncio.run(run_all())


def save_results(results, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    helpers.save_json(results, output_path)
    logger.info(f"Saved technology scan results to: {output_path}")


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
        logger.exception(f"Fatal error: {e}")
