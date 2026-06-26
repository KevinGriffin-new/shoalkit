# shoalkit

Linear & Stokes wave transformation with theory gating — a small, **citable**
Python wrapper descended from the University of Delaware / CACR "Wave
Calculator" (R. A. Dalrymple).

It does three things, deliberately:

1. **Dispersion + transformation.** Solves `ω² = g·k·tanh(kh)` and reproduces
   the CACR output set at a target depth: wavelength `L`, wavenumber `k`,
   celerity `C`, group velocity `Cg`, direction `θ` (Snell), shoaling `Ks`,
   refraction `Kr`, and bottom orbital velocity `u_b`.
2. **Surface profiles.** Closed-form Airy and 2nd-order Stokes elevation with
   no dependencies; bridges to [`raschii`](https://pypi.org/project/raschii/)
   for higher-order Stokes (3rd–5th) and Fenton stream-function waves, plus
   orbital velocities.
3. **Theory gating.** The Ursell number in two **pinned** conventions and a
   transparent `recommend_theory` screen, so a pipeline can decide when linear
   inversion is trustworthy versus when it should fall back to nonlinear forms.

The core is pure standard library; `raschii`/`numpy` are optional.

## Install

```bash
pip install shoalkit                 # core (pure stdlib)
pip install "shoalkit[nonlinear]"    # + raschii/numpy for 3rd–5th order & Fenton
```

## Quick start

```python
import shoalkit as sk

st = sk.transform(H0=2.0, T=8.0, theta0_deg=30.0, h=10.0)
print(st.L, st.C, st.Ks, st.Kr, st.H, st.ub)   # CACR-style outputs
print(st.regime, st.relative_depth)             # 'transitional', 0.141

# specify by wavelength or frequency instead of period:
sk.transform(2.0, L=70.0, h=10.0)               # local wavelength -> solves T
sk.transform(2.0, f=0.125, h=10.0)              # frequency in Hz

# surface elevation (analytic by default; raschii for higher order):
sk.elevation(st, [0, st.L/2], theory="stokes", order=2)
sk.elevation(st, 0.0, theory="fenton", order=5, backend="raschii")

# theory screen:
rec = sk.recommend_theory(st.H, st.L, st.h)
print(rec.recommended, rec.ursell, rec.note)
```

## A note on the Ursell number (read this before quoting a value)

The literature uses two normalizations. Both are provided and named:

| function | definition | notes |
|---|---|---|
| `ursell(H, L, h)` | `H·L²/h³` | engineering form; **identical** to Hedges' `4π²H/(k²h³)` since `L = 2π/k` |
| `ursell_normalized(H, L, h)` | `(3/32π²)·H·L²/h³` | Ursell's original; linear theory valid for this ≪ 1 |

Linear validity bound: engineering `Ur ≪ 32π²/3 ≈ 105` (equivalently normalized
`≪ 1`). `recommend_theory` uses a coarse Stokes/cnoidal crossover near
engineering `Ur ≈ 26` by default; all thresholds are arguments. For design work,
consult Le Méhauté's diagram directly — this is a screen, not a substitute.

## Interactive artifact

`web/wave-calculator.html` is a self-contained, plugin-free reimplementation of
the original applet with a period-accurate animation and a linear/Stokes
toggle. It runs offline in any browser and can be deposited as its own
research artifact (see below).

## Tests

```bash
pip install "shoalkit[test,nonlinear]"
pytest -q
```

Includes the deepwater Stokes limit (`a₂ → ½ka²`), a dispersion round-trip
(T → L → T), the shallow-water celerity limit (`C → √gh`), the Ursell
convention-equivalence check, and a cross-check that the analytic 2nd-order
elevation agrees with `raschii`.

## Making it citable (ORCID + Zenodo)

The metadata is already filled in — author **Kevin Griffin**, ORCID
[`0009-0005-0439-6684`](https://orcid.org/0009-0005-0439-6684), repo
`github.com/KevinGriffin-new/shoalkit`. The remaining steps:

1. Push to GitHub (the canonical home). The `CITATION.cff` gives you a "Cite
   this repository" button automatically. A SourceHut mirror at
   `git.sr.ht/~<user>/shoalkit` is fine, but Zenodo archiving (below) is driven
   off the GitHub repo.
3. Log in to [Zenodo](https://zenodo.org) with GitHub, flip the toggle on for
   this repository under *Account → GitHub*.
4. Cut a release on GitHub (e.g. `v0.1.0`). Zenodo archives the tagged source
   and mints a DOI, reading `.zenodo.json` for the metadata (including your
   ORCID, which links the record to your ORCID profile).
5. Paste the **concept DOI** back into `CITATION.cff` (`doi:` field) and the
   README badge, then push — so every future release cites consistently.

To deposit the interactive HTML as a **separate** artifact instead of bundling
it, upload `web/wave-calculator.html` as its own Zenodo record and link the two
with a *isSupplementTo* / *isSourceOf* related-identifier pair.

## Acknowledgments

This little tool exists because of people who made waves *click* for me.

- **Pam Borman**, my physics instructor at BCIT, who introduced me to Dr. John
  N. Shive's 1959 Bell Labs film *Similarities of Wave Behavior* — the clearest
  half hour ever put to film on dispersion, reflection, and standing waves, and
  the reason a `tanh(kh)` curve feels like something you can actually see.
- **Dr. John N. Shive** (Bell Telephone Laboratories), for that film and the
  coupled-oscillator "Shive wave machine" behind it.
- **A. Spicer Bak**, whose conversations got me looking far more closely at how
  waves really behave as they shoal and break across a beachface — the part of
  the problem this package is meant to help reason about.
- **COMREN / the Ocean Mapping group** ([oceanmapping.ca](https://oceanmapping.ca)),
  for funding my travel to CHC 2026.
- **James Cowan**, for arranging the many moving pieces — COMREN, the
  conference, and BCIT funding and permission — that made that trip possible.

Any errors are mine, not theirs.

## References

- R. G. Dean & R. A. Dalrymple, *Water Wave Mechanics for Engineers and
  Scientists*, World Scientific.
- F. Ursell (1953); T. S. Hedges (1995); B. Le Méhauté (1976).
- J. N. Shive, *Similarities of Wave Behavior* (Bell Telephone Laboratories,
  1959) — coupled-pendulum demonstration of dispersion, reflection, and
  transmission.
- `raschii` — T. Skomedal, nonlinear regular wave construction.

## License

MIT.
