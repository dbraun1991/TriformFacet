import {
  SCENE_CAMERA_FOCAL_POINT,
  SCENE_CAMERA_POSITION,
  SCENE_CAMERA_UP,
  SCENE_CAMERA_VIEW_ANGLE,
} from "./constants.js";

/**
 * Positions `camera` at the wide establishing shot — mirrors
 * render_scene.py's __main__ camera setup. Scene is authored z-up
 * (matching the Python side), a deliberate deviation from three.js's
 * y-up default so every ported constant stays copy-pasteable.
 */
export function applySceneCamera(camera) {
  camera.up.set(...SCENE_CAMERA_UP);
  camera.position.set(...SCENE_CAMERA_POSITION);
  camera.fov = SCENE_CAMERA_VIEW_ANGLE;
  camera.lookAt(...SCENE_CAMERA_FOCAL_POINT);
  camera.updateProjectionMatrix();
}
