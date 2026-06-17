from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class PredictRequest(BaseModel):
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude in geographic coordinates (EPSG:4326).",
        examples=[-23.5505],
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude in geographic coordinates (EPSG:4326).",
        examples=[-46.6333],
    )


class PredictResponse(BaseModel):
    latitude: float
    longitude: float
    price_m2: float
    currency: str


class DomainResponse(BaseModel):
    name: str
    latitude_min: float
    latitude_max: float
    longitude_min: float
    longitude_max: float
