# 0032 — Icon crops for every style variant; explicit `regular_` prefix

## Status

Accepted

## Context

The three style variants (ADR 0029/0030/0031) only had wide establishing
shots (`scene_blueprint.png` etc.), no square icon crops — requested to
add both sizes (matching the default look's `icon.png`/`highres_icon.png`
pair) for all three.

Also requested: a consistent naming rule across every `renders/` file so
size/style are distinguishable at a glance — every filename prefixed with
`regular_` unless it already starts with `highres_` or `scene_`. Before
this, the default and grayscale regular-size icons were bare (`icon.png`,
`grayscale_icon.png`) while their own highres siblings already carried a
`highres_` prefix — an asymmetry that made the two hard to visually pair
in a directory listing. Renamed `icon.png` → `regular_icon.png` and
`grayscale_icon.png` → `regular_grayscale_icon.png` to fix that, and named
every new file to match: `<regular|highres>_<style>_icon.png`, style
omitted for the default look — e.g. `regular_blueprint_icon.png`,
`highres_celshade_icon.png`.

Building the six new icon crops needed a decision on how much to
generalize `render_icon.py`'s existing `render_icon()` function first.
That function already threads a `light_colors` override through
`build_scene()` (added for the grayscale variant, ADR 0027) — insufficient
for the three style variants, which need their own full `palette`/
`surface_shading`/`object_shading`/`cylinder_resolution`/custom-linework
combinations (already encapsulated in each variant's own
`build_scene_<style>()` from ADR 0029/0030/0031). Threading all of those
individually through `render_icon()` as more parameters would have meant
re-deriving each variant's styling a second time at the call site instead
of reusing `build_scene_<style>()` outright. Extracted the plotter/camera/
screenshot boilerplate into a new `render_icon_from_builder(size,
output_path, build_scene_fn)` that takes an arbitrary single-argument
scene builder instead — `render_icon()` itself now just wraps it with a
`lambda plotter: build_scene(plotter, light_colors=light_colors)`, and
each style variant's icon script passes its own `build_scene_<style>`
directly.

The icon camera itself (`ICON_CAMERA_*`, ADR 0022/0023/0024) needed no
re-tuning: it was empirically fit to the *room/object geometry*
(`ROOM`/`HEIGHT`/`CYL_CENTER`/`CYL_RADIUS`/`LIGHT_PADDING`), none of which
any style variant changes — only palette, shading, and linework differ.
Verified rather than assumed: rendered all three and pixel-scanned each
full frame for its own background color (the same check ADR 0022
established), finding zero matching pixels in every case, same as the
default icon.

## Decision

- `render_icon.py`: `render_icon_from_builder(size, output_path,
  build_scene_fn)` extracted from `render_icon()`'s prior body;
  `render_icon()` now delegates to it. Output constant changed from
  `"icon.png"` to `"regular_icon.png"`.
- `render_icon_grayscale.py`: output constant changed from
  `"grayscale_icon.png"` to `"regular_grayscale_icon.png"`.
- `renders/icon.png` and `renders/grayscale_icon.png` renamed (`git mv`) to
  `regular_icon.png` / `regular_grayscale_icon.png`.
- New `render_icon_blueprint.py` / `render_icon_highres_blueprint.py`,
  `render_icon_celshade.py` / `render_icon_highres_celshade.py`,
  `render_icon_handdrawn.py` / `render_icon_highres_handdrawn.py` — each a
  thin wrapper calling `render_icon_from_builder()` with its style's
  `build_scene_<style>` (imported from the corresponding
  `render_scene_<style>.py`) and the matching `regular_`/`highres_`
  filename. Same regular/highres split and 8192px ceiling as the default
  icon (ADR 0025).
- Verified no regression: re-ran every one of the eight pre-existing
  render scripts after this change — every output byte-identical.

## Consequences

- Every style variant now has the full four-output set the default look
  has (wide scene shot + regular icon + highres icon), 14 files in
  `renders/` total.
- Naming is now uniform and self-sorting: `highres_*` and `regular_*`
  pairs sort adjacently per style, and `scene_*` establishing shots are
  visually distinct from icon crops at a glance.
- `render_icon_from_builder()` is now the generic entry point for "crop
  any `build_scene_<style>(plotter)` composition through the icon
  camera" — a fourth style variant, if one is ever added, gets its own
  regular/highres icon pair as a ~15-line file each, following this same
  pattern, with no further changes to `render_icon.py` needed.
