# 0027 — Grayscale icon variant, light colors parameterized

## Status

Accepted

## Context

Requested: a second icon look, `grayscale_icon.png` /
`highres_grayscale_icon.png`, using only light (bright) grayscale tones —
no hue at all — instead of the amber/blue/rose spotlights.

The three spotlight colors were previously hardcoded as literal string
arguments inside `add_fitted_lights()`'s `pv.Light(...)` calls. Producing a
second look meant either duplicating `add_fitted_lights`/`build_scene`
wholesale (risking drift, the exact failure mode ADR 0011/0025 already
avoided for the icon composition itself) or parameterizing the one existing
function. Parameterized it: `add_fitted_lights(plotter, colors=None)` merges
an optional per-surface override dict over `DEFAULT_LIGHT_COLORS`; geometry,
cone angles, shadow mapping, and everything else about the rig is untouched
either way. `build_scene()` and `render_icon()` both gained a pass-through
`light_colors` parameter for the same reason.

Picked three grayscale values (`#ffffff` / `#d9d9d9` / `#b3b3b3` — i.e. the
top ~30% of the 0-255 range) rather than desaturating the original amber/
blue/rose by literal luminance: those three hues have quite different
native luminances (amber and rose are much darker than blue at equal
saturation), so a naive desaturation would have produced three unevenly-
dark, muddier grays instead of a bright, evenly-spaced-by-lightness trio.
Chose the three values by eye for even, clearly-distinguishable steps
(confirmed by rendering, not just picking hex values), not derived
algorithmically — no existing formula in this codebase maps hue→lightness,
and one felt like over-engineering for three fixed constants.

## Decision

- `render_scene.py`: `DEFAULT_LIGHT_COLORS` module constant holds the
  original amber/blue/rose, keyed by surface (`floor`/`wall_back`/
  `wall_side`, matching `add_fitted_lights`'s existing per-light dict).
  `add_fitted_lights(plotter, colors=None)` merges any override over that
  default. `build_scene(plotter, light_colors=None)` passes through.
- `render_icon.py`: `render_icon(size, output_path, light_colors=None)`
  passes through to `build_scene`.
- New `render_icon_grayscale.py`: `GRAYSCALE_LIGHT_COLORS` dict
  (`#ffffff`/`#d9d9d9`/`#b3b3b3`) and `render_grayscale_icon(size,
  output_path)`, calling `render_icon()` with that override. `__main__`
  writes `grayscale_icon.png` at `ICON_SIZE`.
- New `render_icon_highres_grayscale.py`: same pattern as
  `render_icon_highres.py`, calling `render_grayscale_icon(8192, ...)` to
  write `highres_grayscale_icon.png`.
- Verified no regression: re-rendering `icon.png`/`highres_icon.png` after
  this refactor produced byte-identical files (default colors unchanged).

## Consequences

- Two icon looks now share one composition/camera/geometry pipeline with
  zero duplicated scene logic — only light color differs between them.
- The grayscale render loses the concept's color-coded "which light, which
  truth" legibility (see README → Concept) in exchange for shape/lightness
  legibility alone; it's an alternate look, not a replacement for the
  default colored icon.
- Any future look that only needs different light colors (e.g. a
  single-brand-color variant) is now a ~15-line file following the same
  pattern, not a scene fork.
