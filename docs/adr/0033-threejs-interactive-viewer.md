# 0033 — three.js interactive viewer, deployed via GitHub Pages

## Status

Accepted

## Context

AGENTS.md's Features & Future Work listed exactly one open item since the
project's early days: port the scene to three.js for interactive
in-browser viewing (orbit the camera, etc.), instead of PyVista's static
offline renders — explicitly framed there as a *re-derivation*, since
three.js is not a PyVista/VTK target and no direct code port is possible.

Decided with the user before implementation: host on GitHub Pages (the
repo's origin is already GitHub, not GitLab), build via GitHub Actions;
interactivity scope is orbit camera (`OrbitControls`) plus a live style
switcher (no page reload), not a full parametric playground; shadows are
real-time three.js shadow maps, tuned per-surface analogous to
`render_scene.py`'s inscribed-circle cone-angle fitting (ADR 0009/0017),
not baked shadow textures.

## Decision

- **New `web/` top-level directory**, holding a self-contained Vite +
  vanilla-JS (no framework) app. Same "avoid root clutter" move ADR 0028
  made for `src/`/`renders/`, now for a third, unrelated toolchain (Node/
  npm vs. Python/pip) — no naming collision with anything already in the
  repo, nothing under `src/`/`renders/`/`docs/` moved or renamed. Vite
  chosen for a small three.js app: fast dev server, trivial static build
  output, ES modules, easy GitHub Pages base-path config
  (`vite.config.js`'s `base: "/TriformFacet/"`, hardcoded rather than
  derived from CI env — matches this repo's existing "no config layer it
  doesn't need" preference, ADR 0003).
- **Module structure mirrors `render_scene.py`'s own function
  decomposition** 1:1 by name (`buildRoomAndObject`, `addFittedLights`,
  `addEdgeHighlightLines`, `addFeatureEdges`, `fitConeHalfAngle`), under
  `web/src/scene/`, so the Python file stays directly navigable as the
  spec for the JS. Style data (palettes/shading/light-color overrides) is
  centralized in `web/src/scene/palettes.js`, one source of truth per
  style — the same reason the Python side's `build_room_and_object()`/
  `add_fitted_lights()` take override dicts instead of each style variant
  forking the whole scene.
- **Wedge-cylinder geometry**: hand-built `BufferGeometry`, not a CSG
  library — see ADR 0034 for the full derivation.
- **`Line2`/`LineMaterial`/`LineSegmentsGeometry`** (three.js's `examples/
  jsm/lines` addon) for the corner-highlight and feature-edge overlay
  lines, not core `THREE.Line` — core `Line`'s `linewidth` is ignored on
  most platforms (a known three.js/ANGLE limitation), and these lines need
  a real, controllable pixel width to read the way `render_scene.py`'s
  `line_width=3`/`2.5` VTK lines do.
- **Style-switcher scope**: default, blueprint, cel-shade, and grayscale
  (folded in — it turned out to be a free `lightColors`-only override once
  the other three existed, see `web/src/styles/styles.js`). Hand-drawn/
  sketchbook (the Python side's 4th variant, ADR 0031) is explicitly *not*
  ported — its wobbly-line generation is bespoke enough to warrant its own
  pass rather than folding into this one; recorded as deferred, not
  dropped, in AGENTS.md.
- **GitHub Pages via Actions**, modern native deploy
  (`actions/upload-pages-artifact` + `actions/deploy-pages`, not the
  legacy `gh-pages` branch), triggered on push to `main`, path-filtered to
  `web/**` (plus the workflow file itself) so Python/README/ADR-only
  commits don't trigger a rebuild.
- **z-up scene, not three.js's y-up default** (`camera.up.set(0,0,1)`,
  applied consistently across every scene module) — deliberate, so every
  constant ported from `render_scene.py` (`ROOM`, `CYL_CENTER`,
  `SCENE_CAMERA_POSITION`, etc.) stays copy-pasteable verbatim rather than
  needing an axis remap at every use site, trading three.js idiom for
  transcription safety against the Python source of truth.

## Consequences

- The Python rendering pipeline (`src/`, `renders/`) is untouched and
  remains the source of truth for every static render in the repo; `web/`
  is purely additive, verified by running every existing `render_*.py`
  script unchanged.
- A reader auditing the viewer's fidelity to the Python scene can compare
  module-for-module and constant-for-constant rather than needing to
  reverse-engineer an unfamiliar restructuring.
- The style switcher's scope (4 of the Python side's 5 variants, no
  parametric controls) is a real, documented gap versus the full Python
  feature set — see README's "Live viewer" → "Differences from the Python
  renderer" for the complete list, kept current as the viewer grows.
- Node/npm is now a second toolchain contributors need locally to work on
  `web/` — isolated to that directory (own `package.json`/lockfile/
  `.gitignore` entries), no effect on the Python side's `python3 -m venv`
  workflow.
