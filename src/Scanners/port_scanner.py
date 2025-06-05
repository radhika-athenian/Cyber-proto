"""Lightweight asynchronous port scanner."""

import asyncio
import json
import os
from datetime import datetime
from typing import List

OUTPUT_DIR = "data"


def parse_ports(ports: str) -> List[int]:
    """Expand port ranges like '80,443,8000-8010' into a list of ints."""
    result: List[int] = []
    for part in ports.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            start, end = part.split('-')
            result.extend(range(int(start), int(end) + 1))
        else:
            result.append(int(part))
    return sorted(set(result))


async def _scan_port(ip: str, port: int, timeout: float, sem: asyncio.Semaphore) -> int | None:
    try:
        async with sem:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port), timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
            return port
    except Exception:
        return None


async def _scan_host(asset: dict, ports: List[int], timeout: float, sem: asyncio.Semaphore) -> dict:
    ip = asset.get("ip")
    if not ip:
        return {"subdomain": asset.get("subdomain"), "ip": ip, "ports": []}

    tasks = [_scan_port(ip, p, timeout, sem) for p in ports]
    open_ports = []
    for task in asyncio.as_completed(tasks):
        port = await task
        if port is not None:
            open_ports.append({"port": port, "protocol": "tcp", "state": "open"})
    return {"subdomain": asset.get("subdomain"), "ip": ip, "ports": open_ports}


def scan_ports(asset_list, ports: str = "1-100", workers: int = 100, timeout: float = 1.0):
    """Run asynchronous port scans for each asset."""
    port_list = parse_ports(ports)
    sem = asyncio.Semaphore(workers)

    async def runner():
        tasks = [
            _scan_host(asset, port_list, timeout, sem) for asset in asset_list
        ]
        return await asyncio.gather(*tasks)

    return asyncio.run(runner())


def save_results(domain: str, data: list):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, f"{domain}_ports_{timestamp}.json")
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Port scan results saved to {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Async Port Scanner")
    parser.add_argument("--domain", required=True, help="Target domain")
    parser.add_argument("--input", required=True, help="Path to resolved subdomain JSON")
    parser.add_argument("--ports", default="1-100", help="Port range, e.g. 1-1024")
    parser.add_argument("--workers", type=int, default=100, help="Concurrent connections")
    parser.add_argument("--timeout", type=float, default=1.0, help="Connection timeout seconds")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        assets = json.load(f)

    results = scan_ports(assets, ports=args.ports, workers=args.workers, timeout=args.timeout)
    save_results(args.domain, results)