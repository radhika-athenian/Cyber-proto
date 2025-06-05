"""Convenience wrapper to run all scanners from the command line."""
from Scanners.run_scanners import run_all

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run all scanners for a target domain")
    parser.add_argument("--domain", required=True, help="Target root domain (e.g., example.com)")
    parser.add_argument("--ports", default="1-1000", help="Port range for nmap (default: 1-1000)")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker threads")
    args = parser.parse_args()

    run_all(args.domain, ports=args.ports, workers=args.workers)
