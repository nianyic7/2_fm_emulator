# 2_fm_emulator — progress index

Two phases, each with its own progress file. Update the phase file, then add a dated line here.

| Phase | Status (2026-10-23) | File |
|---|---|---|
| Simulations | 2000 / 5000 Gadget4 runs done with meshes (run-0000..run-1999, 7.8 TB on scratch). FastPM comparison outputs lost. | `FMsims/PROGRESS.md` |
| Models + training | Not started. Decide data loader + first model. | `models/PROGRESS.md` (create with the first model work) |

## Session log
- **2026-10-23** — Repo bookkeeping: wrote `CLAUDE.md`, this index, `doc/sim_workflow.md`; brought
  `FMsims/PROGRESS.md` up to date (batch 2 finished 2026-05-27; FastPM outputs gone); added
  `.gitignore` and untracked build products, binaries, slurm logs, notebook checkpoints and the 5000
  generated FastPM lua files (regenerable). History still holds them: see the "git size" item in
  `FMsims/PROGRESS.md` next steps.
- **2026-05-26** — Batch 2 (run-1100..run-1999) and mesh jobs submitted (previous session, see
  `FMsims/PROGRESS.md`).
