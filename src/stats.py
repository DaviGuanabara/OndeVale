import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from src.config import (
    DATA_QUALITY_REPORT_PATH,
    DATASET_SUMMARY_PATH,
    GEOGRAPHIC_DISTRIBUTION_PATH,
    MISSING_VALUES_PATH,
    NEGOTIATION_TYPE_DISTRIBUTION_PATH,
    PRICE_HISTOGRAM_PATH,
    PRICE_M2_BOXPLOT_PATH,
    PRICE_M2_HISTOGRAM_PATH,
    PRICE_M2_SUMMARY_PATH,
    RAW_DATA_PATH,
    SALE_GEOGRAPHIC_DISTRIBUTION_PATH,
    SALE_SUMMARY_PATH,
    SIZE_HISTOGRAM_PATH,
    SCOPE_COLUMN,
    SCOPE_VALUE,
    STATS_DIR,
    STATS_REPORT_PATH,
    TARGET_COLUMN,
)


def ensure_directories() -> None:
    STATS_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    return pd.read_csv(RAW_DATA_PATH)


def get_sale_subset(df: pd.DataFrame) -> pd.DataFrame:
    sale_df = df[df[SCOPE_COLUMN].eq(SCOPE_VALUE)].copy()
    sale_df[TARGET_COLUMN] = sale_df["Price"] / sale_df["Size"]
    return sale_df


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def dataset_summary(df: pd.DataFrame) -> dict:
    return {
        "num_rows": int(df.shape[0]),
        "num_columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "dtypes": {column: str(dtype) for column, dtype in df.dtypes.items()},
    }


def missing_values_summary(df: pd.DataFrame) -> pd.DataFrame:
    missing = df.isna().sum()
    result = pd.DataFrame(
        {
            "column": df.columns,
            "missing_count": [int(missing[column]) for column in df.columns],
            "missing_percentage": [
                float((missing[column] / len(df)) * 100) if len(df) else 0.0
                for column in df.columns
            ],
        }
    )
    return result


def negotiation_type_distribution(df: pd.DataFrame) -> pd.DataFrame:
    counts = df[SCOPE_COLUMN].value_counts(dropna=False)
    percentages = df[SCOPE_COLUMN].value_counts(dropna=False, normalize=True) * 100
    return pd.DataFrame(
        {
            SCOPE_COLUMN: counts.index.astype(str),
            "count": counts.astype(int).to_list(),
            "percentage": percentages.astype(float).to_list(),
        }
    )


def summary_stats(series: pd.Series) -> dict:
    return {
        "count": int(series.count()),
        "mean": float(series.mean()),
        "std": float(series.std()),
        "min": float(series.min()),
        "25%": float(series.quantile(0.25)),
        "50%": float(series.quantile(0.50)),
        "75%": float(series.quantile(0.75)),
        "max": float(series.max()),
    }


def sale_summary(sale_df: pd.DataFrame) -> dict:
    return {
        "row_count": int(len(sale_df)),
        "price": summary_stats(sale_df["Price"]),
        "size": summary_stats(sale_df["Size"]),
        "latitude": summary_stats(sale_df["Latitude"]),
        "longitude": summary_stats(sale_df["Longitude"]),
    }


def price_m2_summary(sale_df: pd.DataFrame) -> dict:
    series = sale_df[TARGET_COLUMN]
    return {
        "count": int(series.count()),
        "mean": float(series.mean()),
        "median": float(series.median()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max()),
        "percentiles": {
            "1%": float(series.quantile(0.01)),
            "5%": float(series.quantile(0.05)),
            "25%": float(series.quantile(0.25)),
            "50%": float(series.quantile(0.50)),
            "75%": float(series.quantile(0.75)),
            "95%": float(series.quantile(0.95)),
            "99%": float(series.quantile(0.99)),
        },
    }


def data_quality_report(df: pd.DataFrame) -> dict:
    zero_coords = ((df["Latitude"] == 0) & (df["Longitude"] == 0)).sum()
    return {
        "coordinates_equal_to_0_0": int(zero_coords),
        "negative_prices": int((df["Price"] < 0).sum()),
        "zero_prices": int((df["Price"] == 0).sum()),
        "negative_sizes": int((df["Size"] < 0).sum()),
        "zero_sizes": int((df["Size"] == 0).sum()),
        "duplicated_rows": int(df.duplicated().sum()),
    }


def save_histogram(
    series: pd.Series,
    path: Path,
    title: str,
    xlabel: str,
    bins: int = 30,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(series.dropna(), bins=bins, color="#4C72B0", edgecolor="black", alpha=0.85)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_boxplot(series: pd.Series, path: Path, title: str, ylabel: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.boxplot(
        series.dropna(),
        orientation="vertical",
        patch_artist=True,
        boxprops={"facecolor": "#55A868"},
    )
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_scatter(
    df: pd.DataFrame,
    path: Path,
    title: str,
    alpha: float,
    marker_size: float,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(
        df["Longitude"],
        df["Latitude"],
        s=marker_size,
        alpha=alpha,
        c="#C44E52",
        edgecolors="none",
    )
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
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


def build_stats_report(
    dataset_info: dict,
    missing_df: pd.DataFrame,
    negotiation_df: pd.DataFrame,
    sale_info: dict,
    price_m2_info: dict,
    quality_info: dict,
) -> str:
    return f"""# Dataset Characterization Report

## Dataset overview

- Rows: {dataset_info["num_rows"]}
- Columns: {dataset_info["num_columns"]}
- Column names: {", ".join(dataset_info["column_names"])}

### Data types

```json
{json.dumps(dataset_info["dtypes"], indent=2)}
```

## Missing values summary

{to_markdown_table(missing_df)}

## Negotiation type summary

{to_markdown_table(negotiation_df)}

## Sale subset summary

```json
{json.dumps(sale_info, indent=2)}
```

## price_m2 summary

```json
{json.dumps(price_m2_info, indent=2)}
```

## Data quality findings

```json
{json.dumps(quality_info, indent=2)}
```

## Visualizations

### Price histogram

![Price histogram](price_histogram.png)

### Size histogram

![Size histogram](size_histogram.png)

### Price per square meter histogram

![Price per square meter histogram](price_m2_histogram.png)

### Price per square meter boxplot

![Price per square meter boxplot](price_m2_boxplot.png)

### Geographic distribution

![Geographic distribution](geographic_distribution.png)

### Sale-only geographic distribution

![Sale-only geographic distribution](sale_geographic_distribution.png)
"""


def main() -> None:
    ensure_directories()

    df = load_data()
    sale_df = get_sale_subset(df)

    dataset_info = dataset_summary(df)
    missing_df = missing_values_summary(df)
    negotiation_df = negotiation_type_distribution(df)
    sale_info = sale_summary(sale_df)
    price_m2_info = price_m2_summary(sale_df)
    quality_info = data_quality_report(df)

    write_json(DATASET_SUMMARY_PATH, dataset_info)
    missing_df.to_csv(MISSING_VALUES_PATH, index=False)
    negotiation_df.to_csv(NEGOTIATION_TYPE_DISTRIBUTION_PATH, index=False)
    write_json(SALE_SUMMARY_PATH, sale_info)
    write_json(PRICE_M2_SUMMARY_PATH, price_m2_info)
    write_json(DATA_QUALITY_REPORT_PATH, quality_info)

    save_histogram(df["Price"], PRICE_HISTOGRAM_PATH, "Price Distribution", "Price")
    save_histogram(df["Size"], SIZE_HISTOGRAM_PATH, "Size Distribution", "Size")
    save_histogram(
        sale_df[TARGET_COLUMN],
        PRICE_M2_HISTOGRAM_PATH,
        "Price per Square Meter Distribution (Sale Properties)",
        "price_m2",
    )
    save_boxplot(
        sale_df[TARGET_COLUMN],
        PRICE_M2_BOXPLOT_PATH,
        "Price per Square Meter Boxplot (Sale Properties)",
        "price_m2",
    )
    save_scatter(
        df,
        GEOGRAPHIC_DISTRIBUTION_PATH,
        "Geographic Distribution of All Properties",
        alpha=0.35,
        marker_size=12,
    )
    save_scatter(
        sale_df,
        SALE_GEOGRAPHIC_DISTRIBUTION_PATH,
        "Geographic Distribution of Sale Properties",
        alpha=0.45,
        marker_size=14,
    )

    report = build_stats_report(
        dataset_info=dataset_info,
        missing_df=missing_df,
        negotiation_df=negotiation_df,
        sale_info=sale_info,
        price_m2_info=price_m2_info,
        quality_info=quality_info,
    )
    STATS_REPORT_PATH.write_text(report, encoding="utf-8")

    print(f"Saved dataset summary to: {DATASET_SUMMARY_PATH}")
    print(f"Saved missing values summary to: {MISSING_VALUES_PATH}")
    print(f"Saved negotiation type distribution to: {NEGOTIATION_TYPE_DISTRIBUTION_PATH}")
    print(f"Saved sale summary to: {SALE_SUMMARY_PATH}")
    print(f"Saved price_m2 summary to: {PRICE_M2_SUMMARY_PATH}")
    print(f"Saved data quality report to: {DATA_QUALITY_REPORT_PATH}")
    print(f"Saved stats report to: {STATS_REPORT_PATH}")


if __name__ == "__main__":
    main()
