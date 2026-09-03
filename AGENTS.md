# AGENTS.md

Guidance for AI agents (and humans) working in this repo.

## What this project is

`TriformFacet` renders one scene: the corner of a room (a floor and two
walls, doubling as an unscaled 3D coordinate frame) with an object floating
in the air above the floor, lit by three colored lights — one per surface.

The point of the scene: the floating object is shaped so that it casts a
*different, equally true* shadow on each surface — a rectangle on the floor,
a circle on one wall, a triangle on the other. See `README.md` → Concept for
the full framing ("the truth one observes does not falsify the truth of
others").

Two names were weighed for the open-source release — Aletheia (Greek for
truth-as-unconcealment, naming *why* the other two shadows stay hidden at
once) and TriformFacet (one facet, three true forms, naming *what* there is
to see) — and TriformFacet won on approachability: it explains itself
without a philosophy gloss. See `README.md` → Naming for the full reasoning.

Read `README.md` first for the current state of the scene and its known
rough edges. Read `docs/adr/` for *why* it's built the way it is — several
non-obvious choices in `render_scene.py` (light placement, the clip-based
object construction, the room geometry) are the result of dead ends that
looked reasonable but didn't work; the ADRs explain what was tried and
ruled out so it doesn't get re-tried.

## Running it

```bash
python3 -m venv .venv          # only if .venv doesn't already exist
.venv/bin/pip install pyvista
.venv/bin/python src/render_scene.py               # renders/scene.png — the main illustration
.venv/bin/python src/render_icon.py                # renders/icon.png — square icon crop
.venv/bin/python src/render_icon_highres.py        # renders/highres_icon.png — same icon, 8192px (ADR 0025)
.venv/bin/python src/render_icon_grayscale.py      # renders/grayscale_icon.png — icon, light-only grayscale (ADR 0027)
.venv/bin/python src/render_icon_highres_grayscale.py  # renders/highres_grayscale_icon.png — same, 8192px
```

All five write into `renders/`, resolved relative to each script's own file
location (not the invoking cwd) — see ADR 0028. Rendering is headless/
off-screen (VTK's software path) — no display or Xvfb needed or available
on this machine.

## Repo layout

- `src/` — every `render_*.py` script, flat (ADR 0003 kept this a single
  static illustration, not a package). They import each other by bare
  module name (e.g. `from render_scene import build_scene`), which only
  resolves correctly when run as `python src/<file>.py` — running a script
  from inside `src/` or importing one from elsewhere requires `src/` on
  `sys.path` some other way.
- `renders/` — every generated PNG. Fully derived; never hand-edit, just
  re-run the relevant script.
- `docs/adr/` — the ADR log referenced throughout this file.

## Working on `src/render_scene.py`

- All scene parameters (room size, object size/position, camera, lights)
  are plain module-level constants near the top of the file — edit them
  directly, there's no config/CLI layer (see ADR 0003).
- After any geometry or lighting change, re-render and actually look at
  `renders/scene.png` before calling it done — this is a visual
  illustration; a clean diff is not sufficient evidence it looks right.
- If a change produces a lighting/shadow artifact, check `docs/adr/` first
  — several look-alike issues (grazing-angle acne vs. distance-based
  coverage loss vs. cone-angle) turned out to have different, non-obvious
  causes when this scene was first built. Isolate with a minimal
  reproduction (strip the scene down to one wall + one light, no occluder)
  rather than guessing at the full scene.
- When adding a new floating-object shape, remember `clip_closed_surface()`
  requires a manifold mesh (`triangulate().clean()` first) and that any new
  sharp crease needs `compute_normals(split_vertices=True, ...)` or smooth
  shading will blend across it and produce dark banding (ADR 0006).

## Decisions

Significant decisions and their rationale live in `docs/adr/` as numbered
ADRs (Context / Decision / Consequences). Add a new one for any decision
that reverses or meaningfully qualifies a prior approach — the value here is
mainly in recording *dead ends*, not just what shipped.

## Features & Future Work

Only genuinely open items — resolved history lives in `docs/adr/`, not here.

- Alternate, sketchier rendering styles for this scene — blueprint/
  technical-drawing, cel/toon shading, hand-drawn — explicitly deferred,
  not started. When picked back up, expect multiple side-by-side style
  variants to compare rather than one direction picked unprompted (the
  pattern used for the corner-visibility exploration, ADR 0013).
