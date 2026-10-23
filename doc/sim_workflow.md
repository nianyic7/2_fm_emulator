# Simulation workflow (FMsims/L400_n128_s40)

How a batch of production runs is launched, post-processed and recorded. Status: `FMsims/PROGRESS.md`.

## 1. One-time setup (already done)
1. `seeds.txt` (5000 seeds) and `param_template.txt` exist. `python gen_paramfile.py` writes
   `~/scratch1/FMsims/L400_n128_s40/run-XXXX/param.txt` for all 5000 (seed substituted).
2. `python gen_outputs.py` writes `outputs.txt` (61 sorted a values = 20 triplets + ...) and
   `reverse_index.txt` per run, and `all_avalues.txt` (the 20 midpoints per run) here. It is seeded;
   rerunning it reproduces the same lists. Do not rerun with a different seed: completed runs would no
   longer match `all_avalues.txt`.
3. Compile: `bash make.sh` (builds `Gadget4` here from `~/gadget4_development` with this `Config.sh`).
   The binary is not in git; rebuild after a fresh clone.

## 2. Launching a batch of 100 runs
- `run-template.sh` runs `n1 <= i < n2` sequentially on one node (96 MPI tasks, 30 h walltime, 100
  runs take ~22 h). `set-run.sh` (or `set-run-1100-2000.sh`) copies it to `run-NNNN.sh` with the job
  name `rNNNN` and `n1/n2` filled. Edit the `seq` range in `set-run.sh` for new batches.
- Each run writes to `~/scratch1/FMsims/L400_n128_s40/run-XXXX/` (`log`, `output/snap_*.hdf5`,
  `param.txt-usedvalues`). The ewald table is copied in from here (Gadget4 regenerates it if missing).
- Submit from this directory: `sbatch run-NNNN.sh`. Stdout: `slurm-rNNNN.out`.
- Check: `grep -c Running slurm-rNNNN.out` (should reach 100 then `Done!`),
  `ls -d ~/scratch1/FMsims/L400_n128_s40/run-*/output | wc -l`.

## 3. Mesh post-processing (delta, deltadot)
- `template_mesh.sh` -> `genmesh-NNNN.sh` (200 runs per job, conda `nbodykit-env`, 1 task, ~6 h).
  Submit with a dependency on the two sim jobs it covers:
  `sbatch --dependency=afterok:<job_a>:<job_b> genmesh-NNNN.sh`.
- Runs `create_delta_deltadot_mesh.py --root ... --Lbox 400. --Nmesh 128 --runname run-XXXX` and
  writes `run-XXXX/mesh/{delta,deltadot}_N128_a<mid>.npy` (40 files) and `run-XXXX/output-a-list.txt`.
- Done marker: `output-a-list.txt` exists; `ls ~/scratch1/FMsims/L400_n128_s40/run-*/output-a-list.txt | wc -l`.

## 4. Record keeping
- After submitting: job IDs, run range and date in `FMsims/PROGRESS.md` (status table + history).
- After completion: verify with the counts above, update the table, commit launch scripts and the
  progress files together.
- Scratch is shared and nearly full (89%, 2026-10-23); check `df -h ~/scratch1` before a batch
  (~3.9 GB per run).

## 5. FastPM suite (dormant)
`L400_n128_s40_fastpm/`: `python gen_luafile.py` regenerates `paramfile/s-XXXX.lua` + `seeds.txt`
(seed 42, identical to the Gadget4 seeds); `run-NNNN.sh` runs a range; `p2m-NNNN.sh` +
`part2mesh.py` paints CIC meshes. Outputs went to `~/scratch1/FMsims/L400_n128_s40/s-XXXX/` and are
gone as of 2026-10-23.
