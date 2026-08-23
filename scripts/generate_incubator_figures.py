"""Generate deterministic documentation figures from the executed incubator artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PALETTE = {
    "baseline": "#1769aa",
    "sensitivity": "#b24b1b",
    "pre": "#7f8c8d",
    "logical": "#6c3483",
    "coherence": "#168f68",
    "graph": "#303030",
    "collapse": "#d62828",
}


def _scenario_by_name(document: dict, name: str) -> dict:
    return next(item for item in document["scenarios"] if item["name"] == name)


def _series(scenario: dict, path: list[str]):
    values = []
    for step in scenario["steps"]:
        value = step
        for key in path:
            value = value[key]
        values.append(value)
    return values


def _finite(values: list[float | None]) -> tuple[np.ndarray, np.ndarray]:
    indexes = np.asarray([index for index, value in enumerate(values) if value is not None], dtype=int)
    numbers = np.asarray([float(value) for value in values if value is not None], dtype=float)
    return indexes, numbers


def _summary(scenario: dict) -> dict:
    steps = scenario["steps"]
    entropy = _series(scenario, ["density", "entropy_bits"])
    logical_psig = _series(scenario, ["topology", "logical_P_sig"])
    graph_psig = _series(scenario, ["topology", "graph_P_sig"])
    tension = _series(scenario, ["eth", "logical_tension"])
    graph_tension = _series(scenario, ["eth", "graph_tension"])
    eth_rate = _series(scenario, ["eth", "eth_rate_bits_per_step"])
    collapse_steps = [step["step"] for step in steps if step["eth"]["collapse_condition_met"]]
    intervention_steps = [step["step"] for step in steps if step["intervention"]["applied"]]
    tension_values = [float(value) for value in tension if value is not None]
    eth_values = [float(value) for value in eth_rate if value is not None]
    return {
        "name": scenario["name"],
        "n_steps": len(steps),
        "entropy_bits_initial": float(entropy[0]),
        "entropy_bits_final": float(entropy[-1]),
        "entropy_bits_max": float(max(entropy)),
        "entropy_bits_net_change": float(entropy[-1] - entropy[0]),
        "eth_rate_min": None if not eth_values else float(min(eth_values)),
        "eth_rate_max": None if not eth_values else float(max(eth_values)),
        "graph_psig_unique_values": sorted({float(value) for value in graph_psig}),
        "logical_psig_initial": logical_psig[0],
        "logical_psig_final": logical_psig[-1],
        "logical_psig_min": min(logical_psig),
        "logical_psig_max": max(logical_psig),
        "logical_tension_max": None if not tension_values else float(max(tension_values)),
        "graph_tension_unavailable_steps": [step["step"] for step in steps if step["eth"]["graph_tension"] is None],
        "collapse_condition_steps": collapse_steps,
        "intervention_applied_steps": intervention_steps,
        "temperature_millikelvin": scenario["profile"]["temperature_millikelvin"],
        "temperature_role": "metadata_only_not_used_to_derive_aer_parameters",
    }


def build_figures(document: dict, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    baseline = _scenario_by_name(document, "baseline_observational")
    sensitivity = _scenario_by_name(document, "lct_eth_sensitivity_local_dephasing")
    steps = np.arange(len(baseline["steps"]))

    base_entropy = np.asarray(_series(baseline, ["density", "entropy_bits"]), dtype=float)
    sens_entropy = np.asarray(_series(sensitivity, ["density", "entropy_bits"]), dtype=float)
    sens_pre_entropy = np.asarray(_series(sensitivity, ["pre_intervention_density", "entropy_bits"]), dtype=float)
    base_rates = _series(baseline, ["eth", "eth_rate_bits_per_step"])
    sens_tension = _series(sensitivity, ["eth", "logical_tension"])
    collapse_steps = [step["step"] for step in sensitivity["steps"] if step["eth"]["collapse_condition_met"]]

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True, layout="constrained")
    axes[0].plot(steps, base_entropy, marker="o", color=PALETTE["baseline"], label="Baseline observationnelle")
    axes[0].plot(steps, sens_pre_entropy, marker="s", linestyle="--", color=PALETTE["pre"], label="Sensibilité avant intervention")
    axes[0].plot(steps, sens_entropy, marker="D", color=PALETTE["sensitivity"], label="Sensibilité après intervention")
    for step in collapse_steps:
        axes[0].axvline(step, color=PALETTE["collapse"], linewidth=1.0, alpha=0.32)
    axes[0].set_ylabel("Entropie de von Neumann (bits)")
    axes[0].set_title("Incubateur COSMOS — entropie calculée et scénario séparé")
    axes[0].grid(alpha=0.25)
    axes[0].legend(loc="upper left", frameon=False)

    rate_x, rate_y = _finite(base_rates)
    tension_x, tension_y = _finite(sens_tension)
    axes[1].plot(rate_x, rate_y, marker="o", color=PALETTE["baseline"], label="Taux ETH baseline (bits/pas)")
    axes[1].plot(tension_x, tension_y, marker="D", color=PALETTE["logical"], label="Tension logique, sensibilité")
    axes[1].axhline(1.0, color=PALETTE["collapse"], linestyle="--", linewidth=1.0, label="Seuil candidat = 1")
    for step in collapse_steps:
        axes[1].axvline(step, color=PALETTE["collapse"], linewidth=1.0, alpha=0.32)
    axes[1].set_xlabel("Pas de porte")
    axes[1].set_ylabel("Valeur calculée")
    axes[1].grid(alpha=0.25)
    axes[1].legend(loc="upper left", frameon=False)
    entropy_path = output_dir / "incubator-entropy-eth.png"
    fig.savefig(entropy_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

    graph_psig = np.asarray(_series(baseline, ["topology", "graph_P_sig"]), dtype=float)
    logical_psig = np.asarray(_series(baseline, ["topology", "logical_P_sig"]), dtype=float)
    logical_coherence = np.asarray(_series(baseline, ["topology", "logical_coherence"]), dtype=float)
    logical_lct = np.asarray(_series(baseline, ["lct", "lct_factor_logical"]), dtype=float)
    phase = np.asarray(_series(baseline, ["lct", "phase_signed"]), dtype=float)
    graph_tension = _series(baseline, ["eth", "graph_tension"])

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True, layout="constrained")
    axes[0].plot(steps, graph_psig, marker="o", color=PALETTE["graph"], label="P_sig graphe")
    axes[0].plot(steps, logical_psig, marker="D", color=PALETTE["logical"], label="P_sig logique (sidecar)")
    axes[0].plot(steps, logical_coherence, marker="s", color=PALETTE["coherence"], label="Cohérence logique (sidecar)")
    axes[0].set_ylabel("Signature / cohérence")
    axes[0].set_title("Incubateur COSMOS — plans topologiques conservés séparément")
    axes[0].grid(alpha=0.25)
    axes[0].legend(loc="lower left", frameon=False)

    axes[1].plot(steps, phase, marker="o", color=PALETTE["graph"], label="Phase LCT signée")
    axes[1].plot(steps, logical_lct, marker="D", color=PALETTE["logical"], label="Facteur LCT logique")
    graph_unavailable = [index for index, value in enumerate(graph_tension) if value is None]
    axes[1].scatter(graph_unavailable, np.zeros(len(graph_unavailable)), marker="x", color=PALETTE["collapse"], label="Tension graphe indisponible")
    axes[1].axhline(0.0, color="#777777", linewidth=0.8)
    axes[1].set_xlabel("Pas de porte")
    axes[1].set_ylabel("Phase / facteur")
    axes[1].grid(alpha=0.25)
    axes[1].legend(loc="lower left", frameon=False)
    topology_path = output_dir / "incubator-topology-lct.png"
    fig.savefig(topology_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

    return {
        "figures": [str(entropy_path), str(topology_path)],
        "scenarios": [_summary(baseline), _summary(sensitivity)],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create figures from a COSMOS incubator JSON artifact.")
    parser.add_argument("--input", default="artifacts/incubator_lct_eth_run.json")
    parser.add_argument("--output-dir", default="docs/assets")
    parser.add_argument("--summary", default="artifacts/incubator_lct_eth_summary.json")
    args = parser.parse_args()
    document = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = build_figures(document, Path(args.output_dir))
    Path(args.summary).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(result['figures'])} figures and {args.summary}.")


if __name__ == "__main__":
    main()
