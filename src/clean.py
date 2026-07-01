from pathlib import Path

from src.config import (
    DATASET_SUMMARY_PATH,
    DATA_QUALITY_REPORT_PATH,
    DOMAIN_GEOJSON_PATH,
    DOMAIN_PATH,
    EXPERIMENTS_DIR,
    FOLD_METRICS_PATH,
    GEOGRAPHIC_DISTRIBUTION_PATH,
    MAE_BOXPLOT_PATH,
    MISSING_VALUES_PATH,
    MODEL_METADATA_PATH,
    MODEL_PATH,
    NEGOTIATION_TYPE_DISTRIBUTION_PATH,
    PREPROCESS_METADATA_PATH,
    PRICE_HISTOGRAM_PATH,
    PRICE_M2_BOXPLOT_PATH,
    PRICE_M2_HISTOGRAM_PATH,
    PRICE_M2_SUMMARY_PATH,
    PROCESSED_DATA_PATH,
    REPORT_PATH,
    R2_BOXPLOT_PATH,
    RMSE_BOXPLOT_PATH,
    SALE_GEOGRAPHIC_DISTRIBUTION_PATH,
    SALE_SUMMARY_PATH,
    SIZE_HISTOGRAM_PATH,
    STATS_REPORT_PATH,
    SELECTED_VS_TRIVIAL_DISTRIBUTION_PATH,
    VALIDATION_DIR,
    VALIDATION_METADATA_PATH,
    VALIDATION_REPORT_PATH,
    VALIDATION_SUMMARY_PATH,
)

GENERATED_FILES = [
    DATASET_SUMMARY_PATH,
    DATA_QUALITY_REPORT_PATH,
    GEOGRAPHIC_DISTRIBUTION_PATH,
    MISSING_VALUES_PATH,
    NEGOTIATION_TYPE_DISTRIBUTION_PATH,
    PREPROCESS_METADATA_PATH,
    PRICE_HISTOGRAM_PATH,
    PRICE_M2_BOXPLOT_PATH,
    PRICE_M2_HISTOGRAM_PATH,
    PRICE_M2_SUMMARY_PATH,
    PROCESSED_DATA_PATH,
    REPORT_PATH,
    SALE_GEOGRAPHIC_DISTRIBUTION_PATH,
    SALE_SUMMARY_PATH,
    SIZE_HISTOGRAM_PATH,
    STATS_REPORT_PATH,
    MODEL_METADATA_PATH,
    MODEL_PATH,
    FOLD_METRICS_PATH,
    VALIDATION_METADATA_PATH,
    VALIDATION_SUMMARY_PATH,
    VALIDATION_REPORT_PATH,
    MAE_BOXPLOT_PATH,
    RMSE_BOXPLOT_PATH,
    R2_BOXPLOT_PATH,
    SELECTED_VS_TRIVIAL_DISTRIBUTION_PATH,
]

GENERATED_DIRS = [
    EXPERIMENTS_DIR,
    VALIDATION_DIR,
]

def main() -> None:
    removed_paths: list[Path] = []

    for file_path in GENERATED_FILES:
        if file_path.exists():
            file_path.unlink()
            removed_paths.append(file_path)

    for directory in GENERATED_DIRS:
        if directory.exists():
            for child in sorted(directory.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            directory.rmdir()
            removed_paths.append(directory)

    if removed_paths:
        print("Removed generated artifacts:")
        for path in removed_paths:
            print(path)
    else:
        print("No generated artifacts found to remove.")

    for static_path in [DOMAIN_PATH, DOMAIN_GEOJSON_PATH]:
        if static_path.exists():
            print(f"Preserved static domain artifact: {static_path}")


if __name__ == "__main__":
    main()
