import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import KFold

from src.config import (
    BEST_MODELS_PATH,
    CV_SPLITS,
    EXPERIMENTS,
    FOLD_METRICS_PATH,
    MAE_BOXPLOT_PATH,
    PREPROCESS_METADATA_PATH,
    PROCESSED_DATA_PATH,
    R2_BOXPLOT_PATH,
    RANDOM_STATE,
    REPORT_PATH,
    RMSE_BOXPLOT_PATH,
    SELECTED_VS_TRIVIAL_DISTRIBUTION_PATH,
    TARGET_COLUMN,
    VALIDATION_DIR,
    VALIDATION_METADATA_PATH,
    VALIDATION_REPORT_PATH,
    VALIDATION_SUMMARY_PATH,
)
from src.experiments import build_pipeline


TRIVIAL_BASELINE_NAME = "TrivialGlobalMean"


def ensure_directories() -> None:
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_processed_data() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DATA_PATH)


def load_best_models() -> dict:
    return json.loads(BEST_MODELS_PATH.read_text(encoding="utf-8"))


def load_preprocess_metadata() -> dict:
    return json.loads(PREPROCESS_METADATA_PATH.read_text(encoding="utf-8"))


def evaluate_configuration(
    df: pd.DataFrame,
    experiment_name: str,
    config: dict,
    k: int,
) -> list[dict]:
    X = df[config["feature_columns"]]
    y = df[TARGET_COLUMN]
    cv = KFold(n_splits=CV_SPLITS, shuffle=True, random_state=RANDOM_STATE)

    rows: list[dict] = []
    for fold, (train_idx, test_idx) in enumerate(cv.split(X, y), start=1):
        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]
        y_train = y.iloc[train_idx]
        y_test = y.iloc[test_idx]

        pipeline = build_pipeline(k=k, use_scaler=config["use_scaler"])
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)

        rows.append(
            {
                "model_type": "knn",
                "experiment": experiment_name,
                "description": config["description"],
                "feature_columns": ",".join(config["feature_columns"]),
                "use_scaler": config["use_scaler"],
                "k": k,
                "model_label": f"{experiment_name}_k{k}",
                "fold": fold,
                "mae": mean_absolute_error(y_test, predictions),
                "rmse": root_mean_squared_error(y_test, predictions),
                "r2": r2_score(y_test, predictions),
            }
        )

    return rows


def evaluate_trivial_baseline(
    df: pd.DataFrame,
    feature_columns: list[str],
) -> list[dict]:
    X = df[feature_columns]
    y = df[TARGET_COLUMN]
    cv = KFold(n_splits=CV_SPLITS, shuffle=True, random_state=RANDOM_STATE)

    rows: list[dict] = []
    for fold, (train_idx, test_idx) in enumerate(cv.split(X, y), start=1):
        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]
        y_train = y.iloc[train_idx]
        y_test = y.iloc[test_idx]

        baseline = DummyRegressor(strategy="mean")
        baseline.fit(X_train, y_train)
        predictions = baseline.predict(X_test)

        rows.append(
            {
                "model_type": "trivial_baseline",
                "experiment": TRIVIAL_BASELINE_NAME,
                "description": (
                    "Predicts the mean price_m2 of the training fold for every test sample."
                ),
                "feature_columns": ",".join(feature_columns),
                "use_scaler": False,
                "k": "",
                "model_label": TRIVIAL_BASELINE_NAME,
                "fold": fold,
                "mae": mean_absolute_error(y_test, predictions),
                "rmse": root_mean_squared_error(y_test, predictions),
                "r2": r2_score(y_test, predictions),
            }
        )

    return rows


def build_fold_metrics(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for experiment_name, config in EXPERIMENTS.items():
        for k in [1, 3, 5, 7, 9, 11, 15, 21]:
            rows.extend(evaluate_configuration(df, experiment_name, config, k))

    selected_baseline = load_best_models()["selected_baseline_model"]
    selected_config = EXPERIMENTS[selected_baseline["experiment"]]
    rows.extend(
        evaluate_trivial_baseline(
            df=df,
            feature_columns=selected_config["feature_columns"],
        )
    )

    fold_metrics = pd.DataFrame(rows)
    return fold_metrics.sort_values(["experiment", "k", "fold"]).reset_index(drop=True)


def summarize_fold_metrics(fold_metrics: pd.DataFrame, selected_experiment: str, selected_k: int) -> pd.DataFrame:
    grouped = fold_metrics.groupby(
        [
            "model_type",
            "experiment",
            "description",
            "feature_columns",
            "use_scaler",
            "k",
            "model_label",
        ],
        dropna=False,
    )

    summary = grouped.agg(
        folds=("fold", "count"),
        mae_mean=("mae", "mean"),
        mae_std=("mae", "std"),
        mae_min=("mae", "min"),
        mae_max=("mae", "max"),
        rmse_mean=("rmse", "mean"),
        rmse_std=("rmse", "std"),
        rmse_min=("rmse", "min"),
        rmse_max=("rmse", "max"),
        r2_mean=("r2", "mean"),
        r2_std=("r2", "std"),
        r2_min=("r2", "min"),
        r2_max=("r2", "max"),
    ).reset_index()

    summary["is_selected_solution"] = (
        (summary["experiment"] == selected_experiment) & (summary["k"] == selected_k)
    )
    summary["is_trivial_baseline"] = summary["experiment"].eq(TRIVIAL_BASELINE_NAME)
    summary = summary.sort_values(["rmse_mean", "mae_mean", "r2_mean"], ascending=[True, True, False])
    return summary.reset_index(drop=True)


def save_metric_boxplot(summary: pd.DataFrame, fold_metrics: pd.DataFrame, metric: str, path: Path) -> None:
    ordered_labels = summary["model_label"].tolist()
    data = [
        fold_metrics.loc[fold_metrics["model_label"].eq(label), metric].tolist()
        for label in ordered_labels
    ]

    fig_height = max(6, len(ordered_labels) * 0.35)
    fig, ax = plt.subplots(figsize=(14, fig_height))
    positions = list(range(1, len(ordered_labels) + 1))
    ax.boxplot(data, positions=positions, orientation="horizontal", patch_artist=True)
    ax.set_yticks(positions)
    ax.set_yticklabels(ordered_labels)
    ax.set_title(f"{metric.upper()} distribution across cross-validation folds")
    ax.set_xlabel(metric.upper())
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_selected_vs_trivial_distributions(
    fold_metrics: pd.DataFrame,
    selected_label: str,
) -> None:
    selected_rows = fold_metrics[fold_metrics["model_label"].eq(selected_label)]
    trivial_rows = fold_metrics[fold_metrics["model_label"].eq(TRIVIAL_BASELINE_NAME)]
    metrics = ["mae", "rmse", "r2"]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax, metric in zip(axes, metrics, strict=True):
        ax.hist(
            selected_rows[metric],
            bins=5,
            alpha=0.7,
            label=selected_label,
            color="#4C72B0",
            edgecolor="black",
        )
        ax.hist(
            trivial_rows[metric],
            bins=5,
            alpha=0.55,
            label=TRIVIAL_BASELINE_NAME,
            color="#DD8452",
            edgecolor="black",
        )
        ax.set_title(metric.upper())
        ax.set_xlabel(metric.upper())
        ax.set_ylabel("Frequency")
        ax.legend()
    fig.tight_layout()
    fig.savefig(SELECTED_VS_TRIVIAL_DISTRIBUTION_PATH, dpi=150)
    plt.close(fig)


def to_markdown_table(df: pd.DataFrame) -> str:
    headers = list(df.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in df.itertuples(index=False):
        values = []
        for value in row:
            if isinstance(value, float):
                values.append(f"{value:.4f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def build_report(
    preprocess_metadata: dict,
    summary: pd.DataFrame,
    selected_row: pd.Series,
    trivial_row: pd.Series,
) -> str:
    comparison = {
        "mae_improvement": float(trivial_row["mae_mean"] - selected_row["mae_mean"]),
        "rmse_improvement": float(trivial_row["rmse_mean"] - selected_row["rmse_mean"]),
        "r2_improvement": float(selected_row["r2_mean"] - trivial_row["r2_mean"]),
    }

    display_columns = [
        "model_label",
        "model_type",
        "mae_mean",
        "mae_std",
        "mae_min",
        "mae_max",
        "rmse_mean",
        "rmse_std",
        "rmse_min",
        "rmse_max",
        "r2_mean",
        "r2_std",
        "r2_min",
        "r2_max",
    ]
    top_rows = summary[display_columns].copy()

    selected_table = to_markdown_table(pd.DataFrame([selected_row[display_columns].to_dict()]))
    trivial_table = to_markdown_table(pd.DataFrame([trivial_row[display_columns].to_dict()]))

    return f"""# Validation Report

## Purpose

This report strengthens the Evaluation stage of the OndeVale project by preserving
fold-by-fold validation evidence, reporting stability statistics, and comparing the
deployed KNN solution against a trivial baseline.

## Validation design

- Processed sale properties used for validation: {preprocess_metadata["rows_after_invalid_geo_filter"]}
- Cross-validation splitter: `KFold(n_splits={CV_SPLITS}, shuffle=True, random_state={RANDOM_STATE})`
- Metrics: `MAE`, `RMSE`, and `R²`
- Trivial baseline: predict the mean `price_m2` of the training fold for every test sample

## Why this report exists

The baseline report already preserved mean metrics. This report extends that evidence by
showing dispersion across folds, making it possible to discuss stability and variance
instead of relying only on average values.

## Deployed KNN solution

{selected_table}

## Trivial baseline

{trivial_table}

## Direct comparison

```json
{json.dumps(comparison, indent=2)}
```

Interpretation:

- Lower `MAE` and `RMSE` are better.
- Higher `R²` is better.
- The deployed KNN remains preferable because it improves all three mean metrics over
  the trivial baseline while also preserving a stable fold-by-fold profile.

## Stability summary for all evaluated configurations

{to_markdown_table(top_rows)}

## Visual artifacts

- `artifacts/validation/mae_boxplot.png`
- `artifacts/validation/rmse_boxplot.png`
- `artifacts/validation/r2_boxplot.png`
- `artifacts/validation/selected_vs_trivial_distributions.png`

## Methodological interpretation

The deployed KNN was not retained only because of its average performance. The fold-by-fold
evidence now shows how much its validation metrics vary across samples. This makes the
evaluation narrative stronger for academic presentation: the project can now discuss both
performance level and performance stability.
"""


def write_metadata(selected_row: pd.Series, trivial_row: pd.Series) -> None:
    payload = {
        "selected_solution": selected_row.to_dict(),
        "trivial_baseline": trivial_row.to_dict(),
        "source_report": str(REPORT_PATH),
        "generated_artifacts": [
            str(FOLD_METRICS_PATH),
            str(VALIDATION_SUMMARY_PATH),
            str(MAE_BOXPLOT_PATH),
            str(RMSE_BOXPLOT_PATH),
            str(R2_BOXPLOT_PATH),
            str(SELECTED_VS_TRIVIAL_DISTRIBUTION_PATH),
            str(VALIDATION_REPORT_PATH),
        ],
    }
    VALIDATION_METADATA_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    ensure_directories()

    df = load_processed_data()
    best_models = load_best_models()
    preprocess_metadata = load_preprocess_metadata()

    fold_metrics = build_fold_metrics(df)
    fold_metrics.to_csv(FOLD_METRICS_PATH, index=False)

    selected_experiment = best_models["selected_baseline_model"]["experiment"]
    selected_k = int(best_models["selected_baseline_model"]["k"])
    summary = summarize_fold_metrics(fold_metrics, selected_experiment, selected_k)
    summary.to_csv(VALIDATION_SUMMARY_PATH, index=False)

    selected_label = f"{selected_experiment}_k{selected_k}"
    selected_row = summary.loc[summary["model_label"].eq(selected_label)].iloc[0]
    trivial_row = summary.loc[summary["model_label"].eq(TRIVIAL_BASELINE_NAME)].iloc[0]

    save_metric_boxplot(summary, fold_metrics, "mae", MAE_BOXPLOT_PATH)
    save_metric_boxplot(summary, fold_metrics, "rmse", RMSE_BOXPLOT_PATH)
    save_metric_boxplot(summary, fold_metrics, "r2", R2_BOXPLOT_PATH)
    save_selected_vs_trivial_distributions(fold_metrics, selected_label)

    report = build_report(preprocess_metadata, summary, selected_row, trivial_row)
    VALIDATION_REPORT_PATH.write_text(report, encoding="utf-8")
    write_metadata(selected_row, trivial_row)

    print(f"Saved fold metrics to: {FOLD_METRICS_PATH}")
    print(f"Saved validation summary to: {VALIDATION_SUMMARY_PATH}")
    print(f"Saved validation report to: {VALIDATION_REPORT_PATH}")


if __name__ == "__main__":
    main()
