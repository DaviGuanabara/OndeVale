import { defineStore } from "pinia";
import { ref } from "vue";

import { requestDomain, requestPrediction, type DomainResponse } from "../services/predictionService";
import {
  delay,
  mapStartupFailure,
  runStartupChecks,
  type StartupStage,
} from "../services/startupService";

export type StartupStepStatus = "pending" | "loading" | "success" | "error";

export interface StartupState {
  frontendLoaded: StartupStepStatus;
  predictionService: StartupStepStatus;
  operationalDomain: StartupStepStatus;
  phase: "idle" | "running" | "ready" | "error";
}

function createInitialStartupState(): StartupState {
  return {
    frontendLoaded: "success",
    predictionService: "pending",
    operationalDomain: "pending",
    phase: "idle",
  };
}

export const usePredictionStore = defineStore("prediction", () => {
  const selectedLatitude = ref<number | null>(null);
  const selectedLongitude = ref<number | null>(null);
  const predictedPriceM2 = ref<number | null>(null);
  const domain = ref<DomainResponse | null>(null);
  const insideDomain = ref<boolean | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const applicationReady = ref(false);
  const startupState = ref<StartupState>(createInitialStartupState());
  const startupError = ref<string | null>(null);

  function setDomain(domainData: DomainResponse): void {
    domain.value = domainData;
    if (selectedLatitude.value !== null && selectedLongitude.value !== null) {
      insideDomain.value = isInsideDomain(selectedLatitude.value, selectedLongitude.value);
    }
  }

  function isInsideDomain(latitude: number, longitude: number): boolean {
    if (!domain.value) {
      return false;
    }

    return (
      latitude >= domain.value.latitude_min &&
      latitude <= domain.value.latitude_max &&
      longitude >= domain.value.longitude_min &&
      longitude <= domain.value.longitude_max
    );
  }

  async function loadDomain(): Promise<void> {
    try {
      setDomain(await requestDomain());
      error.value = null;
    } catch (caughtError) {
      error.value =
        caughtError instanceof Error
          ? caughtError.message
          : "Unexpected error while loading the model validity domain.";
    }
  }

  async function runStartup(): Promise<void> {
    let lastStage: StartupStage | null = null;

    applicationReady.value = false;
    startupError.value = null;
    error.value = null;
    startupState.value = {
      frontendLoaded: "success",
      predictionService: "loading",
      operationalDomain: "pending",
      phase: "running",
    };

    try {
      const result = await runStartupChecks({
        timeoutMs: 60_000,
        onProgress(progress) {
          lastStage = progress.stage;

          if (progress.stage === "health") {
            startupState.value = {
              frontendLoaded: "success",
              predictionService: "loading",
              operationalDomain: "pending",
              phase: "running",
            };
            return;
          }

          startupState.value = {
            frontendLoaded: "success",
            predictionService: "success",
            operationalDomain: "loading",
            phase: "running",
          };
        },
      });

      setDomain(result.domain);
      startupState.value = {
        frontendLoaded: "success",
        predictionService: "success",
        operationalDomain: "success",
        phase: "ready",
      };

      await delay(1_000);
      applicationReady.value = true;
    } catch (caughtError) {
      const startupFailure = mapStartupFailure(caughtError, lastStage);
      startupError.value = startupFailure.message;
      const predictionServiceStatus =
        startupFailure.stage === "domain" ||
        (startupFailure.stage === "timeout" && lastStage === "domain")
          ? "success"
          : "error";
      const operationalDomainStatus =
        startupFailure.stage === "domain" ||
        (startupFailure.stage === "timeout" && lastStage === "domain")
          ? "error"
          : "pending";

      startupState.value = {
        frontendLoaded: "success",
        predictionService: predictionServiceStatus,
        operationalDomain: operationalDomainStatus,
        phase: "error",
      };
    }
  }

  async function selectLocation(latitude: number, longitude: number): Promise<void> {
    selectedLatitude.value = latitude;
    selectedLongitude.value = longitude;
    predictedPriceM2.value = null;
    error.value = null;

    insideDomain.value = domain.value ? isInsideDomain(latitude, longitude) : null;

    if (insideDomain.value === false) {
      error.value =
        "Selected point is outside the model validity domain. Prediction disabled.";
      loading.value = false;
      return;
    }

    loading.value = true;

    try {
      const prediction = await requestPrediction({ latitude, longitude });
      predictedPriceM2.value = prediction.price_m2;
    } catch (caughtError) {
      error.value =
        caughtError instanceof Error
          ? caughtError.message
          : "Unexpected error while requesting a prediction.";
    } finally {
      loading.value = false;
    }
  }

  return {
    selectedLatitude,
    selectedLongitude,
    predictedPriceM2,
    domain,
    insideDomain,
    loading,
    error,
    applicationReady,
    startupState,
    startupError,
    loadDomain,
    runStartup,
    isInsideDomain,
    selectLocation,
  };
});
