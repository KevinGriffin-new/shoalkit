"""Stokes drift and Lagrangian particle transport.

shoalkit's :mod:`dispersion` and :mod:`elevation` modules describe the wave
field from a *fixed* (Eulerian) point of view: what passes a stationary
sensor. This module adds the *Lagrangian* companion -- the slow mean transport
that a fluid parcel (or a drifting buoy, a floating particle, a larva) actually
undergoes because its orbital path does not quite close.

At leading order in wave steepness the parcel-following mean velocity is the
**Stokes drift** (Stokes 1847; Longuet-Higgins 1953):

    u_s(z) = a^2 * omega * k * cosh(2 k (z + h)) / (2 * sinh^2(k h))

with a = H/2, z measured from the mean water level (0 at surface, -h at bed).
The depth-integrated volume transport per unit width is

    Q_s = integral_{-h}^{0} u_s dz = (a^2 * omega / 2) * coth(k h) = E / (rho C)

i.e. the wave energy density divided by rho*C -- the classic Stokes transport.

All quantities are SI. The closed forms here are dependency-free (standard
library only), consistent with the rest of shoalkit; the ``particle_track``
integrator likewise needs no extra packages and produces the open, forward-
creeping orbits that distinguish Lagrangian from Eulerian motion.

References
----------
* G. G. Stokes (1847), *On the theory of oscillatory waves*, Trans. Camb.
  Phil. Soc. 8, 441.
* M. S. Longuet-Higgins (1953), *Mass transport in water waves*,
  Phil. Trans. R. Soc. A 245, 535. doi:10.1098/rsta.1953.0006
* T. S. van den Bremer & O. Breivik (2017), *Stokes drift*,
  Phil. Trans. R. Soc. A. doi:10.1098/rsta.2017.0104
"""
from __future__ import annotations

import math
from typing import Sequence

from .dispersion import WaveState


def _as_list(x) -> list[float]:
    if isinstance(x, (int, float)):
        return [float(x)]
    return [float(v) for v in x]


def stokes_drift(state: WaveState, z=0.0) -> list[float]:
    """Leading-order Stokes drift velocity u_s(z), about MWL.

    Parameters
    ----------
    state : WaveState from :func:`shoalkit.transform`.
    z     : depth(s) from mean water level (0 at surface, -h at bed).
            Scalar or iterable; a list is always returned.

    Returns
    -------
    list of float
        Mean parcel-following horizontal velocity (m/s), in the direction of
        wave propagation, at each ``z``.

    Notes
    -----
    ``u_s(z) = a^2 * omega * k * cosh(2 k (z + h)) / (2 sinh^2(k h))``, a = H/2.
    Deepwater limit ``u_s(0) -> omega k a^2``. This O(a^2) result is unchanged
    at 2nd-order Stokes; it is the standard "Stokes drift" for both Airy and
    2nd-order waves.
    """
    a = state.H / 2.0
    k, om, h = state.k, state.omega, state.h
    kh = state.kh
    pref = a * a * om * k / (2.0 * math.sinh(kh) ** 2)
    return [pref * math.cosh(2.0 * k * (zi + h)) for zi in _as_list(z)]


def stokes_transport(state: WaveState) -> float:
    """Depth-integrated Stokes volume transport per unit width Q_s (m^2/s).

    ``Q_s = (a^2 omega / 2) coth(k h) = E / (rho C)`` with a = H/2. This is the
    net mass-transport a column of fluid carries in the propagation direction.
    """
    a = state.H / 2.0
    return (a * a * state.omega / 2.0) / math.tanh(state.kh)


def mean_drift_velocity(state: WaveState) -> float:
    """Depth-averaged Stokes drift, ``Q_s / h`` (m/s).

    A convenient single scalar to compare against a buoy's observed net
    Lagrangian velocity over a deployment.
    """
    return stokes_transport(state) / state.h


def particle_track(
    state: WaveState,
    z0: float = 0.0,
    x0: float = 0.0,
    *,
    n_periods: float = 5.0,
    steps_per_period: int = 200,
) -> dict[str, list[float]]:
    """Integrate a fluid parcel's Lagrangian trajectory in the Airy field.

    Advances a parcel by RK4 through the linear (Airy) orbital velocity field,
    evaluated at the parcel's *instantaneous* position. Because the field is
    sampled where the parcel actually is (not at its mean position), the loops
    do not close: the parcel creeps forward at the Stokes-drift rate. This is
    the quantity ``stokes_drift`` predicts, here made visible as an open orbit
    -- the natural thing to animate.

    Parameters
    ----------
    z0, x0          : initial parcel position about MWL (m).
    n_periods       : how many wave periods to integrate.
    steps_per_period: RK4 steps per period (accuracy/​smoothness knob).

    Returns
    -------
    dict with keys ``t``, ``x``, ``z`` (lists of equal length) and
    ``drift_predicted`` -- the closed-form ``stokes_drift(state, z0)`` value,
    for comparison against the net horizontal displacement ``x[-1] - x0``.
    """
    a = state.H / 2.0
    k, om, h = state.k, state.omega, state.h
    sinh_kh = math.sinh(k * h)

    def vel(x: float, z: float, t: float) -> tuple[float, float]:
        # Airy orbital velocity, clamped to the bed to keep cosh/sinh finite.
        zc = max(z, -h)
        ph = k * x - om * t
        u = a * om * math.cosh(k * (zc + h)) / sinh_kh * math.cos(ph)
        w = a * om * math.sinh(k * (zc + h)) / sinh_kh * math.sin(ph)
        return u, w

    n = max(1, int(round(n_periods * steps_per_period)))
    dt = state.T / steps_per_period
    x, z, t = float(x0), float(z0), 0.0
    ts, xs, zs = [t], [x], [z]
    for _ in range(n):
        u1, w1 = vel(x, z, t)
        u2, w2 = vel(x + 0.5 * dt * u1, z + 0.5 * dt * w1, t + 0.5 * dt)
        u3, w3 = vel(x + 0.5 * dt * u2, z + 0.5 * dt * w2, t + 0.5 * dt)
        u4, w4 = vel(x + dt * u3, z + dt * w3, t + dt)
        x += dt * (u1 + 2 * u2 + 2 * u3 + u4) / 6.0
        z += dt * (w1 + 2 * w2 + 2 * w3 + w4) / 6.0
        t += dt
        ts.append(t); xs.append(x); zs.append(z)

    return {
        "t": ts,
        "x": xs,
        "z": zs,
        "drift_predicted": stokes_drift(state, z0)[0],
    }
