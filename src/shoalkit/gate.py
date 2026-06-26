"""Ursell number and a coarse wave-theory applicability gate.

Two conventions are provided explicitly, because the literature is not
consistent and a value quoted from one source will not match another unless
the definition is pinned:

* ``ursell``            : engineering form  Ur = H * L**2 / h**3.
                          Identical to Hedges' 4*pi**2 * H / (k**2 * h**3),
                          since L = 2*pi/k. This is the form most coastal
                          references and the Le Mehaute diagram use.
* ``ursell_normalized`` : Ursell's original  U = (3 / (32*pi**2)) * H*L**2/h**3.
                          Linear theory is applicable when U << 1, equivalently
                          when the engineering Ur << 32*pi**2/3 ~= 105.

References:
    F. Ursell (1953), Proc. Camb. Phil. Soc. 49, 685.
    T. S. Hedges (1995), Proc. ICE Water, Maritime & Energy 112, 111.
    B. Le Mehaute (1976), *An Introduction to Hydrodynamics and Water Waves*.

The ``recommend_theory`` gate is a coarse screen, not a substitute for Le
Mehaute's diagram. Boundaries are exposed as arguments so they can be pinned
to whatever convention a downstream pipeline adopts.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

#: Engineering-Ursell value below which linear theory is broadly applicable
#: (== 32*pi**2/3, i.e. normalized U << 1).
LINEAR_UPPER = 32.0 * math.pi ** 2 / 3.0  # ~= 105.3

#: Common engineering-Ursell crossover between Stokes and cnoidal regimes.
STOKES_CNOIDAL = 26.0


def ursell(H: float, L: float, h: float) -> float:
    """Engineering Ursell number, Ur = H * L**2 / h**3."""
    return H * L * L / (h ** 3)


def ursell_normalized(H: float, L: float, h: float) -> float:
    """Ursell's original normalization, U = (3/32pi^2) * H L^2 / h^3."""
    return (3.0 / (32.0 * math.pi ** 2)) * ursell(H, L, h)


@dataclass(frozen=True)
class TheoryRecommendation:
    recommended: str          # 'airy' | 'stokes' | 'cnoidal'
    ursell: float             # engineering convention
    ursell_normalized: float
    kh: float
    steepness: float          # H / L
    note: str


def recommend_theory(H: float, L: float, h: float, *,
                     linear_steepness: float = 0.006,
                     stokes_cnoidal: float = STOKES_CNOIDAL,
                     linear_ursell: float = 1.0) -> TheoryRecommendation:
    """Coarse wave-theory screen from relative depth, steepness and Ursell.

    Logic (deliberately conservative and transparent):

    * Deep / intermediate water (kh >= pi, i.e. h/L >= 0.5): pick ``airy`` if
      the wave is gentle (H/L < ``linear_steepness``), else ``stokes``.
    * Otherwise use the engineering Ursell number:
        - Ur <  ``linear_ursell``   -> ``airy``
        - Ur <  ``stokes_cnoidal``  -> ``stokes``
        - Ur >= ``stokes_cnoidal``  -> ``cnoidal`` (Stokes out of range)

    This is a screen; for design work consult Le Mehaute's diagram directly.
    """
    k = 2.0 * math.pi / L
    kh = k * h
    Ur = ursell(H, L, h)
    Un = ursell_normalized(H, L, h)
    steep = H / L

    if kh >= math.pi:
        if steep < linear_steepness:
            rec, why = "airy", "deep/intermediate water, gentle slope"
        else:
            rec, why = "stokes", "deep/intermediate water, finite steepness"
    else:
        if Ur < linear_ursell:
            rec, why = "airy", f"shallow/transitional, Ur={Ur:.2g} < {linear_ursell:g}"
        elif Ur < stokes_cnoidal:
            rec, why = "stokes", f"transitional, Ur={Ur:.2g} < {stokes_cnoidal:g}"
        else:
            rec, why = "cnoidal", (f"long waves in shallow water, Ur={Ur:.2g} "
                                   f">= {stokes_cnoidal:g}: Stokes out of range")
    return TheoryRecommendation(
        recommended=rec, ursell=Ur, ursell_normalized=Un, kh=kh,
        steepness=steep, note=why,
    )
