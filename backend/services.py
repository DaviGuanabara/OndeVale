import json
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from pyproj import Transformer

from src.config import DOMAIN_PATH, METRIC_COLUMNS, MODEL_PATH, SOURCE_CRS, TARGET_CRS


@lru_cache(maxsize=1)
def get_transformer() -> Transformer:
    return Transformer.from_crs(SOURCE_CRS, TARGET_CRS, always_xy=True)


@lru_cache(maxsize=1)
def get_model():
    return joblib.load(MODEL_PATH)


@lru_cache(maxsize=1)
def get_domain() -> dict:
    if not Path(DOMAIN_PATH).exists():
        raise RuntimeError("Domain artifact missing. Ensure artifacts/data/domain.json exists.")
    return json.loads(DOMAIN_PATH.read_text(encoding="utf-8"))


def load_inference_assets() -> None:
    get_transformer()
    get_model()
    get_domain()


def point_is_within_domain(latitude: float, longitude: float) -> bool:
    domain = get_domain()
    return (
        domain["latitude_min"] <= latitude <= domain["latitude_max"]
        and domain["longitude_min"] <= longitude <= domain["longitude_max"]
    )


def get_domain_response() -> dict:
    domain = get_domain()
    return domain


def project_coordinates(latitude: float, longitude: float) -> tuple[float, float]:
    transformer = get_transformer()
    x, y = transformer.transform(longitude, latitude)
    return float(x), float(y)


def predict_price_m2(latitude: float, longitude: float) -> float:
    model = get_model()
    x, y = project_coordinates(latitude=latitude, longitude=longitude)
    features = pd.DataFrame([[x, y]], columns=METRIC_COLUMNS)
    prediction = model.predict(features)[0]
    return round(float(prediction), 2)
