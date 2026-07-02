---
title: 'shoalkit: linear and Stokes wave transformation with Lagrangian drift'
tags:
  - Python
  - ocean waves
  - coastal engineering
  - Stokes drift
  - wave shoaling
authors:
  - name: Kevin Griffin
    orcid: 0009-0005-0439-6684
    affiliation: 1
affiliations:
  - name: Geomatics - Surveying & Mapping, British Columbia Institute of Technology, Burnaby, BC, Canada
    index: 1
date: 2 July 2026
bibliography: paper.bib
---

# Summary

Coastal and ocean-engineering calculations routinely need the *wave field* at a
point: its length, speed, and how it changes (shoals and refracts) as it
approaches shore. `shoalkit` computes these from linear (Airy) and Stokes wave
theory, reproducing the output set of the University of Delaware / CACR "Wave
Calculator" while adding a transparent wave-theory applicability gate.

Many downstream questions, however, are not about the field at a fixed point but
about *transport*: where a drifting buoy, a spill, a plastic fragment, or a larva
is carried over many wave periods. That transport is the **Stokes drift** — the
small, systematic forward motion a fluid parcel accumulates because its orbit
does not quite close [@Stokes1847; @LonguetHiggins1953]. `shoalkit` provides the
closed-form drift profile, the depth-integrated transport, and a dependency-free
Lagrangian particle integrator, turning an Eulerian wave calculator into one that
also answers the Lagrangian question, and providing a reference prediction that
field drifters can be validated against.

![Over six wave periods, fluid parcels trace open orbits that creep forward at
the Stokes-drift rate (left; open circles mark start positions, filled circles
end positions); the closed-form drift profile $u_s(z)$ falls off from surface to
bed (right; markers are the per-depth predictions used to seed the parcels).
Transitional-water wave, $H=1.6$ m, $T=6$ s, $h=8$ m. Static frame of the
animation produced by `examples/drift_animation.py`.](../docs/drift_figure.png)

# Statement of need

Wave calculators in the CACR/Delaware lineage report orbital *velocity
amplitude* but not the *mean drift* — the second-order (in wave steepness)
Lagrangian quantity. Users who need drift re-derive it ad hoc.

Open Lagrangian drifters (OpenMetBuoy, microSWIFT, SFY, and the author's
Lagrangian Wave Interrogator platform) measure net transport in the field, but
there is no lightweight, citable, dependency-free predictor to check them
against. `shoalkit`'s `mean_drift_velocity` output is directly comparable to the
net Lagrangian velocity a GNSS-tracked drifter reports.

Full-featured particle-tracking stacks such as Parcels [@Delandmeter2019;
@vanSebille2017] and spectral wave models are aimed at basin- and regional-scale
simulation, not a single analytic wave. `shoalkit` fills the "one wave, exact,
in a notebook or a browser" niche; drift is the natural companion to its existing
orbital-velocity output, and the transport it computes governs the fate of
floating material in the ocean [@vanSebille2020].

# Functionality

- `stokes_drift(state, z)` — closed-form drift profile
  $u_s(z) = a^2\,\omega\,k\,\cosh(2k(z+h)) / (2\sinh^2 kh)$, $a=H/2$.
- `stokes_transport(state)` — depth-integrated $Q_s = (a^2\omega/2)\coth(kh)$.
- `mean_drift_velocity(state)` — $Q_s/h$, one scalar for buoy comparison.
- `particle_track(state, z0, ...)` — RK4 integration of a parcel through the
  Airy orbital field, producing the open, forward-creeping orbit whose net
  velocity converges to `stokes_drift` as steepness vanishes.

The theoretical bridge between the Eulerian field and the Lagrangian-mean flow
is the Generalized Lagrangian Mean [@Andrews1978]; the modern synthesis of
Stokes drift is @vandenBremer2017. The closed forms are standard-library only,
consistent with `shoalkit`'s zero-dependency core [@Dean1991].

# Verification

The test suite checks: (1) the deep-water surface-drift limit
$u_s(0)\to\omega k a^2$; (2) the transport identity $Q_s = E/(\rho C)$ to machine
precision; (3) monotonic decay of drift with depth; and (4) convergence of the
Lagrangian particle track's net velocity to the closed-form drift as wave
steepness decreases.

# AI-assistance statement

Parts of this work were carried out with the assistance of Claude Science
(Anthropic), accessed July 2026. Specifically, the tool helped draft the
`stokes_drift`, `stokes_transport`, `mean_drift_velocity`, and `particle_track`
implementations in `drift.py`; ran the literature search behind the reference
list using the OpenAlex and arXiv APIs; and generated the drift animation.

The author reviewed and is responsible for all of it. Every DOI in the
bibliography was checked against its OpenAlex record; the drift derivations were
verified against closed-form limits (the deep-water surface drift $\omega k a^2$
and the transport identity $Q_s = E/(\rho C)$) and against the convergence of
the Lagrangian particle track to the closed form as steepness vanishes; and the
implementation's correctness is exercised by the repository's automated test
suite. The tool is disclosed here as an assistant, not an author: it cannot take
responsibility for the work, and does not.

# Acknowledgements

`shoalkit` descends from the CACR/University of Delaware Wave Calculator
(R. A. Dalrymple), and bridges to `raschii` for higher-order waves.

# References
