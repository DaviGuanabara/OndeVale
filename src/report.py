import json

import pandas as pd

from src.config import (
    BEST_MODELS_PATH,
    EXPERIMENT_RESULTS_PATH,
    PREPROCESS_METADATA_PATH,
    REPORT_PATH,
    REPORTS_DIR,
)


def ensure_directories() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


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


def main() -> None:
    ensure_directories()

    preprocess = json.loads(PREPROCESS_METADATA_PATH.read_text(encoding="utf-8"))
    best_models = json.loads(BEST_MODELS_PATH.read_text(encoding="utf-8"))
    results = pd.read_csv(EXPERIMENT_RESULTS_PATH)

    report = f"""# Geographic KNN Baseline Report

## Dataset handling
- Raw rows: {preprocess["raw_rows"]}
- Sale rows after scope filtering: {preprocess["scope_rows"]}
- Rows after missing-value removal: {preprocess["rows_after_missing_filter"]}
- Rows after invalid-coordinate removal: {preprocess["rows_after_invalid_geo_filter"]}
- Removed invalid `(0, 0)` coordinates: {preprocess["removed_invalid_zero_coordinates"]}

## Validation results
{to_markdown_table(results)}

## Best overall experiment
{json.dumps(best_models["overall_best"], indent=2)}

## Selected baseline model
{json.dumps(best_models["selected_baseline_model"], indent=2)}

## Interpretation
Lower MAE and RMSE are better. Higher R² is better. The selected baseline model is constrained to metric coordinates `[x, y]`, so the final deployed baseline is chosen from experiments B and C even if experiment A wins the ablation.
"""

    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Saved report to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
