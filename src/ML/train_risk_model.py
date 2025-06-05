import json
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

DATA_FILE = 'ai/models/sample_risk_training_data.json'
MODEL_PATH = 'ai/models/risk_model.pkl'

def load_training_data(path):
    with open(path, 'r') as f:
        raw_data = json.load(f)

    X, y = [], []

    for item in raw_data:
        feats = item['features']
        X.append([
            feats['open_ports'],
            feats['high_risk_ports'],
            int(feats['has_weak_ssl']),
            feats['leak_count'],
            feats['subdomain_count']
        ])
        y.append(item['risk_score'])

    return np.array(X), np.array(y)

def train_and_save_model():
    X, y = load_training_data(DATA_FILE)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
    print(f"R² Score: {r2_score(y_test, y_pred):.2f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"[+] Saved trained model to {MODEL_PATH}")

if __name__ == "__main__":
    train_and_save_model()
