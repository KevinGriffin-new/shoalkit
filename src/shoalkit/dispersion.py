"""Linear (Airy) dispersion solve and deepwater->depth wave transformation.

Reproduces the output set of the University of Delaware / CACR "Wave Calculator"
(R. A. Dalrymple), based on the linear dispersion relationship and Snell's law
for straight, parallel offshore contours.

Reference:
    R. G. Dean & R. A. Dalrymple, *Water Wave Mechanics for Engineers and
    Scientists*, World Scientific.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

G_STANDARD = 9.80665  # m/s^2


def solve_wavenumber(omega: float, h: float, g: float = G_STANDARD,
                     tol: float = 1e-12, max_iter: int = 100) -> float:
    """Solve the linear dispersion relation omega**2 = g k tanh(k h) for k.

    Newton iteration seeded with an explicit approximation (Guo-style), which
    converges in a handful of steps across deep, transitional and shallow water.

    Parameters
    ----------
    omega : angular frequency (rad/s), = 2*pi/T
    h     : still-water depth (m)
    g     : gravitational acceleration (m/s^2)
    """
    if omega <= 0 or h <= 0:
        raise ValueError("omega and h must be positive")
    w2 = omega * omega
    x = w2 * h / g                       # = k0 * h (deepwater wavenumber * depth)
    kh = x / math.sqrt(math.tanh(x))     # seed
    k = kh / h
    for _ in range(max_iter):
        t = math.tanh(k * h)
        f = g * k * t - w2
        fp = g * t + g * k * h * (1.0 - t * t)
        step = f / fp
        k -= step
        if abs(step) < tol:
            break
    return k


@dataclass(frozen=True)
class WaveState:
    """Full linear-theory description of a wave at a given depth.

    All quantities are SI (m, s, rad). Angles in degrees where noted.
    """
    # inputs / fundamentals
    T: float            # period (s)
    omega: float        # angular frequency (rad/s)
    h: float            # depth (m)
    g: float            # gravity (m/s^2)
    # at-depth quantities
    k: float            # wavenumber (1/m)
    L: float            # wavelength (m)
    kh: float           # relative depth k*h
    C: float            # celerity = L/T (m/s)
    n: float            # Cg/C ratio
    Cg: float           # group velocity (m/s)
    H: float            # local wave height (m)
    theta_deg: float    # local direction from contour normal (deg)
    Ks: float           # shoaling coefficient
    Kr: float           # refraction coefficient
    ub: float           # bottom orbital velocity amplitude (m/s)
    # deepwater references
    L0: float
    C0: float
    Cg0: float
    H0: float
    theta0_deg: float

    @property
    def relative_depth(self) -> float:
        """h / L. > 0.5 deepwater, < 0.05 shallow, else transitional."""
        return self.h / self.L

    @property
    def regime(self) -> str:
        r = self.relative_depth
        if r > 0.5:
            return "deep"
        if r < 0.05:
            return "shallow"
        return "transitional"


def transform(H0: float, *, T: float | None = None, f: float | None = None,
              L: float | None = None, theta0_deg: float = 0.0, h: float,
              g: float = G_STANDARD) -> WaveState:
    """Transform a deepwater wave to a target depth via linear theory + Snell.

    Specify the wave by exactly one of:
      * ``T`` : deepwater (and everywhere) period in seconds, or
      * ``f`` : frequency in Hz (= 1/T), or
      * ``L`` : the *local* wavelength at depth ``h`` (period is solved from it).

    Parameters
    ----------
    H0         : deepwater wave height (m)
    theta0_deg : deepwater wave direction, degrees from the normal to straight
                 parallel contours (0 = shore-normal incidence)
    h          : target still-water depth (m)
    g          : gravitational acceleration (m/s^2)
    """
    given = [v is not None for v in (T, f, L)]
    if sum(given) != 1:
        raise ValueError("specify exactly one of T, f, or L")
    if h <= 0:
        raise ValueError("h must be positive")

    if L is not None:
        k = 2.0 * math.pi / L
        omega = math.sqrt(g * k * math.tanh(k * h))
        T = 2.0 * math.pi / omega
    else:
        if f is not None:
            T = 1.0 / f
        omega = 2.0 * math.pi / T
        k = solve_wavenumber(omega, h, g)

    # deepwater references
    L0 = g * T * T / (2.0 * math.pi)
    C0 = L0 / T
    Cg0 = C0 / 2.0

    # at-depth quantities
    L_loc = 2.0 * math.pi / k
    C = omega / k
    kh = k * h
    n = 0.5 * (1.0 + 2.0 * kh / math.sinh(2.0 * kh))
    Cg = n * C
    Ks = math.sqrt(Cg0 / Cg)

    th0 = math.radians(theta0_deg)
    sin_th = max(-1.0, min(1.0, (C / C0) * math.sin(th0)))
    th = math.asin(sin_th)
    Kr = math.sqrt(math.cos(th0) / math.cos(th))

    H = H0 * Ks * Kr
    ub = math.pi * H / (T * math.sinh(kh))

    return WaveState(
        T=T, omega=omega, h=h, g=g, k=k, L=L_loc, kh=kh, C=C, n=n, Cg=Cg,
        H=H, theta_deg=math.degrees(th), Ks=Ks, Kr=Kr, ub=ub,
        L0=L0, C0=C0, Cg0=Cg0, H0=H0, theta0_deg=theta0_deg,
    )
