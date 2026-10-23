# FMsims — simulation progress

Phase 1 of `2_fm_emulator`: the N-body suite. Launch/post-process recipe: `../doc/sim_workflow.md`.
Conventions and paths: `../CLAUDE.md`.

## Project goal
A large suite of 400 Mpc/h, 128^3 dark-matter N-body realisations (Planck15, different seeds) giving
`delta(x,a)` and `deltadot(x,a)` on 128^3 meshes at ~20 random times per run, for training ML
emulators / forward models of large-scale structure. Validated against linear theory (power
spectrum, growth rate, continuity equation).

## Setup (decided 2026-03, after the code comparison)
- Code: **Gadget4** (`~/gadget4_development`), 2LPT ICs generated internally (`NGENIC=128`,
  `NGENIC_2LPT`, `NGENIC_USE_LEGACY_PHASEASSIGNMENT`), `PMGRID=256`, double precision, TreePM without
  time splitting. Config: `L400_n128_s40/Config.sh`.
- Cosmology: Omega_m 0.3089, Omega_L 0.6911, Omega_b 0.0486, h 0.6774, sigma8 0.8159, n_s 1.0 in the
  param file (input spectrum `~/gadget4_development/data/input_spectrum_PLANCK15.txt`, renormalised),
  **Neff = 0, no radiation** (this is what differs from MP-Gadget's full Planck15 and gives ~1% growth
  differences at high z; see `gadget4/compare_seed.ipynb`).
- Time range a = 0.01 to 1.0. Softening 0.1 Mpc/h, `MaxSizeTimestep` 0.008.
- Outputs per run: 20 random "midpoint" times a_i in [0.0111, 0.99] (`gen_outputs.py`, numpy seed
  73837, listed per run in `L400_n128_s40/all_avalues.txt`), each with a triplet
  (a_i - da, a_i, a_i + da), da = 0.01 sqrt(a). Snapshots are written in sorted order; the triplet
  order is restored with `reverse_index.txt`. 60 snapshots + 1 per run (3.6 GB).
- Mesh product (`create_delta_deltadot_mesh.py`): TSC + interlacing + compensation on 128^3,
  `delta = rho/rho_mean - 1` at the midpoint and `deltadot = (delta(a_right) - delta(a_left)) / (a_right - a_left)`
  (note: the code uses the right and *middle* snapshot of each triplet, `(delta2 - delta1)/(a2 - a1)`,
  i.e. a forward difference from the midpoint; see "open questions"). 40 `.npy` files (321 MB) per run
  in `run-XXXX/mesh/`; the a values are in `run-XXXX/output-a-list.txt`.
- Seeds: `L400_n128_s40/seeds.txt` (index, seed), 5000 lines, generated once from
  `numpy.random.default_rng(42)`; the FastPM suite uses the same list.

## Status (verified on scratch 2026-10-23)
| Item | State |
|---|---|
| Param + output lists (`run-0000`..`run-4999`) | Written on scratch for all 5000 |
| Gadget4 runs done | **run-0000..run-1999 (2000)**; batch 1 (0-1099) finished 2025-08-22, batch 2 (1100-1999, jobs 16684129-37) finished 2026-05-27 |
| Mesh post-processing | **2000 / 2000** done (batch 1 2025-08-27; batch 2 jobs 16684138-42 finished 2026-05-27) |
| Not run | run-2000..run-4999 (3000); param files exist, no output |
| Scratch usage | 7.8 TB in `~/scratch1/FMsims/L400_n128_s40` (3.6 GB snapshots + 0.32 GB mesh per run); Lustre is 89% full |
| Cost | ~22 h per 100-run job on one 96-core node; ~6 h per 200-run mesh job |
| FastPM comparison suite (`s-0000`..`s-0999`) | Ran 2025-08 with p2m for s-0000..s-0099, but **no `s-*` directories exist on scratch any more** (checked 2026-10-23): outputs were deleted or moved. Only the lua files + seeds remain (regenerable with `gen_luafile.py`). |
| Test runs (`gadget4/test_vel128` etc.) | Outputs still on scratch (`~/scratch1/FMsims/gadget4/`) |

## What was done (history)
1. **Code comparison, 2025-07..08 and 2026-03** (`gadget4/compare_seed.ipynb`): MP-Gadget vs
   Gadget4-2LPT vs linear theory (P_sim/P_lin, cross-correlation with ICs at several z). Input spectra
   (CLASS vs CAMB) agree. Neutrino/radiation treatment explains the ~1% growth offset. Decision:
   Gadget4 + 2LPT, Neff = 0.
2. **deltadot validation** (`gadget4/calc_ddelta_dt.ipynb`, `compare_dt_convergence.ipynb`, on
   `test_vel128`: 29-33 snapshots z = 2.5..0 with fine sampling near z ~ 0.4, 0.1, 0.03): deltadot from
   the continuity equation (velocity divergence; Fourier with 2/3 dealiasing, real-space FD, pmesh)
   agrees with the finite-difference deltadot on large scales; P_deltadot matches f^2 H^2 P on large
   scales; FD converges to a few % of linear theory with da ~ 0.01 sqrt(a). Decision: adaptive
   triplets, no velocity field needed. (`L400_n128_s40/test_da_values.ipynb` checked the triplet spacing.)
3. **Production batch 1** (run-0000..1099) + meshes, 2025-08.
4. **Production batch 2** (run-1100..1999) + meshes, 2026-05-26/27.
5. **FastPM suite** (`L400_n128_s40_fastpm/`): 5000 lua files, 40 uniform steps a = 0.05..1, 40
   output redshifts; 1000 runs + 100 p2m (CIC 128^3 and 2x downsampled 64^3 `.dat`) in 2025-08.
   Outputs now missing (see status). A systematic Gadget4-vs-FastPM comparison was never done.

## Failed / abandoned
- SPH-kernel velocity-divergence deltadot in `calc_ddelta_dt.ipynb`: never finished (undefined `z`),
  superseded by finite differencing.
- MP-Gadget (`mpgadget/`, `mpgadget-200/`, z_start 99 vs 199) and the stand-alone `gadget4-2lpt/`
  and `fastpm/` tests: only used for the comparison; not part of the pipeline.

## Next steps / open questions
- [ ] **Decide the suite size**: run run-2000..run-4999 (3000 more, ~30 node-jobs of 22 h, +11 TB) or
      stop at 2000. Scratch is at 89%; snapshots could be deleted after meshing (keep `mesh/`,
      `output-a-list.txt`, `param.txt`, `outputs.txt`, `reverse_index.txt`, `log`) to free ~3.3 GB/run.
      Ask the user before deleting anything.
- [ ] **deltadot finite-difference stencil**: `create_delta_deltadot_mesh.py` uses (a_mid, a_right), not
      the centred (a_left, a_right) pair that the triplet scheme and the notebooks assume. Check
      whether this is intended (one-sided, half the step) before training on `deltadot`; if the centred
      difference is wanted, recompute `mesh/` from the snapshots (snapshots are still on scratch).
- [ ] **Compensated TSC painting makes `delta` unphysical at late times** (found 2026-10-23):
      `create_delta_deltadot_mesh.py` paints with `compensated=True` (window deconvolution), which
      amplifies shot noise near the Nyquist scale. In the production meshes 14% of cells have
      delta < -1 at a = 0.52 and 29-31% at a > 0.9 (min delta -50 to -74); without compensation
      min delta = -1 exactly (checked on run-0000 snap at a = 0.906: comp+interlaced std 3.46, 20% of
      cells < -1; plain TSC std 1.81, 0%). Decide before training: repaint without compensation (or
      compensate only in Fourier space for power spectra), then recompute `mesh/` for all 2000 runs
      (~6 h per 200 runs). `deltadot` inherits the same noise.
- [ ] Spot-check production meshes against linear theory for a few runs (never done on production).
- Verified 2026-10-23: all 2000 runs have 40 mesh files and a clean `log`; 92 runs have 60 snapshots
  instead of 61 only because their last output time (~0.9996) coincides with TimeMax, so no separate
  a = 1 snapshot is written. Not a problem.
- [ ] Clarify what happened to the FastPM outputs; rerun only if the Gadget4-vs-FastPM comparison is
      still wanted.
- [ ] **git size**: the initial commit (pushed) holds 184 MB of `build/` objects, `Gadget4` binaries,
      the ewald table and checkpoints. They are untracked as of 2026-10-23 but stay in history until the
      initial commit is rewritten (`git commit --amend` on a squashed history + `git push --force`,
      user's call).

## Key paths
- Production outputs: `~/scratch1/FMsims/L400_n128_s40/run-XXXX/` (`output/`, `mesh/`, `output-a-list.txt`)
- Test outputs: `~/scratch1/FMsims/gadget4/test_vel128/output/`
- Notebooks: `gadget4/*.ipynb`, `L400_n128_s40/test_da_values.ipynb`, `L400_n128_s40_fastpm/test_p2m.ipynb`

---
*Last updated: 2026-10-23*
