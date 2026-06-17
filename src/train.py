import argparse
import json

import joblib
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import (
    BEST_MODELS_PATH,
    EXPERIMENTS,
    MODEL_METADATA_PATH,
    MODEL_PATH,
    MODELS_DIR,
    PROCESSED_DATA_PATH,
    TARGET_COLUMN,
)


def ensure_directories() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def build_pipeline(k: int, use_scaler: bool) -> Pipeline:
    steps = []
    if use_scaler:
        steps.append(("scaler", StandardScaler()))
    steps.append(("model", KNeighborsRegressor(n_neighbors=k)))
    return Pipeline(steps)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--selection",
        choices=["baseline", "overall"],
        default="baseline",
        help="Which validated selection rule to use.",
    )
    args = parser.parse_args()

    ensure_directories()

    df = pd.read_csv(PROCESSED_DATA_PATH)
    summary = json.loads(BEST_MODELS_PATH.read_text(encoding="utf-8"))

    selected_key = (
        "selected_baseline_model" if args.selection == "baseline" else "overall_best"
    )
    selected = summary[selected_key]

    experiment_name = selected["experiment"]
    config = EXPERIMENTS[experiment_name]
    k = int(selected["k"])

    X = df[config["feature_columns"]]
    y = df[TARGET_COLUMN]

    pipeline = build_pipeline(k=k, use_scaler=config["use_scaler"])
    pipeline.fit(X, y)

    joblib.dump(pipeline, MODEL_PATH)

    metadata = {
        "selection": args.selection,
        "experiment": experiment_name,
        "feature_columns": config["feature_columns"],
        "use_scaler": config["use_scaler"],
        "k": k,
        "training_rows": int(len(df)),
        "target_column": TARGET_COLUMN,
    }

    MODEL_METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Saved trained model to: {MODEL_PATH}")
    print(f"Saved model metadata to: {MODEL_METADATA_PATH}")


if __name__ == "__main__":
    main()
