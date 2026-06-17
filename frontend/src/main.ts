import { createApp } from "vue";
import { createPinia } from "pinia";
import "maplibre-gl/dist/maplibre-gl.css";

import App from "./App.vue";
import "./style.css";

const app = createApp(App);

app.use(createPinia());
app.mount("#app");
