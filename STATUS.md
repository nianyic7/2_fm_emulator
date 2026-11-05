---
project: FM emulator (N-body suite + ML emulators)
stage: needs-input   # running | analyzing | needs-input | blocked | next-steps-agreed | done
cluster: typhon
progress: "2000/5000 runs"
last_update: 2026-10-23T17:38
decision_needed: "Before training: repaint meshes without compensated TSC (14-31% of cells have delta < -1 at a > 0.5)? Keep the one-sided deltadot stencil or switch to centred? Either fix repaints mesh/ for all 2000 runs. Also: run the remaining 3000 sims (+11 TB, scratch at 89%) or stop at 2000?"
blocked_on: ""
latest_plot: ""
deadlines: []
---
## Latest summary

Phase 1 (simulations): 2000 of 5000 Gadget4 runs are finished with meshes (run-0000..run-1999, 7.8 TB on
scratch); all meshes complete and logs clean as of 2026-10-23. FastPM comparison outputs are lost.
Phase 2 (models + training) has not started. See `PROGRESS.md` and `FMsims/PROGRESS.md`.
