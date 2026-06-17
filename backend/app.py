import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import DomainResponse, HealthResponse, PredictRequest, PredictResponse
from backend.services import (
    get_domain_response,
    load_inference_assets,
    point_is_within_domain,
    predict_price_m2,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_inference_assets()
    yield


def get_cors_origins() -> list[str]:
    raw_origins = os.getenv("ONDEVALE_CORS_ORIGINS", "*").strip()
    if raw_origins == "*":
        return ["*"]
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


app = FastAPI(
    title="OndeVale API",
    description="FastAPI service for geographic KNN price per square meter prediction.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="OndeVale API")


@app.get("/domain", response_model=DomainResponse)
def domain() -> DomainResponse:
    return DomainResponse(**get_domain_response())


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    if not point_is_within_domain(
        latitude=request.latitude,
        longitude=request.longitude,
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "Selected point is outside the model validity domain. "
                "KNN predictions are restricted to the training geographic bounds."
            ),
        )

    price_m2 = predict_price_m2(
        latitude=request.latitude,
        longitude=request.longitude,
    )
    return PredictResponse(
        latitude=request.latitude,
        longitude=request.longitude,
        price_m2=price_m2,
        currency="BRL",
    )
