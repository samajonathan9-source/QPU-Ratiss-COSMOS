"""Generate the COSMOS studio brand assets deterministically.

The logo encodes the pipeline: a five-node correlation ring whose persistence
forms the H1 cycle (outer mint ring and chords), a density-matrix core
(coherence spiral), and three orbital markers for the Q x I x M tryperposition
channel. Rendered with matplotlib only, from code, so the brand is reproducible.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

INK = "#07111c"
PANEL = "#0d1f2d"
MINT = "#42d6ad"
BLUE = "#79b8ff"
CORAL = "#ff927d"
MUTED = "#9bb0bf"


def build_logo(destination: Path) -> None:
    fig = plt.figure(figsize=(6.4, 6.4), facecolor=INK)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    ax.axis("off")

    # Outer correlation ring: nodes whose persistence is the H1 cycle.
    n = 5
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False) + np.pi / 2
    xs = 0.98 * np.cos(ang)
    ys = 0.98 * np.sin(ang)

    theta = np.linspace(0, 2 * np.pi, 300)
    for lw, alpha in [(14, 0.05), (9, 0.10), (5, 0.18)]:
        ax.plot(1.02 * np.cos(theta), 1.02 * np.sin(theta), color=MINT, lw=lw, alpha=alpha, solid_capstyle="round", zorder=1)
    ax.plot(1.02 * np.cos(theta), 1.02 * np.sin(theta), color=MINT, lw=1.6, alpha=0.85, zorder=2)

    # Correlation chords between qubit nodes.
    for i in range(n):
        for j in range(i + 1, n):
            ax.plot([xs[i], xs[j]], [ys[i], ys[j]], color=BLUE, lw=1.0, alpha=0.16, zorder=2)

    ax.scatter(xs, ys, s=210, color=MINT, edgecolor=INK, linewidth=2.0, zorder=5)
    ax.scatter(xs, ys, s=60, color=INK, zorder=6)

    # Density-matrix core with a coherence spiral.
    ax.add_patch(Circle((0, 0), 0.44, facecolor=PANEL, edgecolor=MUTED, lw=1.2, alpha=0.95, zorder=7))
    t = np.linspace(0, 4 * np.pi, 400)
    r = 0.06 + 0.30 * t / (4 * np.pi)
    ax.plot(r * np.cos(t), r * np.sin(t), color=CORAL, lw=2.2, alpha=0.95, zorder=8)
    ax.scatter([0], [0], s=70, color=MINT, edgecolor=INK, lw=1.5, zorder=9)

    # Three orbital markers = the Q x I x M tryperposition channel.
    for k, color in enumerate([MINT, BLUE, CORAL]):
        a0 = ang[k % n] + (k * 2 * np.pi / 3)
        ax.scatter([1.18 * np.cos(a0)], [1.18 * np.sin(a0)], s=95, color=color, edgecolor=INK, lw=1.5, zorder=10)

    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=200, facecolor=INK)
    plt.close(fig)


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "docs" / "brand"
    build_logo(out / "cosmos-logo.png")
    print(f"Wrote {out / 'cosmos-logo.png'}")


if __name__ == "__main__":
    main()
