import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from src.Scanners.run_scanners import run_all


def main():
    parser = argparse.ArgumentParser(
        description="Run all scanners for a target domain.")
    parser.add_argument("--domain", required=True,
                        help="Target root domain (e.g. example.com)")
    parser.add_argument("--ports", default="1-100",
                        help="Port range to scan (default: 1-100)")
    parser.add_argument("--workers", type=int, default=100,
                        help="Concurrent connections")
    args = parser.parse_args()

    results = run_all(args.domain, ports=args.ports, workers=args.workers)

    if isinstance(results, dict):
        print("\nGenerated files:")
        for key, path in results.items():
            print(f" - {key}: {path}")
    elif isinstance(results, (list, tuple)):
        labels = ["assets", "ports", "ssl", "tech_stack"]
        print("\nGenerated files:")
        for label, path in zip(labels, results):
            print(f" - {label}: {path}")


if __name__ == "__main__":
    main()