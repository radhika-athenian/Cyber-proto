"""Convenience wrapper to run all scanners from the command line."""
from Scanners.run_scanners import run_all

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run all scanners for a target domain")
    parser.add_argument("--domain", required=True, help="Target root domain (e.g., example.com)")
    parser.add_argument("--ports", default="1-100", help="Port range (default: 1-100)")
    parser.add_argument("--workers", type=int, default=100, help="Concurrent connections")
    args = parser.parse_args()

    run_all(args.domain, ports=args.ports, workers=args.workers)
