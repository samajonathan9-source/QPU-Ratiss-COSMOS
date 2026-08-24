"""Validate the RATISS sidecar against a real IBM Quantum QPU.

Submits a minimal two-qubit Bell-state circuit to a real hardware backend,
stores the counts and the traceable Job ID, and compares the LCT divergence
between the local Aer simulation and the observed hardware outcome.

The IBM token is read from the IBM_QUANTUM_TOKEN environment variable only;
it is never written into the artifact, the repository or any log line.

Frontiere de revendication : on compare la simulation au materiel reel, on ne
certifie pas le materiel, et le Reality Flag reste une condition de simulation.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any


def _engine(engine_src: str | None):
    candidate = engine_src or os.environ.get("RATISS_ENGINE_SRC")
    if candidate:
        sys.path.insert(0, str(Path(candidate).expanduser().resolve()))
    try:
        from ratiss_topological_decoherence.correlation_import import run_qiskit_counts_trajectory
        from ratiss_topological_decoherence.logical_qubit import TopologicalQubit
    except ImportError as error:
        raise RuntimeError("Set RATISS_ENGINE_SRC or --engine-src to the engine src directory.") from error
    return TopologicalQubit, run_qiskit_counts_trajectory


def build_bell_circuit():
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(2, 2, name="bell_validation")
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure(0, 0)
    circuit.measure(1, 1)
    return circuit


def _marked_mass(counts: dict[str, int], marked: str = "11") -> float:
    total = sum(counts.values())
    return 0.0 if total == 0 else counts.get(marked, 0) / total


def _ideal_counts(shots: int, seed: int) -> dict[str, int]:
    """Deterministic ideal Bell-state counts (|00> and |11> equiprobable)."""
    half = shots // 2
    return {"00": half, "11": shots - half}


def run_aer(circuit, *, shots: int, seed: int) -> dict[str, int]:
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    noise = NoiseModel()
    noise.add_all_qubit_quantum_error(depolarizing_error(0.02, 2), ["cx"])
    simulator = AerSimulator(noise_model=noise, seed_simulator=seed)
    compiled = transpile(circuit, simulator, optimization_level=0, seed_transpiler=seed)
    counts = simulator.run(compiled, shots=shots, seed_simulator=seed).result().get_counts()
    return {str(k): int(v) for k, v in counts.items()}


def run_qpu(circuit, *, backend_name: str, shots: int) -> tuple[dict[str, int], str, str]:
    """Submit once to a real IBM QPU. Returns (counts, job_id, backend_name)."""
    token = os.environ.get("IBM_QUANTUM_TOKEN")
    if not token:
        raise RuntimeError("IBM_QUANTUM_TOKEN environment variable is required for QPU validation.")
    from qiskit_ibm_runtime import QiskitRuntimeService
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2 as Sampler

    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    backend = service.backend(backend_name)
    compiled = transpile(circuit, backend, optimization_level=1)
    sampler = Sampler(mode=backend)
    job = sampler.run([(compiled,)], shots=shots)
    job_id = job.job_id() if callable(getattr(job, "job_id", None)) else job.job_id
    result = job.result()
    pubs = result[0].data
    # The measurement register may be named c0/c1; take the first available.
    field = next(iter(pubs.__dict__))
    raw = pubs.__dict__[field].get_counts()
    counts = {str(k): int(v) for k, v in raw.items()}
    return counts, job_id, backend.name


def sidecar_pair(TopologicalQubit: Any, *, observed_degradation: float, seed: int) -> tuple[dict[str, Any], dict[str, Any]]:
    expected = TopologicalQubit(seed=seed)
    observed = TopologicalQubit(seed=seed)
    expected.h_gate().phase_gate(math.pi / 3)
    observed.h_gate().phase_gate(math.pi / 3).noise(observed_degradation)
    return expected.measure_state(), observed.measure_state()


def lct_divergence(*, ideal_mass: float, observed_mass: float, expected_sidecar: dict, observed_sidecar: dict) -> dict[str, Any]:
    mass_gap = abs(ideal_mass - observed_mass)
    expected_psig = float(expected_sidecar["P_sig"])
    observed_psig = float(observed_sidecar["P_sig"])
    psig_gap = abs(expected_psig - observed_psig)
    scale = max(abs(expected_psig * float(expected_sidecar["coherence"])), 1e-12)
    return {
        "ideal_marked_mass": ideal_mass,
        "observed_marked_mass": observed_mass,
        "marked_mass_gap": mass_gap,
        "expected_sidecar_P_sig": expected_psig,
        "observed_sidecar_P_sig": observed_psig,
        "sidecar_P_sig_gap": psig_gap,
        "lct_divergence": (mass_gap * psig_gap) / scale,
    }


def run_validation(engine_src: str | None, *, backend_name: str, shots: int, seed: int) -> dict[str, Any]:
    from counts_diagnostic import counts_diagnostic

    TopologicalQubit, run_qiskit_counts_trajectory = _engine(engine_src)
    circuit = build_bell_circuit()
    ideal_counts = _ideal_counts(shots, seed)
    aer_counts = run_aer(circuit, shots=shots, seed=seed)
    qpu_counts, job_id, backend_name = run_qpu(circuit, backend_name=backend_name, shots=shots)

    ideal_mass = _marked_mass(ideal_counts)
    aer_mass = _marked_mass(aer_counts)
    qpu_mass = _marked_mass(qpu_counts)

    aer_degradation = 0.0 if ideal_mass == 0.0 else max(0.0, min(1.0, (ideal_mass - aer_mass) / ideal_mass))
    qpu_degradation = 0.0 if ideal_mass == 0.0 else max(0.0, min(1.0, (ideal_mass - qpu_mass) / ideal_mass))

    expected_sidecar, aer_sidecar = sidecar_pair(TopologicalQubit, observed_degradation=aer_degradation, seed=seed)
    _, qpu_sidecar = sidecar_pair(TopologicalQubit, observed_degradation=qpu_degradation, seed=seed)

    aer_div = lct_divergence(ideal_mass=ideal_mass, observed_mass=aer_mass,
                             expected_sidecar=expected_sidecar, observed_sidecar=aer_sidecar)
    qpu_div = lct_divergence(ideal_mass=ideal_mass, observed_mass=qpu_mass,
                             expected_sidecar=expected_sidecar, observed_sidecar=qpu_sidecar)

    aer_diagnostic = counts_diagnostic(ideal_counts, aer_counts, marked="11")
    qpu_diagnostic = counts_diagnostic(ideal_counts, qpu_counts, marked="11")

    qpu_association = run_qiskit_counts_trajectory({
        "source": {"mode": "cosmos_qpu_validation", "backend": backend_name, "job_id": job_id},
        "trajectory": [{"step": 0, "label": "qpu_bell_counts", "counts": qpu_counts}],
    })
    qpu_counts_psig = qpu_association["steps"][0]["topology"]["psig"]

    return {
        "schema": "ratiss.cosmos.qpu_validation.v1",
        "provenance": {
            "execution": "ibm_quantum_platform_qpu_submission",
            "validated_on_hardware": True,
            "claim_boundary": "One real QPU shot set compared to local Aer simulation; the Reality Flag compares, it does not certify hardware.",
            "backend": backend_name,
            "job_id": job_id,
            "shots": shots,
            "seed": seed,
        },
        "circuit": {"name": circuit.name, "n_qubits": 2, "gates": ["h(0)", "cx(0,1)", "measure"]},
        "marked_state": "11",
        "ideal": {"counts": ideal_counts, "marked_mass": ideal_mass},
        "aer": {"counts": aer_counts, "marked_mass": aer_mass, "divergence": aer_div, "counts_diagnostic": aer_diagnostic},
        "qpu": {
            "counts": qpu_counts,
            "marked_mass": qpu_mass,
            "divergence": qpu_div,
            "counts_diagnostic": qpu_diagnostic,
            "counts_association_P_sig": qpu_counts_psig,
            "counts_association_scope": "classical_counts_association_not_density_matrix_tomography",
        },
        "comparison": {
            "aer_lct_divergence": aer_div["lct_divergence"],
            "qpu_lct_divergence": qpu_div["lct_divergence"],
            "qpu_vs_aer_divergence_ratio": None if aer_div["lct_divergence"] == 0 else qpu_div["lct_divergence"] / aer_div["lct_divergence"],
            "message": "Local Aer simulation and real QPU outcome are recorded side by side; neither is substituted for the other.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the RATISS sidecar against a real IBM QPU.")
    parser.add_argument("--engine-src")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--output", default="artifacts/qpu_validation.json")
    parser.add_argument("--shots", type=int, default=512)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    document = run_validation(args.engine_src, backend_name=args.backend, shots=args.shots, seed=args.seed)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(document, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {destination} — QPU Job ID: {document['provenance']['job_id']}")


if __name__ == "__main__":
    main()
