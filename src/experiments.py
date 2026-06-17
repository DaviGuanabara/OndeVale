import json

import pandas as pd
from sklearn.model_selection import KFold, cross_validate
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import (
    BEST_MODELS_PATH,
    CV_SPLITS,
    EXPERIMENT_RESULTS_PATH,
    EXPERIMENTS,
    EXPERIMENTS_DIR,
    K_GRID,
    PROCESSED_DATA_PATH,
    RANDOM_STATE,
    TARGET_COLUMN,
)


def ensure_directories() -> None:
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)


def load_processed_data() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DATA_PATH)


def build_pipeline(k: int, use_scaler: bool) -> Pipeline:
    steps = []
    if use_scaler:
        steps.append(("scaler", StandardScaler()))
    steps.append(("model", KNeighborsRegressor(n_neighbors=k)))
    return Pipeline(steps)


def evaluate_experiment(df: pd.DataFrame, experiment_name: str, config: dict) -> pd.DataFrame:
    X = df[config["feature_columns"]]
    y = df[TARGET_COLUMN]

    cv = KFold(n_splits=CV_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    scoring = {
        "mae": "neg_mean_absolute_error",
        "rmse": "neg_root_mean_squared_error",
        "r2": "r2",
    }

    rows = []
    for k in K_GRID:
        pipeline = build_pipeline(k=k, use_scaler=config["use_scaler"])
        scores = cross_validate(
            pipeline,
            X,
            y,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
        )
        rows.append(
            {
                "experiment": experiment_name,
                "description": config["description"],
                "feature_columns": ",".join(config["feature_columns"]),
                "use_scaler": config["use_scaler"],
                "k": k,
                "mae_mean": -scores["test_mae"].mean(),
                "rmse_mean": -scores["test_rmse"].mean(),
                "r2_mean": scores["test_r2"].mean(),
            }
        )

    return pd.DataFrame(rows)


def select_best(df: pd.DataFrame) -> dict:
    row = df.sort_values(
        by=["rmse_mean", "mae_mean", "r2_mean"],
        ascending=[True, True, False],
    ).iloc[0]
    return row.to_dict()


def main() -> None:
    ensure_directories()
    df = load_processed_data()

    frames = []
    for experiment_name, config in EXPERIMENTS.items():
        frames.append(evaluate_experiment(df, experiment_name, config))

    results = pd.concat(frames, ignore_index=True)
    results = results.sort_values(["experiment", "k"]).reset_index(drop=True)
    results.to_csv(EXPERIMENT_RESULTS_PATH, index=False)

    overall_best = select_best(results)

    metric_results = results[results["experiment"].isin(["B_metric_no_norm", "C_metric_std"])].copy()
    baseline_best = select_best(metric_results)

    summary = {
        "overall_best": overall_best,
        "selected_baseline_model": baseline_best,
        "selection_rule": (
            "The final baseline model must use metric coordinates [x, y]. "
            "Experiment A is kept as an ablation/comparison, but the deployed "
            "baseline is selected from experiments B and C only."
        ),
    }

    BEST_MODELS_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Saved experiment results to: {EXPERIMENT_RESULTS_PATH}")
    print(f"Saved best-model summary to: {BEST_MODELS_PATH}")


if __name__ == "__main__":
    main()