"""shoalkit -- linear and Stokes wave transformation with Lagrangian drift.

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
from .drift import (
    mean_drift_velocity,
    particle_track,
    stokes_drift,
    stokes_transport,
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
    "mean_drift_velocity",
    "particle_track",
    "stokes_drift",
    "stokes_transport",
    "__version__",
]
