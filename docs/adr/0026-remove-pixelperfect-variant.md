# 0026 — Removed the pixel-perfect variant; circles stay the only default

## Status

Accepted

## Context

`render_scene_pixelperfect.py` (→ `scene_pixelperfect.png`) had been carried
alongside the default circle/whiteline scene since ADR 0013, as a
genuinely different look: full-rectangle lighting via gobo-masked
circumscribed spotlights, instead of `scene.png`'s inscribed circles with
dark corners. Feedback ahead of the open-source release, in the course of
cleaning up the repo for publication: it's not needed — the circle look is
preferred outright, not just as the current default among two live options.

Keeping an unused alternate around has real ongoing cost in a small
project: `render_scene.py` carried a whole function
(`fit_cone_half_angle_circumscribed`) that existed only to serve the
now-removed file, several docstrings cross-referenced a script that would
otherwise no longer exist, and ADR 0019's open padding-asymmetry
investigation was scoped entirely to a variant nobody wants to keep
debugging.

## Decision

- Deleted `render_scene_pixelperfect.py` and `scene_pixelperfect.png`.
- Removed `fit_cone_half_angle_circumscribed()` from `render_scene.py` —
  dead code once its only caller is gone.
- Updated `build_room_and_object`, `add_edge_highlight_lines`,
  `add_fitted_lights`, and `build_scene`'s docstrings in `render_scene.py`
  to drop references to the removed script and to a `render_scene_whiteline.py`
  that had already stopped existing since ADR 0015 but was still mentioned
  in passing.
- Removed the "Variants" section, the pixelperfect row in the "Running it"
  commands, and the pixelperfect-only rows in the "Key parameters" table
  from `README.md`; removed the equivalent references from `AGENTS.md`
  (including the padding-asymmetry Future Work item).
- **Not** deleted: ADRs 0009, 0013, 0016, and 0019, which document the
  pixel-perfect variant's own history (the fins-vs-gobo-masks dead end, the
  corner-visibility experiment it grew out of, the unresolved padding
  asymmetry). Per this project's own stated policy (`AGENTS.md` →
  Decisions), the value in ADRs is mainly recording dead ends, not just
  what shipped — removing a shipped feature doesn't retroactively make its
  history worth erasing. ADR 0019's open investigation is now moot (closed
  by removal, not by finding the root cause) rather than resolved; this
  ADR is the record of that.

## Consequences

- One fewer render script, one fewer output image, no more dead code in
  `render_scene.py` serving a file that no longer exists.
- The default scene (dark corners + white edge lines + inscribed circles)
  is now the *only* lighting treatment in the project, not one of two.
- Anyone reading ADR 0019 in the future will find this ADR linked from it
  in spirit (same numbering sequence) explaining that the investigation
  wasn't finished, just made moot.
