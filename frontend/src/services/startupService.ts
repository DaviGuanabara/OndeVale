import type { DomainResponse } from "./predictionService";

export interface HealthResponse {
  status: string;
  service: string;
}

export type StartupStage = "health" | "domain";

export interface StartupProgress {
  stage: StartupStage;
}

export interface StartupResult {
  domain: DomainResponse;
  health: HealthResponse;
}

export class StartupError extends Error {
  stage: StartupStage | "timeout";

  constructor(message: string, stage: StartupStage | "timeout") {
    super(message);
    this.name = "StartupError";
    this.stage = stage;
  }
}

const DEFAULT_TIMEOUT_MS = 60_000;

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

async function requestJson<T>(path: string, signal: AbortSignal): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { signal });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}.`);
  }

  return (await response.json()) as T;
}

export async function runStartupChecks(options?: {
  timeoutMs?: number;
  onProgress?: (progress: StartupProgress) => void;
}): Promise<StartupResult> {
  const timeoutMs = options?.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    options?.onProgress?.({ stage: "health" });
    const health = await requestJson<HealthResponse>("/", controller.signal);

    options?.onProgress?.({ stage: "domain" });
    const domain = await requestJson<DomainResponse>("/domain", controller.signal);

    return { health, domain };
  } catch (caughtError) {
    if (caughtError instanceof DOMException && caughtError.name === "AbortError") {
      throw new StartupError(
        "Unable to reach the prediction service. Please try again in a few moments.",
        "timeout",
      );
    }

    if (caughtError instanceof StartupError) {
      throw caughtError;
    }

    throw caughtError;
  } finally {
    window.clearTimeout(timeoutId);
  }
}

export function mapStartupFailure(
  caughtError: unknown,
  lastStage: StartupStage | null,
): StartupError {
  if (caughtError instanceof StartupError) {
    return caughtError;
  }

  if (lastStage === "domain") {
    return new StartupError(
      "Unable to load the operational domain. Please try again in a few moments.",
      "domain",
    );
  }

  return new StartupError(
    "Unable to reach the prediction service. Please try again in a few moments.",
    "health",
  );
}

export function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}
