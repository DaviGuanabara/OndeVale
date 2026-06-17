<template>
  <main class="home-view">
    <div class="map-frame">
      <MapView />
      <PredictionPanel />
    </div>
  </main>
</template>

<script setup lang="ts">
import { onMounted } from "vue";

import MapView from "../components/MapView.vue";
import PredictionPanel from "../components/PredictionPanel.vue";
import { usePredictionStore } from "../stores/predictionStore";

const predictionStore = usePredictionStore();

onMounted(async () => {
  await predictionStore.loadDomain();
});
</script>

<style scoped>
.home-view {
  min-height: 100vh;
}

.map-frame {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

.map-frame::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(90deg, rgba(245, 247, 250, 0.1), transparent 18%),
    linear-gradient(180deg, transparent, rgba(16, 36, 58, 0.08));
}
</style>
