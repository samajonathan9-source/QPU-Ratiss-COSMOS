"""COSMOS: local Aer counts scaling plus the source RATISS density trajectory.

The script does not submit a QPU job.  It stores every simulated count and
every RATISS result that it receives.  In particular it never replaces a zero
or low P_sig by a preferred value.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np


def _load_ratiss_engine(engine_src: str | None) -> tuple[Any, Any, Any, Any]:
    candidate = engine_src or os.environ.get("RATISS_ENGINE_SRC")
    if candidate:
        sys.path.insert(0, str(Path(candidate).expanduser().resolve()))
    try:
        from ratiss_topological_decoherence.correlation_import import run_qiskit_counts_trajectory
        from ratiss_topological_decoherence.simulation import GateSpec, SimulationConfig, run_program
    except ImportError as error:
        raise RuntimeError(
            "RATISS engine unavailable. Set RATISS_ENGINE_SRC to the engine src directory, "
            "for example ../ratiss-topological-decoherence-engine/src."
        ) from error
    return run_qiskit_counts_trajectory, GateSpec, SimulationConfig, run_program


def build_prefix_circuit(n_qubits: int, depth: int):
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(n_qubits)
    circuit.h(0)
    for control in range(min(depth, n_qubits - 1)):
        circuit.cx(control, control + 1)
    circuit.measure_all()
    return circuit


def run_counts(circuit, *, depolarizing_probability: float, shots: int, seed: int) -> dict[str, int]:
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    noise = NoiseModel()
    noise.add_all_qubit_quantum_error(depolarizing_error(depolarizing_probability, 2), ["cx"])
    simulator = AerSimulator(method="stabilizer", noise_model=noise, seed_simulator=seed)
    compiled = transpile(circuit, simulator, seed_transpiler=seed, optimization_level=0)
    result = simulator.run(compiled, shots=shots, seed_simulator=seed).result()
    return {str(key): int(value) for key, value in result.get_counts().items()}


def _dominant_mass(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    return 0.0 if total == 0 else max(counts.values()) / total


def run_counts_scaling(
    run_qiskit_counts_trajectory: Any,
    *, sizes: list[int], shots: int, noise: float, seed: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for n_qubits in sizes:
        depth = n_qubits - 1
        circuit = build_prefix_circuit(n_qubits, depth)
        ideal = run_counts(circuit, depolarizing_probability=0.0, shots=shots, seed=seed)
        noisy = run_counts(circuit, depolarizing_probability=noise, shots=shots, seed=seed)
        timeline = run_qiskit_counts_trajectory({
            "source": {
                "experiment": "COSMOS counts_scaling",
                "backend": "local_qiskit_aer_stabilizer",
                "noise_model": "declared_cx_depolarizing",
                "depolarizing_probability": noise,
                "validated_on_hardware": False,
            },
            "bit_order": "qiskit_little_endian",
            "trajectory": [
                {"step": 0, "label": "ideal_counts", "counts": ideal},
                {"step": 1, "label": "noisy_counts", "counts": noisy},
            ],
        })
        records.append({
            "n_qubits": n_qubits,
            "cx_depth": depth,
            "shots": shots,
            "ideal_counts": ideal,
            "noisy_counts": noisy,
            "ideal_dominant_mass": _dominant_mass(ideal),
            "noisy_dominant_mass": _dominant_mass(noisy),
            "ratiss_counts_timeline": timeline,
        })
    return records


def run_density_topology(GateSpec: Any, SimulationConfig: Any, run_program: Any) -> dict[str, Any]:
    gates = [
        GateSpec("h", (0,)), GateSpec("cx", (0, 1)), GateSpec("cx", (1, 2)),
        GateSpec("h", (3,)), GateSpec("cx", (3, 4)), GateSpec("cx", (4, 0)),
        GateSpec("cz", (2, 3)),
    ]
    config = SimulationConfig(
        n_qubits=5,
        scenario="cosmos_five_qubit_density_topology",
        one_qubit_depolarizing=0.001,
        two_qubit_depolarizing=0.01,
    )
    return run_program(
        gates,
        config,
        provenance_mode="local_cosmos_density_simulation",
        encoding={
            "profile": "cosmos_distributed_logical_state",
            "description": "Five-qubit density-matrix trajectory coupled to the source-derived RATISS logical sidecar.",
            "hardware_claim": "none",
            "logical_core": {
                "source": "RATISS Experimental IA/decoherence-map:c67d2e7",
                "scope": "algorithmic_topological_logical_qubit_simulation",
            },
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local COSMOS RATISS experiment.")
    parser.add_argument("--engine-src", help="Path to ratiss-topological-decoherence-engine/src.")
    parser.add_argument("--output", default="artifacts/cosmos_run.json")
    parser.add_argument("--sizes", default="8,12,16,20")
    parser.add_argument("--shots", type=int, default=512)
    parser.add_argument("--noise", type=float, default=0.02)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if not 0.0 <= args.noise <= 1.0:
        raise ValueError("--noise must be in [0, 1].")
    sizes = [int(value) for value in args.sizes.split(",") if value.strip()]
    if not sizes or min(sizes) < 2:
        raise ValueError("--sizes must contain qubit counts >= 2.")
    run_counts_adapter, GateSpec, SimulationConfig, run_program = _load_ratiss_engine(args.engine_src)
    output = {
        "schema": "ratiss.cosmos.run.v1",
        "provenance": {
            "execution": "local_qiskit_aer_simulation",
            "validated_on_hardware": False,
            "claim_boundary": "Simulation artifacts only; no QPU execution or physical topological-qubit claim.",
            "seed": args.seed,
        },
        "counts_scaling": run_counts_scaling(run_counts_adapter, sizes=sizes, shots=args.shots, noise=args.noise, seed=args.seed),
        "density_topology": run_density_topology(GateSpec, SimulationConfig, run_program),
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {destination} with {len(output['counts_scaling'])} counts regimes.")


if __name__ == "__main__":
    main()
