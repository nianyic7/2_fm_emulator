# deltadot_tests — one script per design decision about `deltadot`

Scripted versions of the checks that used to live in `../gadget4/calc_ddelta_dt.ipynb`,
`../gadget4/compare_dt_convergence.ipynb` and `../L400_n128_s40/test_da_values.ipynb`, plus the
checks asked for in `doc/specs/2026-11-17-phase2-fm-emulator-design.md` (section 5.1).
Each script answers one question, prints <= 5 summary lines, writes a verbose log to
`test_logs/deltadot_tests/<name>.log` and one PDF to `plots/`.

Conventions: `deltadot = d(delta)/da` (per unit a, as in production), 400 Mpc/h, 128^3, TSC;
growth `D(a), f(a)` for the run cosmology (flat LCDM, Omega_m = 0.3089, no radiation) from
`common.growth`. Run inside `conda activate nbodykit-env`; everything runs on a login node in a
few minutes (each 128^3 painting of 2M particles takes ~5 s).

| Script | Question | Data | Plot |
|---|---|---|---|
| `test_da_triplet_spacing.py` | Is `da = 0.01 sqrt(a)` a sensible step? Linear-theory truncation bias of forward / backward / centred stencils | none | `da_triplet_spacing.pdf` |
| `test_fd_dt_convergence.py [--group z2 z0.4 z0.03] [--plain]` | How does FD `deltadot` depend on the span `Delta a`? (truncation vs noise) | `test_vel128` | `fd_dt_convergence_<group>.pdf` |
| `test_fd_stencil.py [--run run-0000] [--triplets ...]` | Spec 5.1: stored forward stencil (a_mid, a_right) vs backward vs centred; stored file == forward? | production `run-0000` snapshots + `mesh/` | `fd_stencil_run0000.pdf` |
| `test_fd_vs_continuity.py [--group ...]` | Is FD `deltadot` consistent with the exact continuity equation `-(1/a) div[(1+delta) v]`? | `test_vel128` | `fd_vs_continuity_<group>.pdf` |
| `test_tsc_compensation.py` | Record of what compensated+interlaced TSC does to `delta`, `deltadot` (kept by decision of 2026-11-16) | `run-0000` | `tsc_compensation_run0000.pdf` |

## Results (2026-11-17)

- **Stencil (spec 5.1): PASS, keep the stored meshes.** On run-0000 triplets at a = 0.057, 0.17,
  0.52, 0.75, 0.90 the forward stencil agrees with the centred one to `|dP/P| <= 2 %` and
  `r >= 0.9997` for k < 0.5 h/Mpc (and to Nyquist). The 1-2 % offset at late times is the
  expected O(da) truncation bias: in linear theory the forward difference underestimates `dD/da`
  by 0.3 % (a = 0.5) to 0.8 % (a = 1), i.e. 0.7-1.6 % in power, with the same sign at all k; the
  backward stencil is biased the other way. The stored `deltadot_*.npy` files equal the forward
  stencil bit for bit.
- **Span convergence: FD `deltadot` is converged for `Delta a` = 0.02 to 0.085 at z = 2, 0.4, 0.05.**
  `r(deltadot, deltadot_smallest span) > 0.998` to the Nyquist scale and `P/P_lin` on k < 0.15
  changes by < 0.3 % across spans. No sign of a noise floor at small spans (the test cannot go
  below 0.02 with these snapshots; at the production spacing ~0.01 the stencil test above shows the
  same agreement). "Larger spans are more robust" is therefore not supported by the data in this
  range; the only span effect is the truncation bias, which favours *smaller* spans.
- **Continuity equation:** FD and momentum-divergence `deltadot` agree with `r = 1.000` and
  `P_FD / P_cont = 1.003-1.004` on k < 0.15 at all three epochs. This validates the FD definition,
  the per-a units and `common.growth` (P(deltadot)/[(f/a)^2 P(delta)] -> 1.00 on the largest
  scales at a = 0.057 and 0.17; the 4 %, 13 %, 19 % excess at a = 0.33, 0.70, 0.95 for k < 0.15 is
  nonlinear growth of the time derivative, which sets in earlier than in `delta` itself).
- **Compensation (record only):** compensated+interlaced TSC vs plain: std of `delta` 1.80 vs 1.03
  (a = 0.52) and 3.45 vs 1.80 (a = 0.90); 14 % / 29 % of cells below -1; `P_comp/P_plain` rises from
  1.0 at k < 0.1 to 10 at Nyquist for both `delta` and `deltadot`; `r > 0.99` to k = 0.5 h/Mpc.
- `r(deltadot, delta)` (k < 0.5) is 0.87, 0.75, 0.71 at z = 2, 0.4, 0.05: the nonlinear part of
  `deltadot` that the emulator has to learn grows with time, as expected.
