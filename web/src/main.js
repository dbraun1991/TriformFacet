import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { addEdgeHighlightLines } from "./scene/edgeLines.js";
import { addFittedLights } from "./scene/lights.js";
import { buildRoomAndObject } from "./scene/room.js";
import { applySceneCamera } from "./scene/camera.js";
import { SCENE_CAMERA_FOCAL_POINT } from "./scene/constants.js";
import { DEFAULT_PALETTE } from "./scene/palettes.js";
import { createStyleManager } from "./styles/styleManager.js";
import { mountStyleSwitcher } from "./ui/styleSwitcher.js";

const container = document.getElementById("app");

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(DEFAULT_PALETTE.background);

const camera = new THREE.PerspectiveCamera(32, window.innerWidth / window.innerHeight, 0.1, 1000);
applySceneCamera(camera);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(...SCENE_CAMERA_FOCAL_POINT);
controls.update();

const meshes = buildRoomAndObject(scene);
const lights = addFittedLights(scene, renderer);
const edgeLines = addEdgeHighlightLines(scene, renderer);

const styleManager = createStyleManager(scene, renderer, { meshes, lights, edgeLines });
mountStyleSwitcher(document.getElementById("style-switcher"), styleManager);
if (import.meta.env.DEV) {
  window.styleManager = styleManager; // console: styleManager.applyStyle("blueprint")
}

// Objects whose material tracks the viewport's pixel size (Line2/LineMaterial)
// need their `resolution` updated on resize — collected here so the resize
// handler can reach them without each style/feature-edge module re-wiring it.
const resolutionDependents = [edgeLines.material, ...styleManager.lineMaterials];

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  for (const material of resolutionDependents) {
    material.resolution.set(window.innerWidth, window.innerHeight);
  }
});

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

if (import.meta.env.DEV) {
  const { ambient, ...spotLights } = lights;
  import("./ui/debugPanel.js").then(({ mountDebugPanel }) =>
    mountDebugPanel({ ambient, lights: spotLights }),
  );
}
