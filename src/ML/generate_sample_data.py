import json
import random
import os

OUTPUT_FILE = 'src\ML\models\sample_risk_training_data.json'
NUM_SAMPLES = 100

def generate_sample():
    sample_data = []

    for i in range(NUM_SAMPLES):
        domain = f"testdomain{i}.com"

        open_ports = random.randint(1, 20)
        high_risk_ports = random.randint(0, min(open_ports, 5))
        weak_ssl = random.choice([0, 1])
        leak_count = random.randint(0, 10)
        subdomain_count = random.randint(1, 15)

        # Simple risk heuristic formula
        risk_score = (
            (open_ports * 2) +
            (high_risk_ports * 5) +
            (leak_count * 8) +
            (weak_ssl * 15) +
            (subdomain_count)
        )
        risk_score = min(int(risk_score), 100)

        sample_data.append({
            "domain": domain,
            "features": {
                "open_ports": open_ports,
                "high_risk_ports": high_risk_ports,
                "has_weak_ssl": bool(weak_ssl),
                "leak_count": leak_count,
                "subdomain_count": subdomain_count
            },
            "risk_score": risk_score
        })

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(sample_data, f, indent=2)

    print(f"[+] Generated {NUM_SAMPLES} synthetic samples at {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_sample()
