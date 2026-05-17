const ZOOM = 17;
const START_X = 44278;
const START_Y = 78968;

const loadingOverlay = document.getElementById("loading-overlay");
const bandControl = document.getElementById("band-control");
const bandCheckboxes = [...bandControl.querySelectorAll('input[type="checkbox"]')];
const overlayToggle = document.getElementById("overlay-toggle");

function tileToLatLng(x, y, z) {
  const n = 2 ** z;
  const lon = (x / n) * 360 - 180;
  const latRad = Math.atan(Math.sinh(Math.PI * (1 - (2 * y) / n)));
  const lat = (latRad * 180) / Math.PI;
  return [lat, lon];
}

function showLoader() {
  loadingOverlay.classList.remove("hidden");
}

function hideLoader() {
  loadingOverlay.classList.add("hidden");
}

function getSelectedBands() {
  return bandCheckboxes.filter((checkbox) => checkbox.checked).map((checkbox) => checkbox.value);
}

function buildTileUrl() {
  if (overlayToggle.checked) {
    return "/overlay/{z}/{x}/{y}";
  }

  const selectedBands = getSelectedBands();

  // If no band is selected, call backend without bidx so it can apply defaults.
  if (selectedBands.length === 0) {
    return "/tiles/{z}/{x}/{y}";
  }

  const params = new URLSearchParams();
  for (const band of selectedBands) {
    params.append("bidx", band);
  }

  return `/tiles/{z}/{x}/{y}?${params.toString()}`;
}

function syncBandControlState() {
  const usingOverlay = overlayToggle.checked;
  bandControl.classList.toggle("disabled", usingOverlay);
  for (const checkbox of bandCheckboxes) {
    checkbox.disabled = usingOverlay;
  }
}

function createTileLayer() {
  return L.tileLayer(buildTileUrl(), {
    keepBuffer: 6,
    maxNativeZoom: 19,
    maxZoom: 19,
    tileSize: 256,
    updateWhenIdle: false,
  });
}

// Center on the midpoint of the original 2x2 tile block.
const center = tileToLatLng(START_X + 1, START_Y + 1, ZOOM);

// A real map container that can pan and zoom like normal web maps.
const map = L.map("map", {
  zoomControl: true,
  attributionControl: false,
  minZoom: 2,
  maxZoom: 19,
}).setView(center, ZOOM);

// Keep interaction with the control from panning/zooming the map underneath.
L.DomEvent.disableClickPropagation(bandControl);
L.DomEvent.disableScrollPropagation(bandControl);

let tileLayer = createTileLayer();
tileLayer.once("load", hideLoader);
tileLayer.addTo(map);
syncBandControlState();

function reloadTilesForCurrentBands() {
  showLoader();

  map.removeLayer(tileLayer);
  tileLayer = createTileLayer();
  tileLayer.once("load", hideLoader);
  tileLayer.addTo(map);
}

for (const checkbox of bandCheckboxes) {
  checkbox.addEventListener("change", reloadTilesForCurrentBands);
}

overlayToggle.addEventListener("change", () => {
  syncBandControlState();
  reloadTilesForCurrentBands();
});
