import json

import pandas as pd
from pyproj import Transformer

from src.config import (
    PREPROCESS_METADATA_PATH,
    PROCESSED_DATA_PATH,
    PROCESSED_DIR,
    RAW_DATA_PATH,
    REQUIRED_COLUMNS,
    SCOPE_COLUMN,
    SCOPE_VALUE,
    SOURCE_CRS,
    TARGET_COLUMN,
    TARGET_CRS,
)


def ensure_directories() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    return pd.read_csv(RAW_DATA_PATH)


def filter_scope(df: pd.DataFrame) -> pd.DataFrame:
    return df[df[SCOPE_COLUMN].eq(SCOPE_VALUE)].copy()


def drop_missing_required(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(subset=REQUIRED_COLUMNS).copy()


def drop_invalid_geography(df: pd.DataFrame) -> pd.DataFrame:
    return df[(df["Latitude"] != 0) & (df["Longitude"] != 0)].copy()


def build_target(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[TARGET_COLUMN] = df["Price"] / df["Size"]
    return df


def project_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    transformer = Transformer.from_crs(SOURCE_CRS, TARGET_CRS, always_xy=True)
    x, y = transformer.transform(df["Longitude"].to_numpy(), df["Latitude"].to_numpy())
    df["x"] = x
    df["y"] = y
    return df


def main() -> None:
    ensure_directories()

    raw_df = load_data()
    scoped_df = filter_scope(raw_df)
    non_missing_df = drop_missing_required(scoped_df)
    valid_geo_df = drop_invalid_geography(non_missing_df)
    processed_df = project_coordinates(build_target(valid_geo_df))

    processed_df.to_csv(PROCESSED_DATA_PATH, index=False)

    metadata = {
        "raw_rows": int(len(raw_df)),
        "scope_rows": int(len(scoped_df)),
        "rows_after_missing_filter": int(len(non_missing_df)),
        "rows_after_invalid_geo_filter": int(len(valid_geo_df)),
        "removed_missing_required": int(len(scoped_df) - len(non_missing_df)),
        "removed_invalid_zero_coordinates": int(len(non_missing_df) - len(valid_geo_df)),
        "scope_decision": f"{SCOPE_COLUMN} == '{SCOPE_VALUE}'",
        "required_columns": REQUIRED_COLUMNS,
        "target_column": TARGET_COLUMN,
        "source_crs": SOURCE_CRS,
        "target_crs": TARGET_CRS,
    }

    PREPROCESS_METADATA_PATH.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print(f"Saved processed data to: {PROCESSED_DATA_PATH}")
    print(f"Saved preprocessing metadata to: {PREPROCESS_METADATA_PATH}")


if __name__ == "__main__":
    main()
