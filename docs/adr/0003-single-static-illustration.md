# 0003 — Scope: single static illustration, not a parametrized generator

## Status

Accepted

## Context

Before writing any rendering code, the project's end goal was clarified
against three options: (a) a dataset generator producing many scenes with
varying camera angle / object position, e.g. for training or testing a
computer-vision model that estimates viewing angle; (b) a single, well-made
explainer image; (c) an interactive/exploratory tool with live camera and
object controls.

## Decision

Build toward (b): one fixed illustration, refined iteratively in place
(`render_scene.py` → `scene.png`), with scene parameters as plain module-
level constants rather than CLI args or a config surface.

## Consequences

- No parametrization/CLI/config work has been done — camera, room size,
  object shape and position, and light setup are all hardcoded constants at
  the top of `render_scene.py`, edited directly between iterations.
- Revisiting this decision (e.g. toward dataset generation) would mean
  promoting those constants to function parameters and adding a way to
  drive many renders — currently out of scope, tracked as future work in
  `AGENTS.md`.
