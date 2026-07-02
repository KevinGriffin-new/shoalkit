"""Lagrangian drift animation: the transport an Eulerian wave calculator hides.

Renders a side-by-side view of a wave field:
  * left  -- fluid parcels riding open orbits that creep forward (Stokes drift)
  * right -- the drift profile u_s(z), falling off from surface to bed

Regenerates docs/stokes_drift.gif. Requires numpy + matplotlib:
    pip install numpy matplotlib
"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

import shoalkit as sk

FOCAL = "#0B6E4F"      # drift green
WAVE = "#1f6feb"       # surface blue
PARCEL = "#c2410c"     # parcel orange


def main(out="docs/stokes_drift.gif"):
    # A transitional-water wave: elliptical orbits, drift clearly visible.
    st = sk.transform(H0=1.6, T=6.0, h=8.0)

    depths = [0.0, -1.5, -3.0, -5.0, -7.0]
    tracks = [sk.particle_track(st, z0=z, n_periods=6, steps_per_period=180)
              for z in depths]
    zz = np.linspace(-st.h, 0, 200)
    us = np.array(sk.stokes_drift(st, list(zz)))

    fig, (axL, axR) = plt.subplots(
        1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [2.4, 1.0]})

    xmax = st.L * 1.15
    axL.axhline(0, color="0.6", lw=0.8, ls="--", zorder=1)
    axL.axhspan(-st.h - 0.6, -st.h, color="0.85", zorder=0)
    axL.text(xmax * 0.99, -st.h + 0.2, "seabed", ha="right", va="bottom",
             fontsize=7, color="0.4")

    trails = [axL.plot([], [], color=PARCEL, lw=0.9, alpha=0.55, zorder=3)[0]
              for _ in tracks]
    heads = [axL.plot([], [], "o", color=PARCEL, ms=5, zorder=5)[0]
             for _ in tracks]
    for tr in tracks:
        axL.plot(tr["x"][0], tr["z"][0], "o", mfc="none", mec="0.5", ms=5, zorder=2)
    surf, = axL.plot([], [], color=WAVE, lw=2.0, zorder=4)
    xs_surf = np.linspace(0, xmax, 400)

    axL.set_xlim(-2, xmax)
    axL.set_ylim(-st.h - 0.8, st.H)
    axL.set_xlabel("horizontal distance x (m)")
    axL.set_ylabel("elevation z (m, about MWL)")
    axL.set_title("Parcels ride open orbits -- each loop creeps forward (Stokes drift)",
                  fontsize=9, loc="left")

    axR.plot(us, zz, color=FOCAL, lw=2.2)
    axR.fill_betweenx(zz, 0, us, color=FOCAL, alpha=0.12)
    axR.axvline(0, color="0.6", lw=0.8)
    axR.axhline(0, color="0.6", lw=0.8, ls="--")
    for tr, z in zip(tracks, depths):
        axR.plot(tr["drift_predicted"], z, "o", color=PARCEL, ms=5, zorder=5)
    axR.set_xlabel(r"Stokes drift $u_s$ (m/s)")
    axR.set_ylabel("z (m)")
    axR.set_ylim(-st.h - 0.8, st.H)
    axR.set_title("Drift falls off\nwith depth", fontsize=9, loc="left")
    axR.margins(x=0.12)

    fig.suptitle(
        "shoalkit: the Lagrangian drift your Eulerian wave calculator does not show",
        fontsize=10, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.96))

    stride = 6
    frames = range(0, len(tracks[0]["t"]), stride)

    def update(i):
        t = tracks[0]["t"][i]
        surf.set_data(xs_surf, sk.airy_elevation(st, list(xs_surf), t=t))
        for tr, trail, head in zip(tracks, trails, heads):
            trail.set_data(tr["x"][:i + 1], tr["z"][:i + 1])
            head.set_data([tr["x"][i]], [tr["z"][i]])
        return [surf, *trails, *heads]

    anim = FuncAnimation(fig, update, frames=frames, blit=True, interval=50)
    anim.save(out, writer=PillowWriter(fps=20), dpi=110)
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
