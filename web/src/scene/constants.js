// Ported verbatim from src/render_scene.py's module-level constants. Keep
// these values byte-identical to the Python source — this file is the JS
// side's single source of truth for the room/object/camera geometry, same
// role render_scene.py plays for the Python renderer.

export const ROOM = 28.0;
export const HEIGHT = 24.0;

export const CYL_RADIUS = 0.5;
export const CYL_LENGTH = (2.8 * 2) / 3; // ≈ 1.8667

const M = 3.0;
export const CYL_CENTER = [M, M, M];

// Gap kept between each light's footprint and the white corner line nearest
// it (render_scene.py's LIGHT_PADDING / ADR 0017).
export const LIGHT_PADDING = 0.5;

// The wide establishing-shot camera — position/focal_point/up/view_angle,
// copied from render_scene.py's SCENE_CAMERA_* constants.
export const SCENE_CAMERA_POSITION = [53.6, 51.2, 32.4];
export const SCENE_CAMERA_FOCAL_POINT = [7.6, 10.4, 6.4];
export const SCENE_CAMERA_UP = [0, 0, 1];
export const SCENE_CAMERA_VIEW_ANGLE = 32; // vertical FOV, degrees
