import json
import joblib
from pathlib import Path

input_path = 'data/leaks.json'
output_path = 'data/classified_leaks.json'

# Load model & vectorizer
clf = joblib.load('ML/models/leak_model.pkl')
vectorizer = joblib.load('ML/models/vectorizer.pkl')

# Load scraped leaks
with open(input_path, 'r', encoding='utf-8') as f:
    leaks = json.load(f)

# Predict and label
classified = []
for entry in leaks:
    text = entry['content']
    X = vectorizer.transform([text])
    pred = clf.predict(X)[0]
    entry['label'] = pred
    classified.append(entry)

# Save output
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(classified, f, indent=2)

print(f"[✓] Classified {len(classified)} leaks and saved to {output_path}")
