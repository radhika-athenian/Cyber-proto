import json
from pathlib import Path

from src.utils.helpers import load_json, save_json
from src.utils.risk_calculator import calculate_risk_score


def test_save_and_load_json(tmp_path):
    data = {"foo": 1, "bar": [1, 2, 3]}
    file_path = tmp_path / "data.json"
    save_json(data, file_path)
    assert file_path.exists()
    loaded = load_json(file_path)
    assert loaded == data


def test_load_json_missing(tmp_path):
    missing = tmp_path / "missing.json"
    result = load_json(missing, default={"missing": True})
    assert result == {"missing": True}


def test_calculate_risk_score_basic():
    assert calculate_risk_score([10, 20, 30]) == 20.0


def test_calculate_risk_score_invalid_values():
    scores = [10, None, "bad", 20]
    assert calculate_risk_score(scores) == 15.0
    assert calculate_risk_score([]) == 0
