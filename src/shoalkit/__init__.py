"""shoalkit -- linear & Stokes wave transformation with theory gating.

A thin, citable wrapper that:
  * solves the linear dispersion relation and reproduces the CACR/UDel wave
    calculator output set (L, k, C, Cg, direction, Ks, Kr, u_b);
  * provides Airy and 2nd-order Stokes surface elevation in closed form, and
    bridges to ``raschii`` for higher-order Stokes / Fenton profiles;
  * exposes the Ursell number (two pinned conventions) and a transparent
    wave-theory applicability gate.
"""
from .dispersion import (
    G_STANDARD,
    WaveState,
    solve_wavenumber,
    transform,
)
from .elevation import (
    HAVE_RASCHII,
    airy_elevation,
    elevation,
    orbital_velocity,
    stokes2_elevation,
    stokes2_second_harmonic,
)
from .gate import (
    LINEAR_UPPER,
    STOKES_CNOIDAL,
    TheoryRecommendation,
    recommend_theory,
    ursell,
    ursell_normalized,
)

__version__ = "0.1.0"

__all__ = [
    "G_STANDARD",
    "WaveState",
    "solve_wavenumber",
    "transform",
    "HAVE_RASCHII",
    "airy_elevation",
    "elevation",
    "orbital_velocity",
    "stokes2_elevation",
    "stokes2_second_harmonic",
    "LINEAR_UPPER",
    "STOKES_CNOIDAL",
    "TheoryRecommendation",
    "recommend_theory",
    "ursell",
    "ursell_normalized",
    "__version__",
]
