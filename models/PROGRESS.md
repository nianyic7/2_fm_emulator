# models — phase 2 progress (flow-matching emulator)

Design spec: `../doc/specs/2026-11-17-phase2-fm-emulator-design.md` (read it first). Conventions and
paths: `../CLAUDE.md`. Work style for this phase: tutorial-style, the user writes the ML core
(dataset, U-Net, loss, training loop) with guidance; the agent writes boilerplate and documents every
step in `doc/`.

## Goal
Velocity field `v(phi, D)` on the 128^3 mesh whose ODE flow maps the Gaussian initial field to the
a = 1 universe and back (reconstruction of initial conditions). Flow matching with the physical
N-body path; `phi = delta / D`, `u = d phi / dD` = nonlinear residual of the stored `deltadot`.

## Status (2026-11-17)
Spec agreed. No code yet. Next: implementation plan (writing-plans), then step by step.

## Next steps
- [ ] Implementation plan from the spec.
- [ ] Stencil check on run-0000 (spec 5.1) and a = 1 meshes for all runs (spec 5.2), in `FMsims/`.
- [ ] `fm-torch` conda env; `fmemu` package skeleton with tests; `growth.py` verified against the sims.
- [ ] Data pipeline, U-Net, training on 100 runs, evaluation, rollouts.

## Failed / abandoned
(none yet)

---
*Last updated: 2026-11-17*
