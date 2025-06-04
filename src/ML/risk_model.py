import json
import os
import argparse
import joblib
import numpy as np

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []

def build_features(asset_file, ports_file, ssl_file, leaks_file):
    assets = load_json(asset_file)
    ports_data = load_json(ports_file)
    ssl_data = load_json(ssl_file)
    leaks = load_json(leaks_file)

    leak_map = {}
    for leak in leaks:
        domain = leak.get("subdomain") or leak.get("source", "unknown")
        if leak.get("label") == "sensitive":
            leak_map[domain] = leak_map.get(domain, 0) + 1

    ssl_map = {item['subdomain']: item for item in ssl_data}
    ports_map = {item['subdomain']: item['ports'] for item in ports_data}

    features = []
    domains = []

    for entry in assets:
        domain = entry['subdomain']
        domains.append(domain)

        open_ports = ports_map.get(domain, [])
        high_risk_ports = [22, 23, 3389]
        risky_open = sum(1 for p in open_ports if p in high_risk_ports)

        ssl_info = ssl_map.get(domain, {})
        ssl_expired = ssl_info.get('expired', False)
        ssl_days = ssl_info.get('days_to_expiry', 0)
        weak_ssl = ssl_expired or ssl_days < 15

        leak_count = leak_map.get(domain, 0)

        features.append([
            len(open_ports),
            risky_open,
            int(weak_ssl),
            leak_count,
            entry.get("subdomain_count", 1)
        ])

    return np.array(features), domains

def score_domains(args):
    X, domains = build_features(args.assets, args.ports, args.ssl, args.leaks)
    model = joblib.load(args.model)
    scores = model.predict(X)

    result = []
    for domain, score, row in zip(domains, scores, X):
        result.append({
            "subdomain": domain,
            "risk_score": int(min(max(score, 0), 100)),
            "details": {
                "open_ports": int(row[0]),
                "high_risk_ports": int(row[1]),
                "has_weak_ssl": bool(row[2]),
                "leak_count": int(row[3]),
                "subdomain_count": int(row[4])
            }
        })

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"[+] Saved risk scores to {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Risk scoring based on asset data")
    parser.add_argument('--assets', required=True, help='Path to assets JSON file')
    parser.add_argument('--ports', required=True, help='Path to ports JSON file')
    parser.add_argument('--ssl', required=True, help='Path to SSL JSON file')
    parser.add_argument('--leaks', required=True, help='Path to classified leaks JSON file')
    parser.add_argument('--model', required=True, help='Path to trained ML model (.pkl)')
    parser.add_argument('--output', default='data/risk_scores.json', help='Output path for results')

    args = parser.parse_args()
    score_domains(args)
