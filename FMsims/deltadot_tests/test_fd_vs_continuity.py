#!/usr/bin/env python
"""Design question: is the finite-difference deltadot consistent with the exact continuity equation
d(delta)/dt = -(1/a) div[(1+delta) v] evaluated from the particle velocities?  Independent check of
the FD definition (and of the a-derivative units).  Converts calc_ddelta_dt.ipynb.

Data: test_vel128.  At a reference snapshot: centred FD from its two neighbours vs the momentum
divergence (TSC-painted (1+delta)v, spectral divergence) at the reference itself.
Metrics vs k: r(FD, continuity), P_FD / P_cont, both / P_lin, r with delta.
Plots: plots/fd_vs_continuity_<group>.pdf
"""
import argparse
import numpy as np
from common import (TESTRUN, KMAX_TRAIN, KMAX_LIN, snapshot_list, load_particles, paint_delta,
                    paint_momentum, deltadot_continuity, growth, power, cross_coefficient, summarize,
                    style_k_axis, save, setup_logging, Timer, plt)

REFS = {"z2": 7, "z0.4": 15, "z0.03": 23}
p = argparse.ArgumentParser()
p.add_argument("--group", choices=list(REFS), nargs="*", default=list(REFS))
p.add_argument("--plain", action="store_true")
args = p.parse_args()
comp = not args.plain
log = setup_logging("fd_vs_continuity")
files, alist = snapshot_list(TESTRUN)

status = []
for g in args.group:
    ref = REFS[g]
    a_ref = alist[ref]
    with Timer(log, f"[{g}] paint ref + neighbours"):
        _, pos, vel = load_particles(files[ref], velocities=True)
        d_ref = paint_delta(pos, compensated=comp, interlaced=comp)
        mom = paint_momentum(pos, vel, compensated=comp, interlaced=comp)
        d_m = paint_delta(load_particles(files[ref - 1])[1], compensated=comp, interlaced=comp)
        d_p = paint_delta(load_particles(files[ref + 1])[1], compensated=comp, interlaced=comp)
    fd = (d_p - d_m) / (alist[ref + 1] - alist[ref - 1])
    ct = deltadot_continuity(mom, a_ref)
    D, f, _ = growth(a_ref)
    k, P_d = power(d_ref)
    P_lin = (f / a_ref)**2 * P_d
    _, r_fc, P_fd, P_ct = cross_coefficient(fd, ct)
    _, r_fd_d, _, _ = cross_coefficient(fd, d_ref)
    _, r_ct_d, _, _ = cross_coefficient(ct, d_ref)
    log.info("[%s] std FD %.4e, std continuity %.4e, mean FD %.2e, mean cont %.2e", g, fd.std(), ct.std(),
             fd.mean(), ct.mean())
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.4))
    ax[0].plot(k, r_fd_d, label=rf"FD centred, $\Delta a={alist[ref+1]-alist[ref-1]:.3f}$")
    ax[0].plot(k, r_ct_d, label="continuity (momentum divergence)")
    ax[1].plot(k, P_fd / P_lin, label="FD")
    ax[1].plot(k, P_ct / P_lin, label="continuity")
    ax[2].plot(k, r_fc, label="r(FD, continuity)", color="#009E73")
    ax[2].plot(k, P_fd / P_ct, label=r"$P_{\rm FD}/P_{\rm cont}$", color="#D55E00")
    style_k_axis(ax[0], r"$r(\dot\delta,\ \delta)$"); ax[0].set_ylim(0.5, 1.02)
    style_k_axis(ax[1], r"$P(\dot\delta)/[(f/a)^2 P(\delta)]$", logy=True); ax[1].axhline(1, color="0.6", lw=0.8)
    style_k_axis(ax[2], "FD vs continuity"); ax[2].set_ylim(0.8, 1.2); ax[2].axhline(1, color="0.6", lw=0.8)
    for x in ax:
        x.legend(loc="lower left")
    fig.suptitle(rf"FD vs continuity-equation $d\delta/da$: test_vel128 snap {ref}, $a={a_ref:.4f}$ "
                 rf"({'plain' if args.plain else 'compensated+interlaced'} TSC)", y=1.02)
    save(fig, f"fd_vs_continuity_{g}", log)
    status.append(f"{g} (a={a_ref:.3f}): r(FD,cont|k<{KMAX_TRAIN})={summarize(g+' r', k, r_fc, KMAX_TRAIN, log):.3f}, "
                  f"P_FD/P_cont(k<{KMAX_LIN})={summarize(g+' Pratio', k, P_fd/P_ct, KMAX_LIN, log):.3f}, "
                  f"P_FD/P_lin={summarize(g+' Plin', k, P_fd/P_lin, KMAX_LIN, log):.3f}")
print("fd_vs_continuity: see plots/fd_vs_continuity_<group>.pdf")
for s in status:
    print("  " + s)
