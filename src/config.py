from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT_DIR / "dataset" / "DatasetSaoPaulo.csv"

ARTIFACTS_DIR = ROOT_DIR / "artifacts"
STATS_DIR = ARTIFACTS_DIR / "stats"
PROCESSED_DIR = ARTIFACTS_DIR / "data"
EXPERIMENTS_DIR = ARTIFACTS_DIR / "experiments"
MODELS_DIR = ARTIFACTS_DIR / "models"
REPORTS_DIR = ARTIFACTS_DIR / "reports"

DATASET_SUMMARY_PATH = STATS_DIR / "dataset_summary.json"
MISSING_VALUES_PATH = STATS_DIR / "missing_values.csv"
NEGOTIATION_TYPE_DISTRIBUTION_PATH = STATS_DIR / "negotiation_type_distribution.csv"
SALE_SUMMARY_PATH = STATS_DIR / "sale_summary.json"
PRICE_M2_SUMMARY_PATH = STATS_DIR / "price_m2_summary.json"
DATA_QUALITY_REPORT_PATH = STATS_DIR / "data_quality_report.json"
STATS_REPORT_PATH = STATS_DIR / "stats_report.md"
PRICE_HISTOGRAM_PATH = STATS_DIR / "price_histogram.png"
SIZE_HISTOGRAM_PATH = STATS_DIR / "size_histogram.png"
PRICE_M2_HISTOGRAM_PATH = STATS_DIR / "price_m2_histogram.png"
PRICE_M2_BOXPLOT_PATH = STATS_DIR / "price_m2_boxplot.png"
GEOGRAPHIC_DISTRIBUTION_PATH = STATS_DIR / "geographic_distribution.png"
SALE_GEOGRAPHIC_DISTRIBUTION_PATH = STATS_DIR / "sale_geographic_distribution.png"

PROCESSED_DATA_PATH = PROCESSED_DIR / "sales_price_m2_geographic_baseline.csv"
PREPROCESS_METADATA_PATH = PROCESSED_DIR / "preprocess_metadata.json"
DOMAIN_PATH = PROCESSED_DIR / "domain.json"
DOMAIN_GEOJSON_PATH = PROCESSED_DIR / "domain.geojson"
EXPERIMENT_RESULTS_PATH = EXPERIMENTS_DIR / "knn_cv_results.csv"
BEST_MODELS_PATH = EXPERIMENTS_DIR / "best_models.json"
MODEL_PATH = MODELS_DIR / "knn_price_m2_baseline.joblib"
MODEL_METADATA_PATH = MODELS_DIR / "knn_price_m2_baseline.json"
REPORT_PATH = REPORTS_DIR / "baseline_report.md"

REQUIRED_COLUMNS = ["Price", "Size", "Latitude", "Longitude"]
TARGET_COLUMN = "price_m2"
METRIC_COLUMNS = ["x", "y"]
RAW_COORD_COLUMNS = ["Longitude", "Latitude"]

SCOPE_COLUMN = "Negotiation Type"
SCOPE_VALUE = "sale"

SOURCE_CRS = "EPSG:4326"
TARGET_CRS = "EPSG:31983"  # SIRGAS 2000 / UTM zone 23S, appropriate for Sao Paulo

K_GRID = [1, 3, 5, 7, 9, 11, 15, 21]
CV_SPLITS = 5
RANDOM_STATE = 42

EXPERIMENTS = {
    "A_raw_no_norm": {
        "feature_columns": RAW_COORD_COLUMNS,
        "use_scaler": False,
        "description": "Raw longitude/latitude in degrees without normalization.",
    },
    "B_metric_no_norm": {
        "feature_columns": METRIC_COLUMNS,
        "use_scaler": False,
        "description": "Projected metric coordinates without normalization.",
    },
    "C_metric_std": {
        "feature_columns": METRIC_COLUMNS,
        "use_scaler": True,
        "description": "Projected metric coordinates with StandardScaler.",
    },
}
