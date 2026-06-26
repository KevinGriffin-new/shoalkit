"""Surface elevation and orbital velocity profiles.

Two backends:

* ``analytic`` (no extra dependencies): linear Airy and 2nd-order Stokes
  surface elevation in closed form. Exact and dependency-free.
* ``raschii`` (optional, ``pip install shoalkit[nonlinear]``): higher-order
  Stokes (2nd-5th) and Fenton stream-function waves, plus orbital velocities.

All elevations returned here are measured about the **mean water level**
(eta = 0 at still water). Note that raschii's native datum is the seabed
(still water at z = depth); the bridge below subtracts depth so both backends
share the MWL convention.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

from .dispersion import WaveState

try:                                  # optional dependency
    import raschii  # type: ignore
    HAVE_RASCHII = True
except Exception:                     # pragma: no cover
    HAVE_RASCHII = False


def _as_list(x) -> list[float]:
    if isinstance(x, (int, float)):
        return [float(x)]
    return [float(v) for v in x]


def stokes2_second_harmonic(state: WaveState) -> float:
    """Amplitude of the 2nd-order Stokes bound harmonic (about MWL).

    a2 = H^2 k / 16 * cosh(kh) (2 + cosh 2kh) / sinh^3(kh).
    Deepwater limit -> k a^2 / 2 with a = H/2.
    """
    H, k, kh = state.H, state.k, state.kh
    return (H * H * k / 16.0) * (math.cosh(kh) * (2.0 + math.cosh(2.0 * kh))) \
        / (math.sinh(kh) ** 3)


def airy_elevation(state: WaveState, x, t: float = 0.0) -> list[float]:
    """Linear surface elevation eta(x, t) about MWL."""
    a = state.H / 2.0
    k, w = state.k, state.omega
    return [a * math.cos(k * xi - w * t) for xi in _as_list(x)]


def stokes2_elevation(state: WaveState, x, t: float = 0.0) -> list[float]:
    """2nd-order Stokes surface elevation eta(x, t) about MWL (analytic)."""
    a = state.H / 2.0
    a2 = stokes2_second_harmonic(state)
    k, w = state.k, state.omega
    out = []
    for xi in _as_list(x):
        ph = k * xi - w * t
        out.append(a * math.cos(ph) + a2 * math.cos(2.0 * ph))
    return out


def _raschii_wave(state: WaveState, theory: str, order: int):
    if theory == "fenton":
        return raschii.FentonWave(height=state.H, depth=state.h,
                                  length=state.L, N=max(order, 5))
    if theory == "stokes":
        return raschii.StokesWave(height=state.H, depth=state.h,
                                  length=state.L, N=order)
    return raschii.AiryWave(height=state.H, depth=state.h, length=state.L)


def elevation(state: WaveState, x, t: float = 0.0, *, theory: str = "airy",
              order: int = 2, backend: str = "auto") -> list[float]:
    """Surface elevation eta(x, t) about MWL for the chosen wave theory.

    Parameters
    ----------
    theory  : 'airy', 'stokes', or 'fenton'
    order   : Stokes/Fenton order (2-5). Ignored for Airy.
    backend : 'analytic', 'raschii', or 'auto'. 'auto' uses the analytic forms
              for Airy and 2nd-order Stokes, and raschii for anything higher.
    """
    theory = theory.lower()
    use_raschii = backend == "raschii" or (
        backend == "auto" and (theory == "fenton" or
                               (theory == "stokes" and order > 2))
    )
    if use_raschii:
        if not HAVE_RASCHII:
            raise RuntimeError(
                "raschii backend requested but not installed: "
                "pip install shoalkit[nonlinear]"
            )
        w = _raschii_wave(state, theory, order)
        xs = _as_list(x)
        eta = w.surface_elevation(xs, t=t)          # datum = seabed
        return [float(e) - state.h for e in eta]    # convert to MWL

    # analytic backends
    if theory == "airy":
        return airy_elevation(state, x, t)
    if theory == "stokes":
        if order != 2:
            raise ValueError("analytic Stokes backend supports order=2 only; "
                             "use backend='raschii' for higher order")
        return stokes2_elevation(state, x, t)
    raise ValueError(f"unknown theory {theory!r}")


def orbital_velocity(state: WaveState, x: float, z: float, t: float = 0.0):
    """Horizontal/vertical orbital velocity (u, w) at (x, z) about MWL.

    z is measured from MWL (0 at surface mean, -h at bed). Requires raschii.
    Linear closed-form fallback is provided for the Airy case.
    """
    if HAVE_RASCHII:
        w = raschii.AiryWave(height=state.H, depth=state.h, length=state.L)
        vel = w.velocity(float(x), float(z) + state.h, t=t)  # raschii z from bed
        v = vel[0]
        return float(v[0]), float(v[1])
    # Airy closed form
    a = state.H / 2.0
    k, om, h = state.k, state.omega, state.h
    ph = k * x - om * t
    u = a * om * math.cosh(k * (z + h)) / math.sinh(k * h) * math.cos(ph)
    ww = a * om * math.sinh(k * (z + h)) / math.sinh(k * h) * math.sin(ph)
    return u, ww
