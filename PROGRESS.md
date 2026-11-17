# 2_fm_emulator — progress index

Two phases, each with its own progress file. Update the phase file, then add a dated line here.

| Phase | Status (2026-11-17) | File |
|---|---|---|
| Simulations | 2000 / 5000 Gadget4 runs done with meshes (run-0000..run-1999, 7.8 TB on scratch). FastPM comparison outputs lost. | `FMsims/PROGRESS.md` |
| Models + training | Design agreed 2026-11-17 (`doc/specs/2026-11-17-phase2-fm-emulator-design.md`): flow-matching emulator, `phi = delta/D -> u = dphi/dD`, periodic 3D U-Net, forward + backward rollout. No code yet. | `models/PROGRESS.md` |

## Session log
- **2026-11-16/17** — Phase-2 brainstorming. Decisions: keep the compensated-TSC meshes and the
  finite-difference `deltadot` as stored (no repaint); model = flow-matching velocity field in the
  (D, phi = delta/D) parametrisation, i.e. `deltadot` minus its linear prediction; periodic 3D U-Net
  first; metrics T(k), r(k) plus forward and backward ODE rollouts; h200 partition; Gaussian endpoint
  = earliest stored mesh for now (exact a = 0.01 ICs regenerated later); remaining 3000 sims deferred.
  Cosmology-generalisation reasoning and references recorded in the spec (section 8.2). Open: the
  (a_mid, a_right) stencil has no recorded reason; to be quantified on run-0000 before training.
- **2026-10-23 (later)** — Status review of the 2000 finished runs: all meshes complete, logs clean.
  Two data-quality questions before training, both in `FMsims/PROGRESS.md` next steps: the
  compensated TSC painting leaves 14-31% of cells with delta < -1 at a > 0.5, and `deltadot` is a
  one-sided (mid, right) difference. Both need a user decision; fixing either means repainting
  `mesh/` for all 2000 runs from the snapshots (still on scratch).
- **2026-10-23** — Repo bookkeeping: wrote `CLAUDE.md`, this index, `doc/sim_workflow.md`; brought
  `FMsims/PROGRESS.md` up to date (batch 2 finished 2026-05-27; FastPM outputs gone); added
  `.gitignore` and untracked build products, binaries, slurm logs, notebook checkpoints and the 5000
  generated FastPM lua files (regenerable). History still holds them: see the "git size" item in
  `FMsims/PROGRESS.md` next steps.
- **2026-05-26** — Batch 2 (run-1100..run-1999) and mesh jobs submitted (previous session, see
  `FMsims/PROGRESS.md`).
