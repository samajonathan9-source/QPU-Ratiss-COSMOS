"""Render documentation figures from a completed COSMOS artifact only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


PALETTE = {"ink": "#07111c", "panel": "#102433", "mint": "#42d6ad", "blue": "#79b8ff", "coral": "#ff927d", "text": "#eaf2f8", "muted": "#9bb0bf"}


def style(axis) -> None:
    axis.set_facecolor(PALETTE["panel"])
    axis.tick_params(colors=PALETTE["muted"])
    axis.xaxis.label.set_color(PALETTE["text"])
    axis.yaxis.label.set_color(PALETTE["text"])
    axis.title.set_color(PALETTE["text"])
    for spine in axis.spines.values():
        spine.set_color("#315063")
    axis.grid(alpha=0.18, color="#9bb0bf")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="artifacts/cosmos_run.json")
    parser.add_argument("--output-dir", default="docs/assets")
    args = parser.parse_args()
    document = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": PALETTE["ink"], "savefig.facecolor": PALETTE["ink"]})

    scaling = document["counts_scaling"]
    sizes = [item["n_qubits"] for item in scaling]
    ideal = [item["ideal_dominant_mass"] for item in scaling]
    noisy = [item["noisy_dominant_mass"] for item in scaling]
    fig, axis = plt.subplots(figsize=(8.6, 4.8))
    style(axis)
    axis.plot(sizes, ideal, marker="o", linewidth=2.6, color=PALETTE["mint"], label="Aer idéal")
    axis.plot(sizes, noisy, marker="o", linewidth=2.6, color=PALETTE["coral"], label="Aer bruité — CX p=0.02")
    axis.set_title("COSMOS — masse dominante observée dans les counts GHZ")
    axis.set_xlabel("Nombre de qubits")
    axis.set_ylabel("Masse du résultat le plus fréquent")
    axis.set_ylim(0.0, 0.65)
    legend = axis.legend(frameon=False)
    for text in legend.get_texts(): text.set_color(PALETTE["text"])
    fig.tight_layout()
    fig.savefig(output / "cosmos-counts-scaling.png", dpi=180)
    plt.close(fig)

    stages = document["density_topology"]["steps"]
    index = list(range(len(stages)))
    coherence = [stage["logical_topology"]["coherence"] for stage in stages]
    psig = [stage["logical_topology"]["P_sig"] for stage in stages]
    labels = [stage["gate"] for stage in stages]
    fig, left = plt.subplots(figsize=(9.4, 4.8))
    style(left)
    right = left.twinx()
    right.tick_params(colors=PALETTE["muted"])
    right.spines["right"].set_color("#315063")
    left.plot(index, coherence, marker="o", linewidth=2.4, color=PALETTE["blue"], label="Cohérence logique")
    right.plot(index, psig, marker="D", linewidth=2.4, color=PALETTE["mint"], label="P sig logique")
    left.set_title("COSMOS — sidecar logique RATISS par porte du programme densité")
    left.set_xlabel("Étape de porte")
    left.set_ylabel("Cohérence logique")
    right.set_ylabel("P sig logique", color=PALETTE["text"])
    left.set_xticks(index, labels, rotation=35, ha="right")
    lines = left.lines + right.lines
    legend = left.legend(lines, [line.get_label() for line in lines], loc="upper right", frameon=False)
    for text in legend.get_texts(): text.set_color(PALETTE["text"])
    fig.tight_layout()
    fig.savefig(output / "cosmos-density-sidecar.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
