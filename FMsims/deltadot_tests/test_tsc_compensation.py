#!/usr/bin/env python
"""Design record: what does the compensated (window-deconvolved) + interlaced TSC painting do to
delta and deltadot compared with plain TSC?  The user decided (2026-11-16) to keep the compensated
meshes; this script records the consequence (cells with delta < -1, extra small-scale power).

Data: production run-0000, two triplets (a ~ 0.5 and a ~ 0.9).
Plot: plots/tsc_compensation_run0000.pdf
"""
import argparse, os
import numpy as np
from common import (PRODROOT, KMAX_TRAIN, load_particles, paint_delta, power, cross_coefficient,
                    style_k_axis, save, setup_logging, Timer, plt)

p = argparse.ArgumentParser()
p.add_argument("--run", default="run-0000")
p.add_argument("--triplets", type=int, nargs="*", default=[10, 19])
args = p.parse_args()
log = setup_logging("tsc_compensation_" + args.run)
rundir = os.path.join(PRODROOT, args.run)
alist = np.loadtxt(os.path.join(rundir, "output-a-list.txt")).reshape(-1, 3)
rev = np.loadtxt(os.path.join(rundir, "reverse_index.txt")).astype(int)
snaps = sorted(f for f in os.listdir(os.path.join(rundir, "output")) if f.startswith("snap_0"))
snaps = [os.path.join(rundir, "output", snaps[i]) for i in rev]

nt = len(args.triplets)
fig, ax = plt.subplots(nt, 3, figsize=(12, 3.0 * nt), squeeze=False)
lines = []
for row, t in enumerate(args.triplets):
    a0, a1, a2 = alist[t]
    dd = {}
    for name, flag in (("plain TSC", False), ("compensated+interlaced", True)):
        d = []
        for s in (1, 2):
            with Timer(log, f"paint t{t} s{s} {name}"):
                d.append(paint_delta(load_particles(snaps[3 * t + s])[1], compensated=flag, interlaced=flag))
        dd[name] = (d[0], (d[1] - d[0]) / (a2 - a1))
        frac = (d[0] < -1).mean()
        log.info("t%d a=%.4f %s: min delta %.2f, std %.3f, frac(delta<-1) %.3f", t, a1, name, d[0].min(), d[0].std(), frac)
        lines.append(f"a={a1:.3f} {name}: std {d[0].std():.2f}, min {d[0].min():.1f}, cells<-1: {frac*100:.1f}%")
    bins = np.linspace(-3, 6, 91)
    for name, (d, _) in dd.items():
        ax[row, 0].hist(d.ravel(), bins=bins, histtype="step", label=name, density=True)
    ax[row, 0].axvline(-1, color="0.5", ls="--", lw=0.8)
    ax[row, 0].set(xlabel=r"$\delta$", ylabel="pdf", yscale="log", title=rf"{args.run} $a={a1:.4f}$")
    ax[row, 0].legend()
    k, Pp = power(dd["plain TSC"][0]); _, Pc = power(dd["compensated+interlaced"][0])
    _, Ppd = power(dd["plain TSC"][1]); _, Pcd = power(dd["compensated+interlaced"][1])
    ax[row, 1].plot(k, Pc / Pp, label=r"$\delta$")
    ax[row, 1].plot(k, Pcd / Ppd, label=r"$\dot\delta$")
    style_k_axis(ax[row, 1], r"$P_{\rm compensated}/P_{\rm plain}$", logy=True); ax[row, 1].legend()
    _, r_d, _, _ = cross_coefficient(dd["plain TSC"][0], dd["compensated+interlaced"][0])
    _, r_dd, _, _ = cross_coefficient(dd["plain TSC"][1], dd["compensated+interlaced"][1])
    ax[row, 2].plot(k, r_d, label=r"$\delta$"); ax[row, 2].plot(k, r_dd, label=r"$\dot\delta$")
    style_k_axis(ax[row, 2], r"$r({\rm plain},\ {\rm compensated})$"); ax[row, 2].set_ylim(0.8, 1.01); ax[row, 2].legend()
fig.tight_layout()
save(fig, f"tsc_compensation_{args.run.replace('-', '')}", log)
print("tsc_compensation: see plots/tsc_compensation_run0000.pdf")
for l in lines:
    print("  " + l)
