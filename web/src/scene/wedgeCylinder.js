import * as THREE from "three";

/**
 * A wedge cylinder: a cylinder (axis along x, centered at the origin) with
 * a full round cross-section at x=+length/2, tapering via two symmetric
 * planar cuts (upper and lower) to a flat diametral line at x=-length/2 —
 * see docs/adr/0034-wedge-cylinder-threejs.md and src/render_scene.py's
 * make_wedge_cylinder() for the full derivation this ports.
 *
 * Hand-built as a BufferGeometry rather than a CSG clip of a
 * CylinderGeometry (ADR 0034) — the cut is a flat plane through the
 * cylinder (slope = radius/length, matching render_scene.py's `slope`
 * constant exactly), so at any x the cross-section is a circle clipped by
 * two horizontal chords at z = ±zBound(x) (confirmed against
 * docs/adr/0006-wedge-cylinder.md), not an ellipse from naively lerping
 * z-extent while holding y fixed.
 *
 * Five vertex groups, welded only where positions coincide (never sharing
 * indices) so every crease gets distinct per-face normals by construction —
 * the JS analog of render_scene.py's split_vertices=True fix for the same
 * seam:
 *   1. right lateral arc strip (y ≈ +radius)
 *   2. left lateral arc strip (y ≈ -radius)
 *   3. top cut strip (z = +zBound(x)), flat outward normal ∝ (-slope, 0, 1)
 *   4. bottom cut strip (z = -zBound(x)), flat outward normal ∝ (-slope, 0, -1)
 *   5. end cap (triangle fan) at the full-circle end, reusing the arc
 *      strips' own rim vertices so the seam has no gap
 *
 * Triangle winding isn't guaranteed consistently outward across all five
 * patches (the arc strips are parameterized in opposite rotational senses)
 * — callers should render this geometry with `side: THREE.DoubleSide`
 * rather than relying on backface culling.
 */
export function buildWedgeCylinderGeometry(radius, length, resolution = 96) {
  const xFull = length / 2;
  const xThin = -length / 2;
  const lengthSegments = Math.max(4, Math.round(resolution / 2));
  const angularSegments = Math.max(2, Math.round(resolution / 4)); // per side arc

  const positions = [];
  const normals = [];
  const indices = [];

  // 0 at xThin (thin/diametral end), radius at xFull (full-circle end) —
  // same linear taper as render_scene.py's slope-derived cut planes.
  const zBound = (x) => (radius * (x - xThin)) / length;
  const thetaMax = (x) => Math.asin(THREE.MathUtils.clamp(zBound(x) / radius, 0, 1));

  function pushVertex(x, y, z, nx, ny, nz) {
    positions.push(x, y, z);
    normals.push(nx, ny, nz);
    return positions.length / 3 - 1;
  }

  // Winding reversed (a,c,b / a,d,c, not a,b,c / a,c,d) so the arc and cut
  // strips built with this helper are front-facing (CCW) as seen from
  // outside the solid, matching their explicit outward normals above. Get
  // this backwards and three.js's DoubleSide back-face auto-flip
  // (`normal *= faceDirection` in the standard shader chunk) silently
  // negates an already-correct custom normal back to wrong for exactly
  // the outward view that matters — confirmed by cross-product analysis
  // of the un-reversed winding, and by comparing smooth shading (uses
  // this normal, was wrong) against flatShading (recomputes from screen-
  // space derivatives, was correct) on the live wedge. The end cap fan
  // below doesn't use this helper and already winds correctly.
  function addQuad(a, b, c, d) {
    indices.push(a, c, b, a, d, c);
  }

  // --- lateral arc strips: theta centered on 0 (right, y>0) or PI (left,
  // y<0), spanning [-thetaMax(x), +thetaMax(x)] around that center at each
  // x. Radial (outward) normals — a plain cylinder-surface normal. ---
  function buildArcStrip(center) {
    const grid = [];
    for (let i = 0; i <= lengthSegments; i++) {
      const x = xThin + (i / lengthSegments) * length;
      const tMax = thetaMax(x);
      const row = [];
      for (let j = 0; j <= angularSegments; j++) {
        const theta = center + THREE.MathUtils.lerp(-tMax, tMax, j / angularSegments);
        const y = radius * Math.cos(theta);
        const z = radius * Math.sin(theta);
        row.push(pushVertex(x, y, z, 0, Math.cos(theta), Math.sin(theta)));
      }
      grid.push(row);
    }
    for (let i = 0; i < lengthSegments; i++) {
      for (let j = 0; j < angularSegments; j++) {
        addQuad(grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]);
      }
    }
    return grid;
  }

  const rightGrid = buildArcStrip(0);
  const leftGrid = buildArcStrip(Math.PI);

  // --- cut strips: flat quads at z = sign*zBound(x), spanning
  // y in [-w(x), +w(x)] where w(x) = radius*cos(thetaMax(x)). Outward
  // normal derived directly from the face's own plane equation (kept
  // material is z <= zBound(x) for the top face, so outward — away from
  // the solid — is the gradient of f(x,z) = z - zBound(x), i.e.
  // (-slope, 0, 1); mirrored for the bottom face). NOT the same sign as
  // render_scene.py's own n_upper/n_lower: those are vtkClipClosedSurface
  // *clip-plane* normals (pointing at the material being cut away), which
  // is the opposite convention from a resulting face's outward surface
  // normal — copying them verbatim here produced inward-facing normals and
  // visibly wrong (near-black, "see-through"-looking) shading on the
  // tapered half of the object until caught by eye against the live
  // viewer. ---
  function buildCutStrip(sign, normal) {
    const grid = [];
    for (let i = 0; i <= lengthSegments; i++) {
      const x = xThin + (i / lengthSegments) * length;
      const zb = sign * zBound(x);
      const w = radius * Math.cos(thetaMax(x));
      const idxRight = pushVertex(x, w, zb, normal.x, normal.y, normal.z);
      const idxLeft = pushVertex(x, -w, zb, normal.x, normal.y, normal.z);
      grid.push([idxRight, idxLeft]);
    }
    for (let i = 0; i < lengthSegments; i++) {
      const [aR, aL] = grid[i];
      const [bR, bL] = grid[i + 1];
      if (sign > 0) addQuad(aR, bR, bL, aL);
      else addQuad(aL, bL, bR, aR);
    }
  }

  const slope = radius / length;
  buildCutStrip(1, new THREE.Vector3(-slope, 0, 1).normalize()); // top face outward normal
  buildCutStrip(-1, new THREE.Vector3(-slope, 0, -1).normalize()); // bottom face outward normal

  // --- end cap: triangle fan at x = xFull, reusing the arc strips' own
  // last-row vertices (not fresh ones) so the rim has no seam gap. Right
  // row runs bottom -> right -> top; left row runs top -> left -> bottom —
  // concatenated they form one closed loop around the full circle. ---
  {
    const centerIdx = pushVertex(xFull, 0, 0, 1, 0, 0);
    const rim = [...rightGrid[lengthSegments], ...leftGrid[lengthSegments]];
    for (let k = 0; k < rim.length; k++) {
      indices.push(centerIdx, rim[k], rim[(k + 1) % rim.length]);
    }
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
  geometry.setIndex(indices);
  return geometry;
}
