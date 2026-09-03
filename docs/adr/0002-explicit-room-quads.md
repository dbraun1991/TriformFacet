# 0002 — Room surfaces built as explicit quads, not `pv.Plane`

## Status

Accepted

## Context

The room's floor and two walls were first built with
`pv.Plane(center=..., direction=..., i_size=..., j_size=...)`. The rendered
walls didn't meet at their shared corner edge — a visible gap appeared where
the floor/wall-1/wall-2 corner should have been sealed.

Inspecting the actual mesh bounds confirmed the cause: for a given
`direction`, `pv.Plane`'s automatic choice of in-plane `i`/`j` basis vectors
did not match the assumption that `i_size` maps to one specific world axis
and `j_size` to another. The extents came out swapped/offset relative to
what the center + sizes implied.

## Decision

Replace `pv.Plane` for the room surfaces with a small helper —
`quad(p0, p1, p2, p3)` — that builds an explicit 4-point `pv.PolyData` quad
from four literal corner coordinates, with `compute_normals()` called
explicitly afterward. The floor and both walls are now defined by their
exact corner points, so the shared corner edge is guaranteed to coincide
(not just approximately match).

## Consequences

- No ambiguity about which axis a size parameter maps to — the corners are
  literal.
- Slightly more verbose than a one-line `pv.Plane` call, but the room's
  three surfaces now share the corner edge `(0, 0, 0..HEIGHT)` exactly, with
  zero-tolerance floating point equality (same literal coordinates, not
  independently-computed ones).
