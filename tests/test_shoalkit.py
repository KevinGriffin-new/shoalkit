import math

import pytest

import shoalkit as sk


def test_dispersion_deepwater_limit():
    # deep water: omega^2 = g k  => k = omega^2/g
    omega = 2 * math.pi / 8.0
    k = sk.solve_wavenumber(omega, h=1000.0)
    assert k == pytest.approx(omega ** 2 / sk.G_STANDARD, rel=1e-6)


def test_dispersion_shallow_limit():
    # shallow water: C -> sqrt(g h)
    h = 0.5
    st = sk.transform(1.0, T=30.0, h=h)  # long period, very shallow
    assert st.C == pytest.approx(math.sqrt(sk.G_STANDARD * h), rel=2e-3)


def test_transform_roundtrip_T_to_L_to_T():
    st1 = sk.transform(2.0, T=8.0, theta0_deg=30.0, h=10.0)
    st2 = sk.transform(2.0, L=st1.L, theta0_deg=30.0, h=10.0)
    assert st2.T == pytest.approx(st1.T, rel=1e-9)
    assert st2.k == pytest.approx(st1.k, rel=1e-9)
    assert st2.C == pytest.approx(st1.C, rel=1e-9)


def test_feeling_bottom_textbook():
    # CACR puzzle: deepwater wavelength 20 m -> T ~ 3.58 s
    st = sk.transform(1.0, L=20.0, h=500.0)  # deep so local L ~ L0
    assert st.T == pytest.approx(3.58, abs=0.02)


def test_shoaling_refraction_normal_incidence():
    # normal incidence -> no refraction, Kr == 1
    st = sk.transform(2.0, T=8.0, theta0_deg=0.0, h=10.0)
    assert st.Kr == pytest.approx(1.0, rel=1e-9)
    assert st.H == pytest.approx(st.H0 * st.Ks, rel=1e-9)


def test_stokes2_deepwater_limit():
    # a2 -> k a^2 / 2 with a = H/2 in deep water
    st = sk.transform(2.0, T=8.0, h=1000.0)
    a = st.H / 2.0
    a2 = sk.stokes2_second_harmonic(st)
    assert a2 == pytest.approx(st.k * a * a / 2.0, rel=1e-3)


def test_stokes2_crest_higher_than_airy():
    st = sk.transform(2.0, T=8.0, h=6.0)
    airy = sk.airy_elevation(st, 0.0)[0]
    stk = sk.stokes2_elevation(st, 0.0)[0]
    assert stk > airy  # peaked crest


def test_ursell_convention_equivalence():
    # engineering Ur == 4 pi^2 H / (k^2 h^3)
    H, h = 1.5, 4.0
    st = sk.transform(H, T=10.0, h=h)
    Ur = sk.ursell(H, st.L, h)
    hedges = 4 * math.pi ** 2 * H / (st.k ** 2 * h ** 3)
    assert Ur == pytest.approx(hedges, rel=1e-9)
    assert sk.ursell_normalized(H, st.L, h) == pytest.approx(
        (3 / (32 * math.pi ** 2)) * Ur, rel=1e-12)


def test_gate_picks_cnoidal_in_shallow():
    st = sk.transform(1.0, T=12.0, h=2.0)  # Ur >> 26
    rec = sk.recommend_theory(st.H, st.L, st.h)
    assert rec.recommended == "cnoidal"
    assert rec.ursell > sk.STOKES_CNOIDAL


def test_gate_picks_airy_when_gentle_and_deep():
    st = sk.transform(0.2, T=6.0, h=200.0)
    rec = sk.recommend_theory(st.H, st.L, st.h)
    assert rec.recommended == "airy"


@pytest.mark.skipif(not sk.HAVE_RASCHII, reason="raschii not installed")
def test_analytic_matches_raschii_stokes2():
    st = sk.transform(2.0, T=8.0, h=10.0)
    xs = [0.0, st.L / 4, st.L / 2, 3 * st.L / 4]
    ana = sk.elevation(st, xs, theory="stokes", order=2, backend="analytic")
    ras = sk.elevation(st, xs, theory="stokes", order=2, backend="raschii")
    for a, r in zip(ana, ras):
        assert a == pytest.approx(r, abs=0.05)  # leading order should agree
