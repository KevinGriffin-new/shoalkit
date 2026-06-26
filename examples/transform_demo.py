"""Minimal shoalkit demo: transform a deepwater wave and screen the theory."""
import shoalkit as sk

# A 2 m, 8 s swell arriving at 30 deg, evaluated in 10 m of water.
st = sk.transform(H0=2.0, T=8.0, theta0_deg=30.0, h=10.0)

print(f"regime       : {st.regime}  (h/L = {st.relative_depth:.3f})")
print(f"wavelength L : {st.L:8.3f} m")
print(f"wavenumber k : {st.k:8.4f} 1/m")
print(f"celerity   C : {st.C:8.3f} m/s")
print(f"group vel Cg : {st.Cg:8.3f} m/s")
print(f"direction th : {st.theta_deg:8.2f} deg")
print(f"shoaling  Ks : {st.Ks:8.4f}")
print(f"refraction Kr: {st.Kr:8.4f}")
print(f"local H      : {st.H:8.3f} m")
print(f"bottom u_b   : {st.ub:8.3f} m/s")

rec = sk.recommend_theory(st.H, st.L, st.h)
print(f"\nUrsell (eng) : {rec.ursell:.3g}   (normalized {rec.ursell_normalized:.3g})")
print(f"recommended  : {rec.recommended}  -- {rec.note}")

# surface elevation at the crest, analytic vs (if available) raschii
crest = sk.elevation(st, 0.0, theory="stokes", order=2)[0]
print(f"\nStokes-2 crest elevation about MWL: {crest:.3f} m "
      f"(Airy would be {st.H/2:.3f} m)")
