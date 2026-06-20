<template>
  <section class="startup-screen">
    <div class="startup-card">
      <p class="startup-eyebrow">OndeVale</p>
      <h1>Geographic Real Estate Valuation for São Paulo</h1>
      <p class="startup-meta">
        PO-235 Data Science Project
        <br>
        ITA / UNIFESP
      </p>

      <div class="status-list">
        <article class="status-row">
          <span class="status-icon" :class="statusClass(startupState.frontendLoaded)">
            {{ statusIcon(startupState.frontendLoaded) }}
          </span>
          <div>
            <strong>Frontend Loaded</strong>
            <p>The application shell is ready in the browser.</p>
          </div>
        </article>

        <article class="status-row">
          <span class="status-icon" :class="statusClass(startupState.predictionService)">
            {{ statusIcon(startupState.predictionService) }}
          </span>
          <div>
            <strong>Connecting to Prediction Service</strong>
            <p>The FastAPI backend may take a moment to wake up.</p>
          </div>
        </article>

        <article class="status-row">
          <span class="status-icon" :class="statusClass(startupState.operationalDomain)">
            {{ statusIcon(startupState.operationalDomain) }}
          </span>
          <div>
            <strong>Loading Operational Domain</strong>
            <p>The application is fetching the model validity region.</p>
          </div>
        </article>
      </div>

      <div v-if="startupState.phase === 'ready'" class="message-block message-ready">
        <strong>System Ready.</strong>
        <p>Preparing the interactive map.</p>
      </div>

      <div v-else-if="startupError" class="message-block message-error">
        <strong>{{ startupError }}</strong>
        <p>Please try again in a few moments.</p>
        <button class="retry-button" type="button" @click="predictionStore.runStartup()">
          Retry
        </button>
      </div>

      <div v-else class="message-block message-info">
        <strong>{{ loadingTitle }}</strong>
        <p>{{ loadingDescription }}</p>
        <p class="message-note">Please wait.</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { storeToRefs } from "pinia";

import { usePredictionStore, type StartupStepStatus } from "../stores/predictionStore";

const predictionStore = usePredictionStore();
const { startupState, startupError } = storeToRefs(predictionStore);

function statusIcon(status: StartupStepStatus): string {
  if (status === "success") {
    return "✓";
  }

  if (status === "error") {
    return "!";
  }

  if (status === "loading") {
    return "⏳";
  }

  return "·";
}

function statusClass(status: StartupStepStatus): string {
  return `status-${status}`;
}

const loadingTitle = computed(() => {
  if (startupState.value.operationalDomain === "loading") {
    return "Loading operational domain...";
  }

  return "Connecting to prediction service...";
});

const loadingDescription = computed(() => {
  if (startupState.value.operationalDomain === "loading") {
    return "The validity domain is being retrieved before the map is displayed.";
  }

  return "The server may take up to one minute to wake up when hosted on the Render free tier.";
});
</script>

<style scoped>
.startup-screen {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 32px 20px;
  background:
    radial-gradient(circle at top left, rgba(93, 173, 226, 0.18), transparent 28%),
    linear-gradient(180deg, #f6f9fc 0%, #eef3f7 100%);
}

.startup-card {
  width: min(640px, 100%);
  padding: 34px 32px;
  border: 1px solid rgba(20, 33, 61, 0.08);
  border-radius: 28px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 250, 253, 0.96));
  box-shadow:
    0 24px 50px rgba(33, 56, 82, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  color: #10243a;
}

.startup-eyebrow {
  margin: 0;
  color: #5c6f82;
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.startup-card h1 {
  margin: 10px 0 12px;
  font-size: clamp(1.9rem, 4vw, 2.8rem);
  line-height: 1.03;
  letter-spacing: -0.04em;
}

.startup-meta {
  margin: 0 0 26px;
  color: #486077;
  font-size: 1rem;
  line-height: 1.6;
}

.status-list {
  display: grid;
  gap: 14px;
}

.status-row {
  display: grid;
  grid-template-columns: 44px 1fr;
  gap: 14px;
  align-items: start;
  padding: 14px 16px;
  border-radius: 20px;
  border: 1px solid rgba(35, 56, 77, 0.08);
  background: rgba(235, 242, 248, 0.72);
}

.status-row strong {
  display: block;
  margin-bottom: 4px;
  font-size: 0.96rem;
}

.status-row p {
  margin: 0;
  color: #5d7287;
  font-size: 0.9rem;
  line-height: 1.45;
}

.status-icon {
  display: inline-grid;
  width: 32px;
  height: 32px;
  place-items: center;
  border-radius: 999px;
  font-size: 0.95rem;
  font-weight: 800;
}

.status-success {
  color: #0f5132;
  background: rgba(46, 125, 50, 0.12);
}

.status-loading {
  color: #38526b;
  background: rgba(93, 173, 226, 0.18);
}

.status-pending {
  color: #6f8294;
  background: rgba(159, 173, 186, 0.14);
}

.status-error {
  color: #8f1d21;
  background: rgba(209, 73, 91, 0.14);
}

.message-block {
  margin-top: 24px;
  padding: 18px 20px;
  border-radius: 20px;
  border: 1px solid rgba(35, 56, 77, 0.08);
}

.message-block strong {
  display: block;
  margin-bottom: 6px;
  font-size: 1rem;
}

.message-block p {
  margin: 0;
  color: #4f6478;
  line-height: 1.55;
}

.message-note {
  margin-top: 6px;
}

.message-info {
  background: rgba(227, 239, 247, 0.72);
}

.message-ready {
  background: rgba(234, 246, 236, 0.88);
}

.message-error {
  background: rgba(252, 236, 236, 0.92);
}

.retry-button {
  margin-top: 14px;
  padding: 11px 18px;
  border: 0;
  border-radius: 999px;
  background: #10243a;
  color: #ffffff;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.retry-button:hover {
  background: #173149;
}

@media (max-width: 640px) {
  .startup-card {
    padding: 26px 22px;
  }

  .status-row {
    grid-template-columns: 36px 1fr;
    padding: 13px 14px;
  }
}
</style>
