"""Shared helpers for the deltadot design-decision tests.

Conventions (match the production pipeline in ../L400_n128_s40/create_delta_deltadot_mesh.py):
  * deltadot means d(delta)/da  (per unit scale factor, NOT per Gyr as in the old notebooks)
  * Lbox = 400 Mpc/h, Nmesh = 128, TSC painting; compensation/interlacing are flags
  * growth factor D(a), f(a) for the *run* cosmology: flat LCDM, Omega_m = 0.3089, no radiation
    (Gadget4 was run with Neff = 0; see FMsims/PROGRESS.md)

Run inside the `nbodykit-env` conda env.  Verbose output goes to test_logs/deltadot_tests/.
"""
import os, sys, glob, logging, time, warnings
import numpy as np
import h5py
from scipy.integrate import quad
np.seterr(invalid="ignore", divide="ignore")   # k = 0 bin of ratios
warnings.filterwarnings("ignore", category=RuntimeWarning)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nbodykit.lab import ArrayCatalog, ArrayMesh, FFTPower  # noqa: E402

# ----------------------------------------------------------------------------- paths
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRATCH = os.path.expanduser("~/scratch1/FMsims")
TESTRUN = os.path.join(SCRATCH, "gadget4/test_vel128/output")      # 32 snapshots, a = 0.025 .. 1
PRODROOT = os.path.join(SCRATCH, "L400_n128_s40")                   # run-XXXX/output, run-XXXX/mesh
PLOTDIR = os.path.join(os.path.dirname(__file__), "plots")
LOGDIR = os.path.join(REPO, "test_logs", "deltadot_tests")

LBOX = 400.0
NMESH = 128
OMEGA_M = 0.3089      # Gadget4 param Omega0; OmegaLambda = 1 - Omega0, no radiation
KMAX_LIN = 0.15        # h/Mpc: "large scales" where linear theory is compared
KMAX_TRAIN = 0.5       # h/Mpc: scale to which the emulator should be accurate (spec section 7)


def setup_logging(name):
    """Verbose log to test_logs/deltadot_tests/<name>.log; only warnings+ reach stdout."""
    os.makedirs(LOGDIR, exist_ok=True)
    os.makedirs(PLOTDIR, exist_ok=True)
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.handlers = []
    fh = logging.FileHandler(os.path.join(LOGDIR, name + ".log"), mode="w")
    fh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    log.addHandler(fh)
    log.propagate = False
    return log


# ----------------------------------------------------------------------------- growth
def E_of_a(a, Om=OMEGA_M):
    return np.sqrt(Om / a**3 + (1.0 - Om))


def _growth_integral(a, Om):
    return quad(lambda x: 1.0 / (x * E_of_a(x, Om))**3, 0.0, a, epsabs=0, epsrel=1e-10)[0]


def growth(a, Om=OMEGA_M):
    """Return D(a) (normalised to D(1) = 1), f(a) = dlnD/dlna, dD/da for flat LCDM without radiation.

    D(a) = 5/2 Om E(a) int_0^a da'/(a' E)^3  (Heath 1977).  Exact for this cosmology."""
    a = np.atleast_1d(np.asarray(a, dtype=float))
    I = np.array([_growth_integral(x, Om) for x in a])
    E = E_of_a(a, Om)
    dE_da = -1.5 * Om / (a**4 * E)
    D_un = 2.5 * Om * E * I
    dD_da_un = 2.5 * Om * (dE_da * I + E / (a * E)**3)
    norm = 2.5 * Om * E_of_a(1.0, Om) * _growth_integral(1.0, Om)
    D, dD_da = D_un / norm, dD_da_un / norm
    f = a * dD_da / D
    if D.size == 1:
        return D[0], f[0], dD_da[0]
    return D, f, dD_da


def hubble_kms_per_mpch(a, Om=OMEGA_M):
    """H(a) in km/s per (Mpc/h): 100 E(a)."""
    return 100.0 * E_of_a(a, Om)


# ----------------------------------------------------------------------------- snapshots
def snapshot_list(outdir):
    """Sorted snapshot files with their scale factors."""
    files = sorted(glob.glob(os.path.join(outdir, "snap_*.hdf5")))
    a = np.array([h5py.File(f, "r")["Header"].attrs["Time"] for f in files])
    return files, a


def load_particles(fname, velocities=False):
    """Positions (Mpc/h) and, optionally, peculiar velocities (km/s) of PartType1.

    Gadget4 stores u = v_pec / sqrt(a) in cosmological runs, so v_pec = u * sqrt(a)."""
    with h5py.File(fname, "r") as hf:
        a = hf["Header"].attrs["Time"]
        pos = hf["PartType1/Coordinates"][:]
        vel = hf["PartType1/Velocities"][:] * np.sqrt(a) if velocities else None
    return a, pos, vel


def paint_delta(pos, Nmesh=NMESH, Lbox=LBOX, compensated=False, interlaced=False):
    """TSC-painted delta = rho/rho_mean - 1 as a numpy array."""
    cat = ArrayCatalog({"Position": pos}, BoxSize=[Lbox] * 3)
    mesh = cat.to_mesh(Nmesh=Nmesh, resampler="tsc", compensated=compensated,
                       interlaced=interlaced, position="Position")
    return mesh.paint(mode="real").value - 1.0


def paint_momentum(pos, vel, Nmesh=NMESH, Lbox=LBOX, compensated=False, interlaced=False):
    """TSC-painted momentum density (1+delta) v for the three components (km/s), numpy arrays.

    nbodykit normalises a `value`-weighted mesh by the mean particle number per cell, so the
    result is sum_i v_i W(x - x_i) / nbar = (1+delta) <v>, i.e. the momentum field."""
    cat = ArrayCatalog({"Position": pos, "V": vel}, BoxSize=[Lbox] * 3)
    out = []
    for i in range(3):
        cat["Vi"] = cat["V"][:, i]
        mesh = cat.to_mesh(Nmesh=Nmesh, resampler="tsc", compensated=compensated,
                           interlaced=interlaced, position="Position", value="Vi")
        out.append(mesh.paint(mode="real").value)
    return out


def deltadot_continuity(mom, a, Lbox=LBOX):
    """d(delta)/da from the exact continuity equation d(delta)/dt = -(1/a) div[(1+delta) v].

    mom: list of 3 momentum meshes in km/s; divergence in Fourier space; result per unit a."""
    N = mom[0].shape[0]
    k = np.fft.fftfreq(N, d=Lbox / N) * 2 * np.pi
    kz = np.fft.rfftfreq(N, d=Lbox / N) * 2 * np.pi
    kvec = np.meshgrid(k, k, kz, indexing="ij")
    div_k = 0j
    for i in range(3):
        ki = kvec[i].copy()
        ki[np.abs(np.abs(ki) - np.pi * N / Lbox) < 1e-8] = 0.0   # kill the Nyquist plane (reality)
        div_k = div_k + 1j * ki * np.fft.rfftn(mom[i])
    div = np.fft.irfftn(div_k, s=(N, N, N))                      # km/s per (Mpc/h)
    return -div / (a**2 * hubble_kms_per_mpch(a))


# ----------------------------------------------------------------------------- spectra
def power(field, Lbox=LBOX, second=None):
    """1d P(k) [(Mpc/h)^3] of a numpy field (or cross-spectrum with `second`); returns k, P."""
    m1 = ArrayMesh(field, BoxSize=Lbox)
    m2 = ArrayMesh(second, BoxSize=Lbox) if second is not None else None
    r = FFTPower(m1, second=m2, mode="1d", dk=None)
    return r.power["k"], r.power["power"].real


def cross_coefficient(f1, f2, Lbox=LBOX):
    """k, r(k) = P12 / sqrt(P1 P2), P1, P2."""
    k, p12 = power(f1, Lbox, second=f2)
    _, p1 = power(f1, Lbox)
    _, p2 = power(f2, Lbox)
    with np.errstate(invalid="ignore", divide="ignore"):
        r = p12 / np.sqrt(p1 * p2)
    return k, r, p1, p2


def band(k, kmin, kmax):
    return (k >= kmin) & (k < kmax) & np.isfinite(k)


def summarize(name, k, values, kmax, log, fmt="{:.4f}"):
    """Mean of `values` over k < kmax; logged and returned."""
    sel = band(k, 0, kmax) & np.isfinite(values)
    v = float(np.mean(values[sel])) if sel.any() else np.nan
    log.info("%s  mean(k<%.2f) = %s", name, kmax, fmt.format(v))
    return v


def style_k_axis(ax, ylabel, logy=False):
    ax.set_xscale("log")
    if logy:
        ax.set_yscale("log")
    ax.set_xlabel(r"$k\ [h/{\rm Mpc}]$")
    ax.set_ylabel(ylabel)
    ax.axvline(KMAX_TRAIN, color="0.7", ls=":", lw=0.8)
    ax.grid(alpha=0.3)


def save(fig, name, log):
    path = os.path.join(PLOTDIR, name + ".pdf")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    log.info("saved %s", path)
    return path


class Timer:
    def __init__(self, log, what):
        self.log, self.what = log, what

    def __enter__(self):
        self.t0 = time.time()
        return self

    def __exit__(self, *a):
        self.log.info("%s: %.1f s", self.what, time.time() - self.t0)


# ----------------------------------------------------------------------------- plot style
# Okabe-Ito palette (colour-blind safe), used in fixed order; never cycled beyond 7 series.
PALETTE = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]
plt.rcParams.update({
    "axes.prop_cycle": plt.cycler(color=PALETTE),
    "lines.linewidth": 1.4,
    "axes.grid": False,
    "font.size": 9,
    "legend.fontsize": 8,
    "legend.frameon": False,
    "figure.dpi": 100,
})
