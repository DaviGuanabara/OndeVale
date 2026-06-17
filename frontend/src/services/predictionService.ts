export interface PredictionRequest {
  latitude: number;
  longitude: number;
}

export interface PredictionResponse {
  latitude: number;
  longitude: number;
  price_m2: number;
  currency: "BRL";
}

export interface DomainResponse {
  name: string;
  latitude_min: number;
  latitude_max: number;
  longitude_min: number;
  longitude_max: number;
}

function normalizeBaseUrl(rawBaseUrl?: string): string {
  if (!rawBaseUrl) {
    return "http://127.0.0.1:8000";
  }

  if (rawBaseUrl.startsWith("http://") || rawBaseUrl.startsWith("https://")) {
    return rawBaseUrl.replace(/\/$/, "");
  }

  return `https://${rawBaseUrl.replace(/\/$/, "")}`;
}

const API_BASE_URL = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL);

export async function requestPrediction(
  payload: PredictionRequest,
): Promise<PredictionResponse> {
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let message = "Prediction request failed.";

    try {
      const errorPayload = (await response.json()) as { detail?: unknown };
      if (typeof errorPayload.detail === "string") {
        message = errorPayload.detail;
      }
    } catch {
      // Fallback to the generic message when the response body is not JSON.
    }

    throw new Error(message);
  }

  return (await response.json()) as PredictionResponse;
}

export async function requestDomain(): Promise<DomainResponse> {
  const response = await fetch(`${API_BASE_URL}/domain`);

  if (!response.ok) {
    throw new Error("Failed to load the model validity domain.");
  }

  return (await response.json()) as DomainResponse;
}
