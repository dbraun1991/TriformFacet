# 0015 — Unlit edge lines promoted from experiment to the default scene

## Status

Accepted

## Context

ADR 0013 tried two ways to make the room's inner corner read as an actual
3D space: unlit edge lines (`render_scene_whiteline.py`) and a
"pixel-perfect" fully-lit alternative (`render_scene_pixelperfect.py`),
kept as separate outputs alongside the existing `scene.png` so they could
be compared directly. Feedback after seeing all three side by side: the
white-line version is preferred over the (until-then) default `scene.png`.

## Decision

Fold `add_edge_highlight_lines()` into `build_scene()` itself, so it's part
of the default scene rather than a separate opt-in variant. Concretely:

- `render_scene.py`'s `scene.png` and `render_icon.py`'s `icon.png` both
  now include the edge lines automatically (no code change needed in
  `render_icon.py` — it already builds its scene via `build_scene()`).
- `render_scene_whiteline.py` and its `scene_whiteline.png` output are
  deleted — `render_scene.py` *is* now that version, so keeping a separate,
  identical-looking script would just be dead duplication.
- `render_scene_pixelperfect.py` is **not** folded in — it remains a
  separate, still-distinct-looking experimental variant (no dark corners
  at all, a materially different aesthetic), not something "promoted" the
  same way.

## Consequences

- `scene.png` and `icon.png` both changed appearance (edge lines added) as
  of this decision — anyone comparing against earlier screenshots in this
  conversation/session should expect the difference.
- One fewer render script to keep in sync; `build_scene()` is simpler to
  reason about as "the" default scene builder again, rather than one of
  several similar variants.
- If a no-line comparison is ever wanted again, it's a one-line change
  (drop the `add_edge_highlight_lines(plotter)` call), not a missing
  capability — `add_fitted_lights()` and `add_edge_highlight_lines()` are
  still separate functions.
