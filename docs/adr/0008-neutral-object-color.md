# 0008 — Floating object recolored to near-white

## Status

Accepted

## Context

The wedge cylinder (ADR 0006) was originally colored a saturated blue
(`#3f6fb0`), chosen when the scene had a single neutral studio lightkit and
no colored lights. Once the three lights were each given a distinct
saturated color — amber (floor), blue (back wall), rose (side wall) — the
object's own blue competed with the lighting rather than showing it: a blue
object under blue, amber, and rose light doesn't visibly read as "reflecting
three different lights," it just looks blue with some tinting at the edges.

## Decision

Recolor the object to a light gray, near-white (`#f2f0ea`), keeping its
existing specular/diffuse/ambient shading values unchanged.

## Consequences

- The object now visibly picks up each light's color where that light
  dominates a given patch of surface (rose on the side facing the rose
  wall-light, warm amber underneath from the floor light, cool blue on top
  from the back-wall light) — reinforcing the scene's point that one object
  presents a different true "color"/shape to each observer.
- Supersedes the color choice implicit in ADR 0006 (and mentioned in ADR
  0004's context); no other part of those decisions changes.
