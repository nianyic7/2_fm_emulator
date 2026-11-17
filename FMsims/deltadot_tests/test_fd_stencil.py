#!/usr/bin/env python
"""Design question (spec 5.1): does the stored forward stencil (a_mid, a_right) differ materially
from the centred (a_left, a_right) or backward (a_left, a_mid) one?  Decides whether the 2000
production meshes can be used as they are.

Data: production run-0000 snapshots (compensated + interlaced TSC, exactly as the pipeline).
For a few triplets spanning a: paint the three snapshots, form the three stencils, and compare
  P_stencil / P_centred,  r(stencil, centred),  P_stencil / P_lin  with P_lin = (f/a)^2 P(delta_mid)
Also checks that the forward stencil reproduces the stored mesh/deltadot file (pipeline sanity).

Pass criteria (k < 0.5 h/Mpc): |P_fwd/P_cen - 1| < 3 % and r(fwd, cen) > 0.99 -> keep stored meshes.
Plot: plots/fd_stencil_run0000.pdf
"""
import argparse, os
import numpy as np
from common import (PRODROOT, KMAX_TRAIN, KMAX_LIN, load_particles, paint_delta, growth, power,
                    cross_coefficient, summarize, band, style_k_axis, save, setup_logging, Timer, plt)

p = argparse.ArgumentParser()
p.add_argument("--run", default="run-0000")
p.add_argument("--triplets", type=int, nargs="*", default=[1, 5, 10, 15, 19],
               help="triplet indices (0..19) in output-a-list order")
args = p.parse_args()
log = setup_logging("fd_stencil_" + args.run)

rundir = os.path.join(PRODROOT, args.run)
alist = np.loadtxt(os.path.join(rundir, "output-a-list.txt")).reshape(-1, 3)
rev = np.loadtxt(os.path.join(rundir, "reverse_index.txt")).astype(int)
snaps = sorted(f for f in os.listdir(os.path.join(rundir, "output")) if f.startswith("snap_0"))
snaps = [os.path.join(rundir, "output", snaps[i]) for i in rev]     # triplet order

nt = len(args.triplets)
fig, ax = plt.subplots(nt, 3, figsize=(12, 2.9 * nt), squeeze=False)
worst_dp, worst_r, status = 0.0, 1.0, []
for row, t in enumerate(args.triplets):
    a0, a1, a2 = alist[t]
    d = []
    for s in range(3):
        with Timer(log, f"paint triplet {t} snap {s}"):
            a_s, pos, _ = load_particles(snaps[3 * t + s])
            assert abs(a_s - alist[t][s]) < 1e-6, (a_s, alist[t][s])
            d.append(paint_delta(pos, compensated=True, interlaced=True))
    fwd = (d[2] - d[1]) / (a2 - a1)          # stored definition
    bwd = (d[1] - d[0]) / (a1 - a0)
    cen = (d[2] - d[0]) / (a2 - a0)
    stored = np.load(os.path.join(rundir, "mesh", f"deltadot_N128_a{a1:.6f}.npy"))
    rel = np.abs(stored - fwd).max() / np.abs(fwd).max()
    log.info("triplet %d a=%.4f: max|stored - forward| / max|forward| = %.2e", t, a1, rel)
    D1, f1, _ = growth(a1)
    k, P_d = power(d[1])
    P_lin = (f1 / a1)**2 * P_d
    _, P_cen = power(cen)
    for name, fld in (("forward (stored)", fwd), ("backward", bwd), ("centred", cen)):
        _, r, P_s, _ = cross_coefficient(fld, cen)
        ax[row, 0].plot(k, P_s / P_cen, label=name)
        ax[row, 1].plot(k, r, label=name)
        ax[row, 2].plot(k, P_s / P_lin, label=name)
        if name.startswith("forward"):
            sel = band(k, 0, KMAX_TRAIN)
            dp = np.nanmax(np.abs(P_s[sel] / P_cen[sel] - 1))
            rmin = np.nanmin(r[sel])
            worst_dp, worst_r = max(worst_dp, dp), min(worst_r, rmin)
            summarize(f"triplet {t} fwd/cen P ratio", k, P_s / P_cen, KMAX_TRAIN, log)
            summarize(f"triplet {t} fwd P/Plin", k, P_s / P_lin, KMAX_LIN, log)
            status.append(f"a={a1:.3f}: max|P_fwd/P_cen-1|={dp*100:.1f}%, min r={rmin:.4f} (k<{KMAX_TRAIN}); "
                          f"stored==forward to {rel:.1e}")
    style_k_axis(ax[row, 0], r"$P_{\rm stencil}/P_{\rm centred}$")
    style_k_axis(ax[row, 1], r"$r({\rm stencil},\ {\rm centred})$")
    style_k_axis(ax[row, 2], r"$P(\dot\delta)/[(f/a)^2 P(\delta)]$", logy=True)
    ax[row, 0].axhline(1, color="0.6", lw=0.8); ax[row, 2].axhline(1, color="0.6", lw=0.8)
    ax[row, 0].set_ylim(0.9, 1.15); ax[row, 1].set_ylim(0.9, 1.005)
    ax[row, 0].set_title(rf"{args.run}, triplet {t}: $a=({a0:.4f}, {a1:.4f}, {a2:.4f})$", loc="left")
    ax[row, 0].legend(loc="upper left")
fig.tight_layout()
save(fig, f"fd_stencil_{args.run.replace('-', '')}", log)

ok = worst_dp < 0.03 and worst_r > 0.99
print(f"fd_stencil ({args.run}): forward vs centred, k<{KMAX_TRAIN}: max |dP/P| {worst_dp*100:.1f}%, "
      f"min r {worst_r:.4f} -> {'PASS: keep stored meshes' if ok else 'FAIL: consider repainting'}")
for s in status:
    print("  " + s)
raise SystemExit(0 if ok else 1)
