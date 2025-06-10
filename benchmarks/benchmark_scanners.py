import time
from src.Scanners.ssl_checker import scan_subdomains
from src.Scanners.tech_scanner import detect_technologies

example_domains = ["example.com", "python.org", "github.com"]
example_assets = [{"subdomain": d} for d in example_domains]

print("Benchmarking SSL scanner...")
start = time.perf_counter()
scan_subdomains(example_assets, workers=1)
seq = time.perf_counter() - start
start = time.perf_counter()
scan_subdomains(example_assets, workers=10)
async_time = time.perf_counter() - start
print(f"Sequential: {seq:.2f}s, Async: {async_time:.2f}s")

print("\nBenchmarking technology scanner...")
start = time.perf_counter()
detect_technologies(example_domains, workers=1)
seq = time.perf_counter() - start
start = time.perf_counter()
detect_technologies(example_domains, workers=10)
async_time = time.perf_counter() - start
print(f"Sequential: {seq:.2f}s, Async: {async_time:.2f}s")

