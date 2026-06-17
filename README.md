<p align="center">
  <img src="logos/ita-logo.svg" height="120" alt="ITA">
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="logos/Logotipo_UNIFESP.png" height="120" alt="UNIFESP">
</p>

<h1 align="center">OndeVale</h1>

<p align="center">
  Geographic Estimation of Real Estate Price per Square Meter in São Paulo
</p>

<p align="center">
  A Data Science Case Study developed for the course<br>
  <b>PO-235 – Data Science Project</b><br>
  Graduate Program in Operations Research (PG/PO)<br>
  Instituto Tecnológico de Aeronáutica (ITA) and Universidade Federal de São Paulo (UNIFESP)
</p>

OndeVale is a web application that estimates the **price per square meter** of real estate in São Paulo using **only geographic location**.

This repository is a Data Science course project. Its purpose is twofold:

- build a working end-to-end predictive system
- justify the methodological and architectural decisions behind that system

## Academic Context

OndeVale was developed as a case study for the course **PO-235 – Data Science Project**, offered by the **Graduate Program in Operations Research (PG/PO)**, a joint program between the **Instituto Tecnológico de Aeronáutica (ITA)** and the **Universidade Federal de São Paulo (UNIFESP)**.

The course is taught by **Prof. Dr. Filipe A. N. Verri** and focuses on the complete lifecycle of a Data Science project, including:

- Data collection
- Data characterization
- Data handling
- Inductive learning
- Validation
- Documentation
- Deployment

Following the methodology proposed in:

> Verri, F. A. N. (2026). *Data Science Project: An Inductive Learning Approach*. DOI: 10.5281/zenodo.14498010.

this project was developed as an end-to-end Data Science product, transforming a trained machine learning model into a publicly accessible web application.

## Project Goal

The objective of OndeVale is to investigate how much information about real estate value can be extracted exclusively from geographic location.

The project estimates the price per square meter of residential properties in São Paulo using a K-Nearest Neighbors (KNN) model trained only on spatial coordinates.

Beyond predictive performance, the project emphasizes:

- methodological reproducibility
- explicit model validation
- model validity domain definition
- deployment of a usable Data Science product

The final result is an interactive web application that allows users to click on a map and obtain a real-time estimate of property value per square meter.

### Course Deliverables Alignment

The project was designed to satisfy the case study requirements defined in PO-235:

```text
Data collection
↓
Data handling
↓
Inductive learning
↓
Validation
↓
Documentation
↓
Deployment
```

OndeVale explicitly implements all stages through a reproducible workflow, a trained machine learning model, a documented API, an interactive web interface, and a public deployment strategy.

## Project Flow

```text
Dataset
↓
Data characterization
↓
KNN training
↓
FastAPI inference service
↓
Interactive web map
↓
User prediction
```

The current user flow is:

```text
User
↓
Map Click
↓
API Call
↓
KNN Prediction
↓
Visual Feedback
```

## Architecture

OndeVale uses a layered architecture that keeps the Data Science workflow, inference service, and user interface separated.

```text
Dataset
↓
KNN
↓
FastAPI
↓
Vue
↓
Render
```

### Dataset Layer

The raw data is stored in `dataset/DatasetSaoPaulo.csv`. The project first characterizes the dataset, inspects missing values and data quality, and defines the supervised regression scope.

### Modeling Layer

The baseline model is a **KNeighborsRegressor** trained only with projected metric coordinates:

- source CRS: `EPSG:4326`
- target CRS: `EPSG:31983`
- features: `x`, `y`
- target: `price_m2`

Because KNN is distance-based, coordinate projection is part of the model definition.

### API Layer

The FastAPI backend receives latitude and longitude, projects them using the same transformation used during training, checks the model validity domain, loads the trained model artifact, and returns a prediction when the point is valid.

### Frontend Layer

The Vue frontend presents a full-screen interactive map and a floating panel. The user clicks on the map, the frontend requests a prediction, and the UI shows coordinates, domain validity, and estimated BRL/m².

### Static Domain Layer

A fixed São Paulo municipality domain is stored as a static resource and is used by both the backend and the frontend for geographic validation.

### Deployment Layer

Render is used to publish both the backend and the frontend. The objective is that a professor can open a public URL and test the system without installing any local dependencies.

## Technology Choices

### Python

Python was selected because the analytical pipeline, model training, and backend inference service can remain in the same ecosystem. This reduces conceptual fragmentation and keeps the project easier to explain.

### scikit-learn

scikit-learn is appropriate because the project baseline uses classical supervised learning, not deep learning. It provides a stable and transparent implementation of KNN, which is ideal for a reproducible course project.

### FastAPI

FastAPI was chosen for the backend because it is lightweight, typed, and generates documentation automatically. That makes it useful both for implementation and for demonstrating the API contract clearly.

### Vue 3

Vue 3 was selected because it is lightweight, maintainable, and simpler than React for this project. The frontend is small, focused, and stateful, which fits Vue very well.

### TypeScript

TypeScript was chosen to make the frontend-service boundary safer. Since the application exchanges structured geographic data and prediction payloads, explicit types reduce accidental integration errors.

### Pinia

Pinia is the official state management library for Vue and is sufficient for the current complexity. It keeps state centralized without introducing unnecessary architectural overhead.

### MapLibre GL JS

MapLibre was selected because it is closer to professional GIS applications than Leaflet. It provides a modern geospatial user experience and matches the project goal of building a location-driven analytical interface.

### Carto Positron

Carto Positron was selected as the basemap because it is clean, minimalistic, and GIS-oriented. It provides geographic context without visually competing with the prediction panel.

### Render

Render was selected because it provides a straightforward deployment path for both a Python web service and a static frontend. This is especially useful in a course setting where public access matters.

### uv

`uv` was chosen for Python dependency and environment management because it is fast, reproducible, and simple to integrate into development and deployment workflows.

## Frontend Architecture

The intended frontend architecture is:

```text
frontend/src/
├── views/
│   └── HomeView.vue
├── components/
│   ├── MapView.vue
│   └── PredictionPanel.vue
├── services/
│   └── predictionService.ts
├── stores/
│   └── predictionStore.ts
```

### `HomeView.vue`

Composes the main screen by combining the map and the floating prediction panel.

### `MapView.vue`

Initializes MapLibre, renders the Carto Positron basemap, draws the model validity rectangle and outside-area mask, handles map clicks, and positions the marker.

### `PredictionPanel.vue`

Displays:

- latitude
- longitude
- model validity status
- predicted BRL/m²
- loading and error states

### `predictionService.ts`

Encapsulates HTTP communication with the backend:

- `GET /domain`
- `POST /predict`

### `predictionStore.ts`

Stores the frontend state:

- `selectedLatitude`
- `selectedLongitude`
- `predictedPriceM2`
- `loading`
- `error`
- `domain`
- `insideDomain`

## Backend Architecture

The backend is intentionally simple:

```text
backend/
├── app.py
├── schemas.py
└── services.py
```

- `app.py` defines routes, CORS, and API wiring
- `schemas.py` defines request/response models
- `services.py` handles projection, model loading, domain loading, and inference

The model and domain are loaded once and reused across requests.

## Machine Learning Workflow

The project follows the methodological spirit of the Data Science course:

1. Problem definition
2. Dataset characterization
3. Data handling
4. Learning
5. Validation
6. Experimental comparison
7. Delivery through API and frontend

This order is important. The application layer was built only after the data and the baseline model had already been studied and validated.

## API Endpoints

### Health Check

`GET /`

```json
{
  "status": "ok",
  "service": "OndeVale API"
}
```

### Model Validity Domain

`GET /domain`

Returns the fixed operational domain of the application:

```json
{
  "name": "Municipality of São Paulo",
  "latitude_min": -24.05,
  "latitude_max": -23.30,
  "longitude_min": -46.95,
  "longitude_max": -46.20
}
```

### Prediction

`POST /predict`

Request:

```json
{
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

Response:

```json
{
  "latitude": -23.5505,
  "longitude": -46.6333,
  "price_m2": 8185.1,
  "currency": "BRL"
}
```

FastAPI documentation is available at:

- `/docs`
- `/redoc`

## Model Validity Domain

KNN is a local, distance-based model. That means it should not be trusted outside the operational region for which the application is defined.

### Why extrapolation is dangerous

When a model receives a point outside the training distribution, it is forced to respond using neighborhoods that were never intended to represent that region. In KNN, this problem is especially important because the prediction is based directly on nearby examples. If the point is too far from the observed space, the idea of “nearby” becomes methodologically weak.

### Why KNN should not predict outside the valid operational area

KNN does not learn a global parametric equation for the whole city. It learns a local similarity rule over observed properties. Outside the adopted municipal validity region, the prediction becomes an extrapolation disguised as interpolation, which can mislead the user.

## Validity Domain

The dataset explicitly represents properties located in the municipality of São Paulo.

Therefore, OndeVale adopts a fixed operational domain corresponding to the municipality of São Paulo.

This decision prevents coordinate errors and geographic outliers from affecting the application scope and guarantees consistency between the dataset definition and the deployed system.

The domain is intentionally fixed and is not inferred from the training dataset.

The static artifacts are:

`artifacts/data/domain.json`

`artifacts/data/domain.geojson`

### How the UI communicates validity

The frontend requests `GET /domain` at startup and then:

- draws the valid rectangle on the map
- draws a mask over the outside area
- marks the current selection as `Inside Domain` or `Outside Domain`
- disables predictions for points outside the valid area

This makes the model limitation explicit instead of silently returning unreliable results.

The backend also depends on `domain.json` and validates prediction requests against it. If the artifact is missing, the backend fails explicitly at startup.

## Local Execution

### Backend

```bash
uv sync
uv run python -m src.preprocess
uv run uvicorn backend.app:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

By default, the frontend expects the backend at:

```text
http://127.0.0.1:8000
```

The Vite development server usually runs at:

```text
http://127.0.0.1:5173
```

## Vite Cache Cleanup

If Vite reports stale optimized dependency errors or missing component errors, clean the frontend cache and reinstall dependencies:

```bash
cd frontend
rm -rf node_modules
rm -rf .vite
rm -rf node_modules/.vite
npm install
npm run dev
```

## Deployment Strategy

The deployment strategy is:

```text
GitHub
↓
Render
↓
Public URL
```

### Why this matters

The goal is that a professor can open a public URL, click on the map, and interact with the system without installing anything locally.

### Render Blueprint

The repository contains a `render.yaml` blueprint that defines:

- a Python web service for FastAPI
- a static site for the Vue frontend

The frontend receives the backend host through `VITE_API_BASE_URL` during deployment.

## Render Deployment

OndeVale can be deployed on Render from a single Blueprint without creating services manually.

1. Push the repository to GitHub.
2. Log in to Render.
3. Click `New` and choose `Blueprint`.
4. Select the repository that contains OndeVale.
5. Review the detected `render.yaml` and apply the Blueprint.
6. Wait for Render to build both services.
7. Open the public `ondevale-frontend` URL and interact with the application.

### Blueprint Services

The Blueprint creates exactly two services:

- `ondevale-api`
- `ondevale-frontend`

### Deployment Notes

- `ondevale-api` is a Python web service that installs dependencies with `uv`, starts `uvicorn`, exposes `GET /` for health checks, and loads model artifacts directly from the repository.
- `ondevale-frontend` is a Render static site built from `frontend/` and published from `frontend/dist`.
- The frontend receives the backend host through `VITE_API_BASE_URL`, so the deployed UI points to the deployed API automatically.
- `ONDEVALE_CORS_ORIGINS` is configured in the backend service and can be tightened later if a stricter production origin policy is desired.

## Repository Structure

```text
OndeVale/
├── artifacts/
├── backend/
├── dataset/
├── frontend/
├── src/
├── Makefile
├── pyproject.toml
├── render.yaml
└── README.md
```

### `src/`

Contains the Data Science workflow:

- `stats.py`
- `preprocess.py`
- `experiments.py`
- `train.py`
- `report.py`

### `artifacts/`

Stores generated outputs:

- descriptive statistics
- processed data
- domain definition
- experiment results
- trained model
- reports

## Running the Data Science Pipeline

The full reproducible workflow is:

```bash
make stats
make preprocess
make experiments
make train
make report
```

The complete pipeline can also be executed with:

```bash
make all
```

This runs:

```text
stats
↓
preprocess
↓
experiments
↓
train
↓
report
```

## Final Perspective

OndeVale is a complete chain from dataset understanding to interactive prediction delivery. That end-to-end coherence is important in a Data Science course project because the final interface should reflect and respect the methodological constraints of the model behind it.



## Dataset

The dataset used in this project is:

São Paulo Real Estate Sale/Rent – April 2019

Source:
https://www.kaggle.com/datasets/argonalyst/sao-paulo-real-estate-sale-rent-april-2019
