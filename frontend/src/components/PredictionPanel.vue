<template>
  <aside class="panel-shell">
    <div class="panel-header">
      <p class="eyebrow">OndeVale</p>
      <h1>Spatial Price Estimator</h1>
      <p class="lead">
        Click anywhere in São Paulo to estimate the local price per square meter
        using the geographic KNN baseline.
      </p>
    </div>

    <section class="panel-section">
      <div class="section-title">Coordinates</div>
      <div class="metric-grid">
        <article class="metric-card">
          <span class="metric-label">Latitude</span>
          <strong>{{ formattedLatitude }}</strong>
        </article>
        <article class="metric-card">
          <span class="metric-label">Longitude</span>
          <strong>{{ formattedLongitude }}</strong>
        </article>
      </div>
    </section>

    <section class="panel-section">
      <div class="section-title">Prediction</div>
      <div class="prediction-card">
        <div class="domain-status" :class="domainStatusClass">
          {{ domainStatusText }}
        </div>
        <span class="metric-label">Price per square meter</span>
        <div v-if="loading" class="status-text">Calculating prediction...</div>
        <div v-else-if="error" class="status-error">{{ error }}</div>
        <div v-else-if="predictedPriceM2 !== null" class="prediction-value">
          {{ formattedPrice }}
          <span class="prediction-unit">BRL/m²</span>
        </div>
        <div v-else class="status-text">
          Select a location on the map to request a prediction.
        </div>
      </div>
    </section>
  </aside>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { storeToRefs } from "pinia";

import { usePredictionStore } from "../stores/predictionStore";

const predictionStore = usePredictionStore();
const {
  selectedLatitude,
  selectedLongitude,
  predictedPriceM2,
  insideDomain,
  loading,
  error,
} = storeToRefs(predictionStore);

const formattedLatitude = computed(() =>
  selectedLatitude.value === null ? "Not selected" : selectedLatitude.value.toFixed(6),
);

const formattedLongitude = computed(() =>
  selectedLongitude.value === null ? "Not selected" : selectedLongitude.value.toFixed(6),
);

const formattedPrice = computed(() => {
  if (predictedPriceM2.value === null) {
    return "";
  }

  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 2,
  }).format(predictedPriceM2.value);
});

const domainStatusText = computed(() => {
  if (selectedLatitude.value === null || selectedLongitude.value === null) {
    return "Awaiting Selection";
  }

  if (insideDomain.value === null) {
    return "Domain Unavailable";
  }

  return insideDomain.value ? "Inside Domain" : "Outside Domain";
});

const domainStatusClass = computed(() => {
  if (selectedLatitude.value === null || selectedLongitude.value === null) {
    return "status-pending";
  }

  if (insideDomain.value === true) {
    return "status-valid";
  }

  return "status-invalid";
});
</script>

<style scoped>
.panel-shell {
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 10;
  width: min(380px, calc(100vw - 32px));
  padding: 22px;
  border: 1px solid rgba(20, 33, 61, 0.08);
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(247, 250, 252, 0.94));
  backdrop-filter: blur(18px);
  box-shadow:
    0 24px 50px rgba(33, 56, 82, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.75);
}

.panel-header h1 {
  margin: 8px 0 12px;
  font-size: clamp(1.6rem, 2vw, 2rem);
  line-height: 1.05;
  letter-spacing: -0.03em;
}

.eyebrow {
  margin: 0;
  color: #5c6f82;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.lead {
  margin: 0;
  color: #41556a;
  font-size: 0.96rem;
}

.panel-section + .panel-section {
  margin-top: 18px;
}

.section-title {
  margin-bottom: 12px;
  color: #23384d;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.metric-card,
.prediction-card {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(235, 242, 248, 0.78);
  border: 1px solid rgba(35, 56, 77, 0.08);
}

.domain-status {
  display: inline-flex;
  margin-bottom: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.status-valid {
  color: #0f5132;
  background: rgba(46, 125, 50, 0.12);
}

.status-pending {
  color: #38526b;
  background: rgba(93, 173, 226, 0.14);
}

.status-invalid {
  color: #8f1d21;
  background: rgba(209, 73, 91, 0.14);
}

.metric-card strong,
.prediction-value {
  display: block;
  margin-top: 8px;
  color: #10243a;
  font-size: 1rem;
}

.metric-label {
  color: #607487;
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.prediction-value {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-top: 10px;
  font-size: clamp(1.35rem, 2vw, 1.9rem);
  font-weight: 700;
  letter-spacing: -0.03em;
}

.prediction-unit {
  color: #607487;
  font-size: 0.9rem;
  font-weight: 600;
}

.status-text {
  margin-top: 10px;
  color: #50657a;
}

.status-error {
  margin-top: 10px;
  color: #b42318;
  font-weight: 600;
}

@media (max-width: 800px) {
  .panel-shell {
    top: auto;
    right: 16px;
    bottom: 16px;
    left: 16px;
    width: auto;
    padding: 18px;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>
