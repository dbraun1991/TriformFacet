import * as THREE from "three";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";

/**
 * Boundary/sharp-crease edges of the given meshes, as one bright unlit
 * LineSegments2 — mirrors render_scene.py's add_feature_edges(). `meshes`
 * is any iterable of THREE.Mesh; `thresholdAngle` (degrees) is the minimum
 * dihedral angle VTK/three.js counts as a "feature" edge (three's
 * EdgesGeometry default is 1°, PyVista's is 30° — pass explicitly per
 * caller, matching render_scene.py's own per-style overrides rather than
 * relying on a differing library default).
 */
export function addFeatureEdges(
  scene,
  renderer,
  meshes,
  { color = "#ffffff", lineWidth = 1.5, thresholdAngle = 30 } = {},
) {
  const points = [];
  for (const mesh of meshes) {
    const edges = new THREE.EdgesGeometry(mesh.geometry, thresholdAngle);
    const pos = edges.attributes.position;
    const offset = mesh.position;
    for (let i = 0; i < pos.count; i++) {
      points.push(
        pos.getX(i) + offset.x,
        pos.getY(i) + offset.y,
        pos.getZ(i) + offset.z,
      );
    }
    edges.dispose();
  }

  const geometry = new LineSegmentsGeometry();
  geometry.setPositions(points);

  const material = new LineMaterial({ color, linewidth: lineWidth, depthTest: true });
  const size = renderer.getSize(new THREE.Vector2());
  material.resolution.set(size.x, size.y);

  const lines = new LineSegments2(geometry, material);
  scene.add(lines);
  return lines;
}
