<template>
  <div ref="mapElement" class="map-root"></div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import maplibregl, { type LngLatLike, Marker } from "maplibre-gl";
import type { Feature, FeatureCollection, Polygon } from "geojson";
import { storeToRefs } from "pinia";

import { usePredictionStore } from "../stores/predictionStore";

const SÃO_PAULO_CENTER: LngLatLike = [-46.6333, -23.5505];
const CARTO_POSITRON_STYLE =
  "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";

const mapElement = ref<HTMLDivElement | null>(null);
const predictionStore = usePredictionStore();
const { domain, selectedLatitude, selectedLongitude } = storeToRefs(predictionStore);

let map: maplibregl.Map | null = null;
let marker: Marker | null = null;
const DOMAIN_SOURCE_ID = "validity-domain";
const MASK_SOURCE_ID = "validity-mask";

function buildDomainPolygon(): Feature<Polygon> | null {
  if (!domain.value) {
    return null;
  }

  return {
    type: "Feature",
    properties: {},
    geometry: {
      type: "Polygon",
      coordinates: [[
        [domain.value.longitude_min, domain.value.latitude_min],
        [domain.value.longitude_max, domain.value.latitude_min],
        [domain.value.longitude_max, domain.value.latitude_max],
        [domain.value.longitude_min, domain.value.latitude_max],
        [domain.value.longitude_min, domain.value.latitude_min],
      ]],
    },
  };
}

function buildMaskPolygon(): Feature<Polygon> | null {
  if (!domain.value) {
    return null;
  }

  return {
    type: "Feature",
    properties: {},
    geometry: {
      type: "Polygon",
      coordinates: [
        [
          [-180, -85],
          [180, -85],
          [180, 85],
          [-180, 85],
          [-180, -85],
        ],
        [
          [domain.value.longitude_min, domain.value.latitude_min],
          [domain.value.longitude_min, domain.value.latitude_max],
          [domain.value.longitude_max, domain.value.latitude_max],
          [domain.value.longitude_max, domain.value.latitude_min],
          [domain.value.longitude_min, domain.value.latitude_min],
        ],
      ],
    },
  };
}

function syncDomainLayers(): void {
  if (!map || !domain.value || !map.isStyleLoaded()) {
    return;
  }

  const domainFeature = buildDomainPolygon();
  const maskFeature = buildMaskPolygon();
  if (!domainFeature || !maskFeature) {
    return;
  }

  const domainGeoJson: FeatureCollection<Polygon> = {
    type: "FeatureCollection",
    features: [domainFeature],
  };
  const maskGeoJson: FeatureCollection<Polygon> = {
    type: "FeatureCollection",
    features: [maskFeature],
  };

  const domainSource = map.getSource(DOMAIN_SOURCE_ID) as maplibregl.GeoJSONSource | undefined;
  const maskSource = map.getSource(MASK_SOURCE_ID) as maplibregl.GeoJSONSource | undefined;

  if (domainSource && maskSource) {
    domainSource.setData(domainGeoJson);
    maskSource.setData(maskGeoJson);
    return;
  }

  map.addSource(DOMAIN_SOURCE_ID, {
    type: "geojson",
    data: domainGeoJson,
  });
  map.addSource(MASK_SOURCE_ID, {
    type: "geojson",
    data: maskGeoJson,
  });

  map.addLayer({
    id: "validity-mask-fill",
    type: "fill",
    source: MASK_SOURCE_ID,
    paint: {
      "fill-color": "#10243a",
      "fill-opacity": 0.18,
    },
  });

  map.addLayer({
    id: "validity-domain-fill",
    type: "fill",
    source: DOMAIN_SOURCE_ID,
    paint: {
      "fill-color": "#5dade2",
      "fill-opacity": 0.06,
    },
  });

  map.addLayer({
    id: "validity-domain-outline",
    type: "line",
    source: DOMAIN_SOURCE_ID,
    paint: {
      "line-color": "#1f5f8b",
      "line-width": 2,
      "line-dasharray": [2, 2],
    },
  });
}

function syncMarker(latitude: number | null, longitude: number | null): void {
  if (!map || latitude === null || longitude === null) {
    return;
  }

  if (!marker) {
    marker = new Marker({
      color: "#d1495b",
      scale: 1.15,
    });
  }

  marker.setLngLat([longitude, latitude]).addTo(map);
}

onMounted(() => {
  if (!mapElement.value) {
    return;
  }

  map = new maplibregl.Map({
    container: mapElement.value,
    style: CARTO_POSITRON_STYLE,
    center: SÃO_PAULO_CENTER,
    zoom: 10.5,
    attributionControl: {},
  });

  map.addControl(new maplibregl.NavigationControl(), "top-left");

  map.on("load", () => {
    syncDomainLayers();
  });

  map.on("click", async (event) => {
    const latitude = Number(event.lngLat.lat.toFixed(6));
    const longitude = Number(event.lngLat.lng.toFixed(6));
    await predictionStore.selectLocation(latitude, longitude);
  });
});

watch(
  [selectedLatitude, selectedLongitude],
  ([latitude, longitude]) => {
    syncMarker(latitude, longitude);
  },
  { immediate: true },
);

watch(domain, () => {
  syncDomainLayers();
});

onBeforeUnmount(() => {
  marker?.remove();
  map?.remove();
});
</script>

<style scoped>
.map-root {
  height: 100vh;
  width: 100%;
}
</style>
