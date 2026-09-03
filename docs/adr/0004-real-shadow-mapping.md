# 0004 — Real shadow mapping via positional lights, not faked contact shadows

## Status

Accepted

## Context

The first working render used a single studio lightkit (no real shadows)
plus a hand-authored flat, semi-transparent ellipse mesh under the object to
fake a "contact shadow" on the floor. This doesn't generalize: the actual
requirement is three *different*, correctly-shaped shadows — one per surface
— that must automatically match whatever the floating object's silhouette
looks like from each light's direction, including after the object became a
custom-cut "wedge cylinder" (ADR 0006) rather than a plain cylinder. A
hand-authored decal shape can't track that.

An early attempt at real shadows (`plotter.enable_shadows()` with one
`pv.Light` added on top of `enable_lightkit()`) produced severe artifacts —
hard black banding across the walls and floor.

## Decision

- Use `Plotter.enable_shadows()` for real VTK shadow-map rendering.
- Drop `enable_lightkit()` entirely — the banding artifacts went away once
  lighting came only from explicit positional `pv.Light` objects, with no
  camera-attached lightkit lights mixed in.
- Use one dedicated `pv.Light` per surface (floor, back wall, side wall),
  each a true positional light (`positional = True`) with a defined
  `cone_angle`, rather than an omnidirectional point light — spotlights
  give VTK's shadow pass a single well-defined shadow-map frustum per light,
  which omnidirectional point lights don't map onto as cleanly.

## Consequences

- Shadows are geometrically correct and automatically follow the object's
  actual shape — required once the object became the custom wedge cylinder.
- Inherits VTK's shadow-map quirks: grazing-angle acne (addressed by light
  placement, ADR 0005) and a distance-related coverage limitation (ADR
  0005), with no resolution/bias controls exposed by this PyVista version's
  `Plotter.enable_shadows()` / `Light.__init__`.
