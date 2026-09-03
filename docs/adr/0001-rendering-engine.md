# 0001 — Rendering engine: PyVista (VTK), headless

## Status

Accepted

## Context

The goal was to recreate a remembered scene — a room corner with a floating
object, shaded/rendered rather than a flat diagram — as a single Python
script. The dev machine has no display and no `Xvfb`/`xvfb-run` installed.
Options considered: Blender via `bpy`, matplotlib 3D, and PyVista.

## Decision

Use PyVista (the Python wrapper around VTK), rendering through
`pv.Plotter(off_screen=True)`. Verified this produces real shaded, lit
screenshots via VTK's software rendering path with no display and no Xvfb
required on this machine.

## Consequences

- Real per-pixel lighting, shading, and (with caveats — see ADR 0004)
  shadow mapping, without matplotlib's flat/unshaded 3D look.
- Much lighter and faster to iterate on than a Blender/`bpy` pipeline would
  have been, at the cost of coarser control — PyVista's high-level API
  doesn't expose some VTK internals (shadow-map resolution/bias in
  particular; see ADR 0005).
- Dependency footprint is just `pyvista` (which pulls in `vtk`), installed
  into a local venv (ADR 0007).
