import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import joblib
from pathlib import Path

from src.utils import config, helpers
from src.utils.logger import get_logger

logger = get_logger(__name__)

input_path = config.DATA_DIR / 'leaks.json'
output_path = config.DATA_DIR / 'classified_leaks.json'

# Load model & vectorizer
clf = joblib.load(config.MODELS_DIR / 'leak_model.pkl')
vectorizer = joblib.load(config.MODELS_DIR / 'vectorizer.pkl')

# Load scraped leaks
leaks = helpers.load_json(input_path, default=[])

# Predict and label
classified = []
for entry in leaks:
    text = entry['content']
    X = vectorizer.transform([text])
    pred = clf.predict(X)[0]
    entry['label'] = pred
    classified.append(entry)

# Save output
helpers.save_json(classified, output_path)
logger.info(f"Classified {len(classified)} leaks and saved to {output_path}")