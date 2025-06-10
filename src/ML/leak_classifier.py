import joblib
from pathlib import Path

from src.utils import config, helpers
from src.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_INPUT = config.DATA_DIR / "leaks.json"
DEFAULT_OUTPUT = config.DATA_DIR / "classified_leaks.json"


def classify_leaks(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> None:
    """Load leaks, apply the classifier and save labeled results."""
    clf = joblib.load(config.MODELS_DIR / "leak_model.pkl")
    vectorizer = joblib.load(config.MODELS_DIR / "vectorizer.pkl")

    leaks = helpers.load_json(input_path, default=[])
    classified = []
    for entry in leaks:
        text = entry["content"]
        X = vectorizer.transform([text])
        pred = clf.predict(X)[0]
        entry["label"] = pred
        classified.append(entry)

    helpers.save_json(classified, output_path)
    logger.info(f"Classified {len(classified)} leaks and saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Classify leaked data")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to leak JSON")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Path to save labeled JSON")
    args = parser.parse_args()

    classify_leaks(Path(args.input), Path(args.output))
