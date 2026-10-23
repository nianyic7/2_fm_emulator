# 2_fm_emulator — N-body simulation suite + ML emulators of large-scale structure

Goal: build a large suite of dark-matter-only N-body realisations (density `delta(x,a)` and its time
derivative `deltadot(x,a)` on 128^3 meshes) and train ML emulators / forward models on them. Two
phases, each with its own progress file:

| Phase | Where | Progress file |
|---|---|---|
| 1. Simulations (launch, post-process, validate) | `FMsims/` | `FMsims/PROGRESS.md` |
| 2. Models + training (not started) | `models/` (to be created) | `models/PROGRESS.md` (to be created) |

`PROGRESS.md` at the top level is only an index + session log pointing at those two. Read it first,
then the phase file for the phase you are working on. How to launch/post-process a batch:
`doc/sim_workflow.md`.

## Cluster and paths (Typhon, IAS)
- Home `/home/nianyic`; scratch `~/scratch1` -> `/mnt/lustre/user/nianyic` (Lustre, no backup; shared
  filesystem 89% full as of 2026-10-23). Slurm partition `typhon`, 96 cores / 384 GB per node.
- **Simulation outputs are never in git.** Production outputs: `~/scratch1/FMsims/L400_n128_s40/run-XXXX/`
  (`output/snap_*.hdf5`, `mesh/{delta,deltadot}_N128_a*.npy`, `output-a-list.txt`, `reverse_index.txt`).
  Test outputs: `~/scratch1/FMsims/gadget4/{test_vel128,test_vel64,2lpt}/`.
- Codes: Gadget4 `~/gadget4_development` (production code; module script `module_ias.sh` there),
  FastPM `~/fastpm`, MP-Gadget `~/MP-Gadget` (the last two were only used for the code comparison).
- Python: conda env `nbodykit-env` for all mesh/post-processing scripts (nbodykit, h5py, bigfile).
  Scripts import `load_basics` from `~/utils` (on `PYTHONPATH` via `~/.bashrc`).
- Git remote `origin` = git@github.com:nianyic7/2_fm_emulator.git (`main`).

## Layout
- `FMsims/L400_n128_s40/` — **production Gadget4 suite** (400 Mpc/h, 128^3, 2LPT ICs, Planck15, 5000 seeds).
  Launch scripts (`run-NNNN.sh`, `genmesh-NNNN.sh`, their templates and `set-run*.sh`), `Config.sh`,
  `param_template.txt`, generators (`gen_paramfile.py`, `gen_outputs.py`), seeds (`seeds.txt`),
  mesh post-processing (`create_delta_deltadot_mesh.py`), `all_avalues.txt` (the 20 output a's per run).
- `FMsims/L400_n128_s40_fastpm/` — FastPM comparison suite (same seeds; generator `gen_luafile.py`,
  `template.lua`, particle-to-mesh `part2mesh.py`). Outputs no longer on scratch (see FMsims/PROGRESS.md).
- `FMsims/gadget4/` — validation notebooks (`compare_seed`, `calc_ddelta_dt`, `compare_dt_convergence`)
  and the test runs they use (`test_vel128` is the reference), plus `linear_density*.npy` inputs.
- `FMsims/gadget4-2lpt/`, `FMsims/mpgadget*/`, `FMsims/fastpm/` — one-off test runs from the
  code-comparison phase (2025-07/08). Kept for the record; not used by the production pipeline.
- `doc/` — workflow notes. `test_logs/` — verbose test output (gitignored).

## Conventions
- Each run dir on scratch is self-describing (`param.txt`, `outputs.txt`, `reverse_index.txt`); the
  launch scripts in git are the record of *how* it was run. Keep them tracked; keep `build/`, binaries,
  `slurm-*.out`, logs and notebook checkpoints out of git (`.gitignore`).
- Batches: one slurm job = 100 sims (`run-NNNN.sh`, NNNN = first run index) or 200 mesh jobs
  (`genmesh-NNNN.sh`). Make new ones from the templates with `set-run.sh` / `set-run-1100-2000.sh`.
- Numbering: Gadget4 runs are `run-0000`..`run-4999`, FastPM runs `s-0000`..`s-4999`; index i uses seed
  `seeds.txt[i]` in both suites.
- Git: commit after meaningful progress; update `PROGRESS.md` (index) and the phase progress file in
  the same commit. Ask before force-pushing or rewriting history.
- Ask when uncertain about physics/numerics parameters, run scope (how many more runs), or output
  layout; do not assume. Routine script mechanics need no question.
- Tests (phase 2): tests before implementation, <=5 lines of stdout on success, verbose output to
  `test_logs/`, no fudge factors.
