# Phase 2 design: flow-matching emulator of the density field (first version)

Date: 2026-11-17. Status: agreed with the user in the brainstorming session of 2026-11-16/17.
Scope of this spec: the first end-to-end version (data pipeline, U-Net velocity model, evaluation
including forward and backward rollout). Follow-ups are listed in section 9 and get their own specs.

## 1. Goal

Learn a velocity field `v(phi, D)` on the 128^3 mesh whose ODE flow maps the Gaussian initial density
field (growth factor `D ~ 0.013`, a = 0.01) to the a = 1 universe (`D = 1`) and back. Forward
integration is an emulator of structure formation; backward integration from an observed/simulated
a = 1 field is a reconstruction of the initial conditions, a Gaussian random field.

This is flow matching (Lipman et al. 2023) with a *physical* probability path: the N-body
trajectory `delta(x, a)` of each run is the path between the paired endpoints (initial Gaussian
field, final field), and the 20 random output times per run are the `t ~ U(0, 1)` samples at which
the velocity is regressed. The data in `FMsims/` were designed for this: each run stores
`delta(a_i)` and the finite-difference `deltadot(a_i) = d delta / da` at 20 random `a_i` in
[0.011, 0.99] (see `FMsims/PROGRESS.md`).

## 2. Decisions taken (and why)

| Decision | Choice | Reason |
|---|---|---|
| Mesh painting | Keep compensated TSC + interlacing as stored (cells with delta < -1 exist) | User decision 2026-11-16: the model should emulate the stored fields as produced; no repaint. |
| deltadot definition | Keep finite differencing from snapshots (no velocity-divergence) | Validated in `gadget4/compare_dt_convergence.ipynb`; user decision 2026-11-16. |
| FD stencil | Pending a quantitative check (section 5.1). Default: keep the stored (a_mid, a_right) forward difference | No recorded reason for the forward stencil; see section 8.1. |
| Model task | `phi(D) -> u = d phi / d D`, i.e. deltadot minus its linear-theory prediction | Nonlinear residual only; linear growth handled analytically (section 3). |
| Baseline | `deltadot_lin = f(a)/a * delta(x, a)` applied to the current field | Needs only stored meshes; backup option: subtract linear prediction only below a `k_lin` in Fourier space. |
| Time variable / state | `D(a)` and `phi = delta / D` | Flow starts at rest on the Gaussian field; most cosmology-independent form (section 8.2). |
| Architecture | Periodic 3D U-Net first; FNO and others later | Proven for field-to-field N-body maps (He et al. 2019; Jamieson et al. 2023). |
| Metrics | Spectral `T(k)`, `r(k)` of `u`, plus forward and backward rollout | Section 7. |
| Compute | `h200` partition (8 H200, 2 TB RAM/node), data staged to node-local disk; scripts partition-agnostic so `apollo` works too | The 670 GB mesh set fits in RAM; I/O, not FLOPs, is the likely bottleneck. |
| Gaussian endpoint | Earliest stored mesh `delta(a_first)/D(a_first)` now; regenerate exact a = 0.01 2LPT fields from the seeds later | No IC snapshot exists (first snapshot per run is at a random a, median 0.03). |
| Remaining 3000 sims | Later, only if the model is data-limited | Lustre at 83 %, +3.9 GB per run. |
| Work style | Tutorial-style: agent writes boilerplate and a written explanation of every step; user writes the ML core (dataset, U-Net, loss, training loop) with guidance and review | User wants to learn by doing (first astro + DL project). |

## 3. Parametrisation

With `' = d/da`, `D(a)` the linear growth factor normalised to `D(1) = 1`, `f = d ln D / d ln a`, and
`D' = f D / a`:

```
phi = delta / D
u   = d phi / dD = (delta' - (f/a) delta) / (D D') = a (delta' - (f/a) delta) / (f D^2)
```

In linear theory `delta' = (f/a) delta`, so `u = 0` exactly: the network learns only the nonlinear
coupling, and the flow starts at rest on the Gaussian field. The stored `deltadot` (per unit a) is
converted to `u` in the data loader; no repainting is needed. The conditioning variable fed to the
network is `D` (extensible to `[D, Omega_m, sigma_8]`, section 8.2).

`D(a)` and `f(a)` must match what Gadget4 integrated: Planck15 with `Omega_m = 0.3089`,
`Omega_Lambda = 0.6911`, **no radiation, Neff = 0** (see `FMsims/PROGRESS.md`). They are obtained
by integrating the linear growth ODE with these two parameters only, and verified against the
simulations on linear scales (a mismatch leaves a linear residual in `u` at low k; section 7).

## 4. Repository layout and environment

```
models/
  PROGRESS.md          phase-2 progress file
  doc/                 one tutorial page per step (concept, equations, what the code does, what to check)
  fmemu/               installable package
    growth.py          D(a), f(a), dD/da for the run cosmology (growth ODE, Omega_m + Omega_Lambda only)
    data.py            run index, loading, (phi, u) conversion, periodic 64^3 crops, augmentation, split
    unet.py            periodic 3D U-Net with FiLM conditioning on D
    train.py           training loop, logging, checkpoints
    evaluate.py        T(k), r(k) per D bin; comparison against the u = 0 baseline
    ode.py             fixed-step RK4 integration of phi in D on the full 128^3 box, forward and backward
  configs/             YAML run configs (tracked)
  slurm/               GPU job scripts (stage data to $TMPDIR, run train/evaluate)
  tests/               tests first; <= 5 lines of stdout on success, verbose output to test_logs/
```

Environment: a new conda env (`fm-torch`) with PyTorch + CUDA for everything under `models/`.
Painting scripts stay in `FMsims/` and in `nbodykit-env`. Checkpoints, logs and metrics go to
`~/scratch1/FMsims/models/<run-name>/`; configs and code to git.

## 5. Data products to add (in `FMsims/`, nbodykit env)

### 5.1 Stencil check on run-0000
Paint, for two triplets of run-0000 (one at a ~ 0.5, one at a > 0.9), the forward difference
`(delta(a_right) - delta(a_mid)) / (a_right - a_mid)` as stored and the centred difference
`(delta(a_right) - delta(a_left)) / (a_right - a_left)`. Compare `P(k)` and `r(k)` of the two, and
`P(deltadot)` against `(f/a)^2 P(delta)` on large scales (the production spot-check against linear
theory that was never done). Decision rule: if the two stencils agree to within a few per cent in
`P(k)` and `r(k) > 0.99` to `k ~ 0.5 h/Mpc`, keep the stored meshes; otherwise recompute `deltadot`
for all 2000 runs with the centred stencil (~60 h of mesh jobs; snapshots are on scratch).

### 5.2 a = 1 mesh for every run
`delta_N128_a1.000000.npy` in each `run-XXXX/mesh/`, painted from the last snapshot with the same
painter and settings (compensated TSC, interlaced). 92 runs end at a ~ 0.9996 instead of 1.0; use
that snapshot and record its a. One painting per run, well under an hour for 2000 runs on one node.

## 6. Data pipeline (`data.py`)

- **Index**: table of (run, a_mid, D, path_delta, path_deltadot) built from `output-a-list.txt` of
  each run; cached as a small file.
- **Sample**: one (run, a) pair -> `phi` and `u` on 128^3; random periodic 64^3 crop; random flips and
  axis permutations (the 48-element cubic group). Inference runs on the full 128^3 box, which
  periodic padding allows.
- **Normalisation**: `phi` has a time-independent scale by construction. `u` is divided by a scale
  `sigma_u(D)` measured once on the training set in D bins and stored with the config.
- **Split by run**: `run-1900..run-1999` test (held out permanently), `run-1800..run-1899` validation,
  training grows from 100 runs (`run-0000..run-0099`) to the remaining 1800.
- **Staging**: slurm job copies the needed runs' `mesh/` to node-local disk (`TmpDisk` 3 TB on h200
  nodes) before training; loader reads `.npy` with memory mapping.

## 7. Model, training and evaluation

**Model**: periodic 3D U-Net, 2-3 resolution levels, residual blocks, 1 input channel (`phi`),
1 output channel (`u`), FiLM scale/shift from an embedding of the conditioning vector `[D]` at each
level. Reference design: map2map (Li) and Jamieson et al. 2023, written out in a few hundred lines
rather than imported, so that the model is swappable (FNO later).

**Training**: MSE on normalised `u`; AdamW, cosine schedule, mixed precision; single GPU first,
multi-GPU only if the 2000-run training needs it.

**Evaluation**, always next to the linear baseline `u = 0`:
1. *Velocity*: transfer function `T(k) = sqrt(P_pred / P_true)` and cross-correlation `r(k)` of
   predicted vs true `u`, in bins of D. First target: `r > 0.95` and `|T - 1| < 5 %` to
   `k ~ 0.5 h/Mpc`.
2. *Forward rollout*: integrate `phi` from the earliest mesh of a test run to `D = 1` (fixed-step RK4
   in D, full 128^3), compare `delta(a = 1)` with the painted a = 1 mesh via `P(k)` and `r(k)`.
3. *Backward rollout*: integrate from the a = 1 mesh back to the D of the earliest mesh, compare with
   the stored field. `r(k)` of this reconstruction is the headline number for the project goal; it
   will degrade at high k where shell crossing has erased information, and the first result
   establishes where.

## 8. Reasoning notes

### 8.1 Why the stored deltadot uses (a_mid, a_right)
No reason is recorded. The validation notebook `gadget4/compare_dt_convergence.ipynb` used
*centred* snapshot pairs around the reference snapshot, plain (uncompensated) TSC, and
differentiated with respect to cosmic time in Gyr^-1; the production script
`create_delta_deltadot_mesh.py` uses the (mid, right) pair, compensated TSC, and d/da. The only
principled argument for the forward stencil is discrete consistency with time stepping:
`delta(a_mid) + (a_right - a_mid) deltadot = delta(a_right)` exactly, so a forward-Euler step of
the learned velocity reproduces the next snapshot. For the *instantaneous* derivative that an ODE
solver wants, the centred difference is the better estimate (error O(da^2) vs O(da), the forward
bias being ~ (da/2) delta''). Section 5.1 quantifies the difference before training.

### 8.2 Cosmology dependence and generalisation
The suite has a single cosmology (Planck15, Neff = 0), so any model trained on it is a
fixed-cosmology emulator, whether it learns the full `deltadot` or the residual. Learning the
residual in the (D, phi) parametrisation does not reduce generality; it is the most
cosmology-independent formulation available:

- *Linear growth* `D(a), f(a)` is the strongest cosmology dependence and is removed from the network
  entirely. For a new cosmology it is recomputed analytically; the reconstruction runs in D and
  `a(D)` only labels the time axis.
- *Nonlinear mode coupling in D-time* is almost cosmology-independent for LCDM: the Euler equation in
  D-time carries the factor `3 Omega_m(a) / (2 f(a)^2) ~ 3/2`, i.e. the Einstein-de Sitter
  approximation under which perturbation-theory kernels are universal (Bernardeau et al. 2002) and
  on which COLA (Tassev et al. 2013) and FastPM (Feng et al. 2016) rely. NECOLA (Kaushal et al.
  2022), a learned correction to COLA trained at one cosmology, transferred to other cosmologies
  without retraining for this reason. Cosmology rescaling (Angulo & White 2010) exploits the same
  near-universality.
- *Initial power spectrum shape and amplitude* enter only through the field `phi` itself (the
  dynamics are local in the field); the network needs no `P(k)` input. What is not guaranteed is
  behaviour under distribution shift (very different `sigma_8` or shape). This is an empirical
  question and cheap to test with a few dozen runs at other cosmologies.

For the reconstruction goal a fixed-cosmology forward model is the standard setting (e.g. BORG,
Jasche & Wandelt 2013, assumes a cosmology for the forward model and for the Gaussian prior
`P_lin(k)`). Marginalising over cosmology requires a cosmology-conditioned emulator trained on a
suite that varies `Omega_m`, `sigma_8` (Jamieson et al. 2023 feed `Omega_m` as an input).

Consequences: (i) the conditioning vector is `[D]` now, built to be extended to
`[D, Omega_m, sigma_8]`; (ii) follow-up: a small generalisation test with a handful of runs at two or
three other cosmologies, evaluated without retraining. If transfer is poor, the next suite varies
cosmology and the network gets the parameters as input; the 2000 Planck15 runs remain the anchor.

### 8.3 Risks
- Forward-difference bias in `u` at late times (5.1).
- Growth-factor mismatch with Gadget4 leaves a linear residual at low k (caught by metric 7.1).
- Backward integration amplifies small-scale errors (measured by 7.3, not hidden).
- Compensated-TSC noise is inherited by `u`; the model must learn to emulate it as part of the data.

## 9. Follow-ups (separate specs)
1. Regenerate the exact 2LPT field at a = 0.01 for all runs from the seeds (Gadget4 NGENIC) and
   paint it; replace the earliest-mesh endpoint.
2. Fourier Neural Operator and other architectures (model is swappable by design).
3. Standard straight-path flow-matching baseline between the same endpoints
   (`x_t = (1-t) x_0 + t x_1`, `v = x_1 - x_0`) vs the physical path.
4. Cosmology generalisation test (8.2) and, if needed, a varied-cosmology suite with parameter
   conditioning.
5. Reconstruction with a Gaussian prior at scale; decide on the remaining 3000 Planck15 runs.

## References
- Lipman, Chen, Ben-Hamu, Nickel, Le 2023, *Flow Matching for Generative Modeling*, ICLR 2023, arXiv:2210.02747.
- Jamieson, Li, Alves de Oliveira, Villaescusa-Navarro, Ho, Spergel 2023, *Field-level Neural Network Emulator for Cosmological N-body Simulations*, ApJ 952, 145, arXiv:2206.04594.
- He, Li, Feng, Ho, Ravanbakhsh, Chen, Poczos 2019, *Learning to predict the cosmological structure formation* (D3M), PNAS 116, 13825, arXiv:1811.06533.
- Li et al., map2map: https://github.com/eelregit/map2map (periodic 3D U-Net / V-Net for field-to-field N-body emulation).
- Kaushal, Villaescusa-Navarro, Giusarma, Li, Hawry, Reyes 2022, *NECOLA: Towards a Universal Field-level Cosmological Emulator*, ApJ 930, 115, arXiv:2111.02441.
- Tassev, Zaldarriaga, Eisenstein 2013, *Solving large scale structure in ten easy steps with COLA*, JCAP 06, 036, arXiv:1301.0322.
- Feng, Chu, Seljak, McDonald 2016, *FastPM: a new scheme for fast simulations of dark matter and haloes*, MNRAS 463, 2273, arXiv:1603.00476.
- Angulo & White 2010, *One simulation to fit them all - changing the background parameters of a cosmological N-body simulation*, MNRAS 405, 143, arXiv:0912.4277.
- Bernardeau, Colombi, Gaztanaga, Scoccimarro 2002, *Large-scale structure of the Universe and cosmological perturbation theory*, Phys. Rep. 367, 1, arXiv:astro-ph/0112551.
- Jasche & Wandelt 2013, *Bayesian physical reconstruction of initial conditions from large-scale structure surveys* (BORG), MNRAS 432, 894, arXiv:1203.3639.
