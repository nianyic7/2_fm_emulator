---
project: FM emulator (N-body suite + ML emulators)
stage: next-steps-agreed   # running | analyzing | needs-input | blocked | next-steps-agreed | done
cluster: typhon
progress: "2000/5000 runs; phase-2 design agreed, no model code yet"
last_update: 2026-11-17T10:30
decision_needed: ""
blocked_on: ""
latest_plot: ""
deadlines: []
---
## Latest summary

Phase 1 (simulations): 2000 of 5000 Gadget4 runs finished with meshes (run-0000..run-1999, 7.8 TB on
scratch). Decided 2026-11-16: keep the compensated-TSC meshes and finite-difference deltadot as stored;
remaining 3000 runs deferred.
Phase 2 (models): design agreed 2026-11-17 (`doc/specs/2026-11-17-phase2-fm-emulator-design.md`):
flow-matching emulator with the physical N-body path, state phi = delta/D, velocity u = dphi/dD
(nonlinear residual), periodic 3D U-Net, forward + backward ODE rollout as metrics, h200 partition.
Next: implementation plan, then stencil check on run-0000 and a = 1 meshes, then env + package skeleton.
