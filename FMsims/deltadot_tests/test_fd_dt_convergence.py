#!/usr/bin/env python
"""Design question: how does the finite-difference deltadot depend on the step Delta a?
(Is a *larger* difference more robust?)  Converts compare_dt_convergence.ipynb.

Data: test_vel128 (32 snapshots).  For each redshift group, centred pairs of increasing span
around a reference snapshot.  Metrics vs k, for each span:
  r(deltadot, delta_ref)            how well deltadot tracks the density field (1 in linear theory)
  P(deltadot) / P_lin               P_lin = (f/a)^2 (D(a_mid)/D(a_ref))^2 P(delta_ref): unity on
                                    linear scales if growth is right; excess = noise or nonlinearity
  r(deltadot, deltadot_finest)      convergence towards the smallest span
Two error sources compete: truncation (grows with span, ~ span^2 for centred) and noise
(particle/painting/integrator noise in each delta, divided by the span, so grows as 1/span).

Painting: production settings (compensated TSC + interlacing) unless --plain (notebook settings).
Plots: plots/fd_dt_convergence_<group>.pdf
"""
import argparse
import numpy as np
from common import (TESTRUN, KMAX_TRAIN, KMAX_LIN, snapshot_list, load_particles, paint_delta,
                    growth, power, cross_coefficient, summarize, style_k_axis, save, setup_logging,
                    Timer, plt)

GROUPS = {   # reference snapshot index, centred pairs (inner -> outer)
    "z2":    (7,  [(6, 8), (5, 9), (4, 10), (3, 11)]),
    "z0.4":  (15, [(14, 16), (13, 17)]),
    "z0.03": (23, [(22, 24), (21, 25), (20, 26), (19, 27), (18, 28)]),
}

p = argparse.ArgumentParser()
p.add_argument("--group", choices=list(GROUPS), nargs="*", default=list(GROUPS))
p.add_argument("--plain", action="store_true", help="plain TSC, no compensation/interlacing")
args = p.parse_args()
comp = not args.plain
log = setup_logging("fd_dt_convergence" + ("_plain" if args.plain else ""))

files, alist = snapshot_list(TESTRUN)
log.info("%d snapshots, a = %s", len(files), np.array2string(alist, precision=4))
cache = {}


def delta(i):
    if i not in cache:
        with Timer(log, f"paint snap {i} (a={alist[i]:.4f})"):
            cache[i] = paint_delta(load_particles(files[i])[1], compensated=comp, interlaced=comp)
    return cache[i]


status = []
for g in args.group:
    ref, pairs = GROUPS[g]
    a_ref = alist[ref]
    D_ref, f_ref, _ = growth(a_ref)
    d_ref = delta(ref)
    k, P_ref = power(d_ref)
    dd, spans, amid = [], [], []
    for i, j in pairs:
        dd.append((delta(j) - delta(i)) / (alist[j] - alist[i]))
        spans.append(alist[j] - alist[i])
        amid.append(0.5 * (alist[i] + alist[j]))
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.4))
    res = []
    for n, (ddot, span, am) in enumerate(zip(dd, spans, amid)):
        D_m, f_m, _ = growth(am)
        P_lin = (f_m / am)**2 * (D_m / D_ref)**2 * P_ref
        _, r_d, P_dd, _ = cross_coefficient(ddot, d_ref)
        _, r_fine, _, _ = cross_coefficient(ddot, dd[0])
        lab = rf"$\Delta a={span:.3f}$ (snaps {pairs[n][0]},{pairs[n][1]})"
        ax[0].plot(k, r_d, label=lab)
        ax[1].plot(k, P_dd / P_lin, label=lab)
        ax[2].plot(k, r_fine, label=lab)
        res.append((span, summarize(f"[{g}] span {span:.3f} r(dd,delta)", k, r_d, KMAX_TRAIN, log),
                    summarize(f"[{g}] span {span:.3f} P/Plin", k, P_dd / P_lin, KMAX_LIN, log),
                    summarize(f"[{g}] span {span:.3f} r(dd,finest)", k, r_fine, KMAX_TRAIN, log)))
    style_k_axis(ax[0], r"$r(\dot\delta,\ \delta_{\rm ref})$")
    style_k_axis(ax[1], r"$P(\dot\delta)\,/\,P_{\rm lin}(\dot\delta)$")
    style_k_axis(ax[2], r"$r(\dot\delta,\ \dot\delta_{\rm smallest\ span})$")
    ax[0].set_ylim(0.5, 1.02)
    ax[1].set_ylim(0.8, 1.6)
    ax[1].axhline(1, color="0.6", lw=0.8)
    ax[2].set_ylim(0.9, 1.005)
    ax[0].legend(loc="lower left")
    fig.suptitle(rf"FD $\dot\delta = d\delta/da$ vs. step: test_vel128, reference $a={a_ref:.4f}$ "
                 rf"($z={1/a_ref-1:.2f}$), {'plain TSC' if args.plain else 'compensated+interlaced TSC'}", y=1.02)
    save(fig, f"fd_dt_convergence_{g}" + ("_plain" if args.plain else ""), log)
    r_small, r_large = res[0][1], res[-1][1]
    status.append(f"{g}: r(dd,delta|k<{KMAX_TRAIN}) {r_small:.3f} (span {res[0][0]:.3f}) -> "
                  f"{r_large:.3f} (span {res[-1][0]:.3f}); P/Plin(k<{KMAX_LIN}) {res[0][2]:.3f} -> {res[-1][2]:.3f}")

print("fd_dt_convergence: see plots/fd_dt_convergence_<group>.pdf")
for s in status:
    print("  " + s)
