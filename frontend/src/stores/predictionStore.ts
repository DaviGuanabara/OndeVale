import { defineStore } from "pinia";
import { ref } from "vue";

import { requestDomain, requestPrediction, type DomainResponse } from "../services/predictionService";

export const usePredictionStore = defineStore("prediction", () => {
  const selectedLatitude = ref<number | null>(null);
  const selectedLongitude = ref<number | null>(null);
  const predictedPriceM2 = ref<number | null>(null);
  const domain = ref<DomainResponse | null>(null);
  const insideDomain = ref<boolean | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

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
      domain.value = await requestDomain();
      error.value = null;
    } catch (caughtError) {
      error.value =
        caughtError instanceof Error
          ? caughtError.message
          : "Unexpected error while loading the model validity domain.";
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
    loadDomain,
    isInsideDomain,
    selectLocation,
  };
});
