<template>
  <StartupScreen v-if="!applicationReady" />
  <HomeView v-else />
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { storeToRefs } from "pinia";

import StartupScreen from "./components/StartupScreen.vue";
import HomeView from "./views/HomeView.vue";
import { usePredictionStore } from "./stores/predictionStore";

const predictionStore = usePredictionStore();
const { applicationReady } = storeToRefs(predictionStore);

onMounted(async () => {
  await predictionStore.runStartup();
});
</script>
