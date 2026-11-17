#!/usr/bin/env python
"""Design question: is the triplet half-spacing da = 0.01 sqrt(a) a sensible finite-difference step?

Pure cosmology, no simulation data.  Converts test_da_values.ipynb and adds the *linear-theory*
truncation bias of each stencil: apply the forward (a, a+da), backward (a-da, a) and centred
(a-da, a+da) difference to D(a) itself and compare with dD/da.  In the linear regime delta is
proportional to D, so this is exactly the bias the production deltadot inherits on large scales.

Pass criteria: centred bias < 0.1 % everywhere; forward bias reported (expected ~ da/2 * D''/D').
Plot: plots/da_triplet_spacing.pdf
"""
import numpy as np
from scipy.integrate import quad
from common import growth, E_of_a, setup_logging, save, plt

log = setup_logging("da_triplet_spacing")
DA0 = 0.01                      # gen_outputs.py: da = 0.01 * sqrt(a)
MAX_DLNA_GADGET = 0.008         # MaxSizeTimestep in the production param file (in ln a)
H0_INV_GYR = 9.7779 / 0.6774    # 1/H0 in Gyr for h = 0.6774


def da_of_a(a):
    return DA0 * np.sqrt(a)


def age_gyr(a):
    return H0_INV_GYR * quad(lambda x: 1.0 / (x * E_of_a(x)), 0, a)[0]


a = np.linspace(0.0111, 0.99, 200)
da = da_of_a(a)
D, f, dDda = growth(a)
Dp, _, _ = growth(a + da)
Dm, _, _ = growth(a - da)
bias_fwd = (Dp - D) / da / dDda - 1
bias_bwd = (D - Dm) / da / dDda - 1
bias_cen = (Dp - Dm) / (2 * da) / dDda - 1
dlna = np.log((a + da) / (a - da))
dt = np.array([age_gyr(x + d) - age_gyr(x - d) for x, d in zip(a, da)])

for x, d, bf, bc in zip(a[::40], da[::40], bias_fwd[::40], bias_cen[::40]):
    log.info("a=%.3f da=%.4f forward bias=%+.3e centred bias=%+.3e", x, d, bf, bc)

fig, ax = plt.subplots(1, 3, figsize=(11, 3.2))
ax[0].plot(a, dlna, label=r"$\Delta \ln a$ of the triplet ($a\pm da$)")
ax[0].axhline(MAX_DLNA_GADGET, color="0.4", ls="--", lw=1, label="Gadget4 MaxSizeTimestep")
ax[0].set(xlabel="a", ylabel=r"$\Delta\ln a$", yscale="log", title="Triplet span vs. integrator step")
ax[0].legend()
ax[1].plot(a, dt, label=r"$\Delta t$ of the triplet [Gyr]")
ax[1].set(xlabel="a", ylabel=r"$\Delta t$ [Gyr]", yscale="log", title="Triplet span in time")
ax[1].legend()
ax[2].plot(a, 100 * bias_fwd, label="forward $(a, a+da)$ [stored]")
ax[2].plot(a, 100 * bias_bwd, label="backward $(a-da, a)$")
ax[2].plot(a, 100 * bias_cen, label="centred $(a-da, a+da)$")
ax[2].axhline(0, color="0.6", lw=0.8)
ax[2].set(xlabel="a", ylabel=r"stencil bias on $dD/da$ [%]", title="Linear-theory truncation bias")
ax[2].legend()
for x in ax:
    x.grid(alpha=0.3)
fig.suptitle(r"Triplet half-spacing $da = 0.01\sqrt{a}$: span and finite-difference bias in linear theory", y=1.03)
save(fig, "da_triplet_spacing", log)

ok = np.all(np.abs(bias_cen) < 1e-3)
print(f"da_triplet_spacing: centred bias max {np.abs(bias_cen).max()*100:.3f}% -> {'PASS' if ok else 'FAIL'}")
print(f"  forward (stored) bias: {bias_fwd[0]*100:+.2f}% at a={a[0]:.3f}, "
      f"{bias_fwd[np.argmin(abs(a-0.5))]*100:+.2f}% at a=0.5, {bias_fwd[-1]*100:+.2f}% at a={a[-1]:.2f}")
print(f"  triplet dln a / Gadget max step: {dlna[-1]/MAX_DLNA_GADGET:.1f} at a=1, {dlna[0]/MAX_DLNA_GADGET:.1f} at a=0.011")
raise SystemExit(0 if ok else 1)
