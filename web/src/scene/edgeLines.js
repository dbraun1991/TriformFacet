import * as THREE from "three";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { HEIGHT, ROOM } from "./constants.js";

/**
 * The room's three shared edges (floor/wall_back, floor/wall_side,
 * wall_back/wall_side) as bright, unlit lines — mirrors
 * render_scene.py's add_edge_highlight_lines(). Uses Line2/LineMaterial for
 * real pixel-width lines (core THREE.Line ignores `linewidth` on most
 * platforms). Returns the LineSegments2 object so styles/styleManager.js
 * can recolor it live.
 */
export function addEdgeHighlightLines(scene, renderer, color = "#ffffff", lineWidth = 3) {
  const points = [
    0, 0, 0, ROOM, 0, 0, // floor / wall_back shared edge
    0, 0, 0, 0, ROOM, 0, // floor / wall_side shared edge
    0, 0, 0, 0, 0, HEIGHT, // wall_back / wall_side shared edge
  ];

  const geometry = new LineSegmentsGeometry();
  geometry.setPositions(points);

  const material = new LineMaterial({
    color,
    linewidth: lineWidth, // pixels
    depthTest: true,
  });
  const size = renderer.getSize(new THREE.Vector2());
  material.resolution.set(size.x, size.y);

  const lines = new LineSegments2(geometry, material);
  scene.add(lines);
  return lines;
}
