"""Execute the RATISS LCT-ETH topological incubator locally.

This module intentionally keeps graph P_sig, logical P_sig, entropy and LCT
terms separate.  It never substitutes a preferred value when a metric is zero
or unavailable.  The optional dephasing profile is an explicitly separate
scenario; the baseline only observes its candidate collapse conditions.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class IncubatorProfile:
    """Declared parameters for one reproducible incubator scenario."""

    name: str
    alpha_0: float
    eta_lct: float
    omega_lct: float
    timestep: float
    collapse_threshold: float
    impact_threshold: float
    apply_local_dephasing: bool
    temperature_millikelvin: float
    temperature_reference_millikelvin: float
    pressure_beta: float
    pressure_gamma: float
    crosstalk_kappa: float


def _load_simulation_module(engine_src: str | None):
    candidate = engine_src or os.environ.get("RATISS_ENGINE_SRC")
    if candidate:
        sys.path.insert(0, str(Path(candidate).expanduser().resolve()))
    try:
        from ratiss_topological_decoherence import simulation
    except ImportError as error:
        raise RuntimeError(
            "RATISS engine unavailable. Set RATISS_ENGINE_SRC to the engine src directory, "
            "for example ../ratiss-topological-decoherence-engine/src."
        ) from error
    return simulation


def von_neumann_metrics(rho: np.ndarray, n_qubits: int) -> dict[str, Any]:
    """Return density-matrix metrics without clipping or replacing observations."""
    hermitian_rho = (rho + rho.conj().T) / 2.0
    eigenvalues = np.linalg.eigvalsh(hermitian_rho).real
    positive = eigenvalues[eigenvalues > 0.0]
    entropy_bits = float(-np.sum(positive * np.log2(positive))) if len(positive) else 0.0
    purity_global = float(np.real(np.trace(rho @ rho)))
    return {
        "entropy_bits": entropy_bits,
        "purity_global": purity_global,
        "density_coherence_proxy": float(1.0 - entropy_bits / n_qubits),
        "trace_real": float(np.real(np.trace(rho))),
        "trace_imaginary": float(np.imag(np.trace(rho))),
        "eigenvalue_sum": float(np.sum(eigenvalues)),
        "negative_eigenvalues": [float(value) for value in eigenvalues if value < 0.0],
        "rho_dimension": int(rho.shape[0]),
    }


def frobenius_gradient(current: np.ndarray, previous: np.ndarray | None, timestep: float) -> float | None:
    """Return the unmodified finite-difference Frobenius norm, or None initially."""
    if previous is None:
        return None
    if timestep <= 0.0:
        raise ValueError("timestep must be strictly positive")
    return float(np.linalg.norm(current - previous, ord="fro") / timestep)


def impact_by_qubit(current: np.ndarray, previous: np.ndarray | None, timestep: float) -> list[float] | None:
    """Compute the per-qubit correlation change used for inspection selection."""
    if previous is None:
        return None
    if timestep <= 0.0:
        raise ValueError("timestep must be strictly positive")
    delta = np.abs(current - previous) / timestep
    return [float(np.sum(delta[index]) - delta[index, index]) for index in range(delta.shape[0])]


def off_diagonal_crosstalk_proxy(correlation_matrix: np.ndarray) -> float:
    """Return a correlation statistic, explicitly not an EM crosstalk measurement."""
    n = correlation_matrix.shape[0]
    if n < 2:
        return 0.0
    mask = ~np.eye(n, dtype=bool)
    return float(np.mean(np.abs(correlation_matrix[mask])))


def tryperposition_signal(
    density: dict[str, Any],
    graph_psig: float,
    logical_psig: float | None,
    correlation_matrix: np.ndarray,
) -> dict[str, Any]:
    """Build the measured Q × I × M channel used by the active incubator path.

    The graph and logical P_sig values remain exported independently.  This is
    not a fallback that overwrites graph P_sig: it is a third, declared signal
    built from the simulated density layer (Q), information/topology layer (I)
    and density-trace integrity witness (M).  It remains evaluable when the
    finite-H1 graph persistence is exactly zero.
    """
    logical_value = 0.0 if logical_psig is None else float(logical_psig)
    correlation_amplitude = off_diagonal_crosstalk_proxy(correlation_matrix)
    quantum_amplitude = float(density["density_coherence_proxy"])
    information_amplitude = float(math.sqrt(graph_psig**2 + logical_value**2 + correlation_amplitude**2))
    material_amplitude = float(1.0 - abs(float(density["trace_real"]) - 1.0))
    psig_tryperposition = float(quantum_amplitude * information_amplitude * material_amplitude)
    return {
        "state": "Psi = Q x I x M",
        "P_sig_tryperposition": psig_tryperposition,
        "quantum_layer_Q": {
            "density_coherence_proxy": quantum_amplitude,
            "purity_global": density["purity_global"],
            "entropy_bits": density["entropy_bits"],
        },
        "information_layer_I": {
            "graph_P_sig": graph_psig,
            "logical_P_sig": logical_psig,
            "correlation_amplitude": correlation_amplitude,
            "information_amplitude": information_amplitude,
        },
        "material_layer_M": {
            "trace_integrity_amplitude": material_amplitude,
            "scope": "density_trace_integrity_proxy_not_cryptographic_proof",
        },
    }


def _tension(stress: float | None, alpha_0: float, reference_psig: float, current_psig: float) -> tuple[float | None, str | None]:
    """Compute the candidate tension without an epsilon fallback for zero P_sig."""
    if stress is None:
        return None, "initial_step_has_no_gradient"
    stable_abscissa = alpha_0 * reference_psig
    if reference_psig == 0.0:
        return None, "reference_psig_is_zero"
    if stable_abscissa == 0.0:
        return None, "stable_abscissa_is_zero"
    if current_psig == 0.0:
        return None, "current_psig_is_zero"
    return float(stress / (stable_abscissa * current_psig)), None


def lct_eth_terms(
    *,
    step: int,
    density: dict[str, Any],
    graph_psig: float,
    logical_psig: float | None,
    logical_coherence: float | None,
    tryperposition_psig: float,
    reference_graph_psig: float,
    reference_logical_psig: float | None,
    reference_tryperposition_psig: float,
    previous_entropy_bits: float | None,
    gradient_frobenius: float | None,
    correlation_matrix: np.ndarray,
    profile: IncubatorProfile,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Calculate candidate LCT and ETH records from already-observed state data."""
    phase_signed = float(math.cos(profile.omega_lct * step * profile.timestep))
    phase_amplitude = float(abs(phase_signed))
    entropy_bits = float(density["entropy_bits"])
    delta_entropy = None if previous_entropy_bits is None else float(entropy_bits - previous_entropy_bits)
    eth_rate = None if delta_entropy is None else float(delta_entropy / profile.timestep)
    stress = None if gradient_frobenius is None else float(gradient_frobenius * (1.0 - density["purity_global"]))
    graph_tension, graph_reason = _tension(stress, profile.alpha_0, reference_graph_psig, graph_psig)
    if logical_psig is None or reference_logical_psig is None:
        logical_tension, logical_reason = None, "logical_psig_not_applicable"
    else:
        logical_tension, logical_reason = _tension(stress, profile.alpha_0, reference_logical_psig, logical_psig)
    tryperposition_tension, tryperposition_reason = _tension(
        stress,
        profile.alpha_0,
        reference_tryperposition_psig,
        tryperposition_psig,
    )
    crosstalk_proxy = off_diagonal_crosstalk_proxy(correlation_matrix)
    pressure = float(
        profile.pressure_beta
        * (profile.temperature_millikelvin / profile.temperature_reference_millikelvin) ** profile.pressure_gamma
        * (1.0 + profile.crosstalk_kappa * crosstalk_proxy)
    )
    # Couplage LCT-ETH stabilisé : ETH module l'amplitude d'apprentissage via
    # exp(-|eth_rate|). Le bain cryogénique virtuel (ETH) calme l'apprentissage
    # quand il est agité (grand |ΔS/Δt|) et l'autorise quand il est calme
    # (|ΔS/Δt|≈0). Ce facteur est strictement positif et borné dans (0,1] : le
    # couplage ne peut ni inverser le signe du gradient ni l'amplifier — il
    # amortit seulement, ce qui garantit la stabilité du facteur d'apprentissage.
    eth_modulation = None if eth_rate is None else float(math.exp(-abs(eth_rate)))
    lct = {
        "measurement_state": "pre_intervention_density",
        "phase_signed": phase_signed,
        "phase_amplitude": phase_amplitude,
        "graph_P_sig": graph_psig,
        "logical_P_sig": logical_psig,
        "P_sig_tryperposition": tryperposition_psig,
        "active_P_sig_channel": "tryperposition",
        "density_coherence_proxy": density["density_coherence_proxy"],
        "logical_coherence": logical_coherence,
        "lct_factor_graph": float(phase_signed * graph_psig * density["density_coherence_proxy"]),
        "lct_factor_logical": None if logical_psig is None or logical_coherence is None else float(phase_signed * logical_psig * logical_coherence),
        "candidate_delta_w_graph": float(profile.eta_lct * phase_signed * graph_psig * density["density_coherence_proxy"]),
        "candidate_delta_w_logical": None if logical_psig is None or logical_coherence is None else float(profile.eta_lct * phase_signed * logical_psig * logical_coherence),
        "lct_factor_tryperposition": float(phase_signed * tryperposition_psig * density["density_coherence_proxy"]),
        "candidate_delta_w_tryperposition": float(profile.eta_lct * phase_signed * tryperposition_psig * density["density_coherence_proxy"]),
        "eth_modulation": eth_modulation,
        "lct_factor_coupled": None if eth_modulation is None else float(phase_signed * tryperposition_psig * density["density_coherence_proxy"] * eth_modulation),
        "candidate_delta_w_coupled": None if eth_modulation is None else float(profile.eta_lct * phase_signed * tryperposition_psig * density["density_coherence_proxy"] * eth_modulation),
        "coupling_scope": "eth_amplitude_modulation_exp_minus_abs_rate_stabilized",
    }
    eth = {
        "measurement_state": "pre_intervention_density",
        "delta_entropy_bits": delta_entropy,
        "eth_rate_bits_per_step": eth_rate,
        "gradient_frobenius": gradient_frobenius,
        "oscillation_stress": stress,
        "graph_tension": graph_tension,
        "graph_tension_unavailable_reason": graph_reason,
        "logical_tension": logical_tension,
        "logical_tension_unavailable_reason": logical_reason,
        "tryperposition_tension": tryperposition_tension,
        "tryperposition_tension_unavailable_reason": tryperposition_reason,
        "active_tension": tryperposition_tension,
        "active_tension_channel": "tryperposition",
        "crosstalk_proxy": crosstalk_proxy,
        "crosstalk_scope": "correlation_statistic_not_electromagnetic_measurement",
        "eth_pressure_indicator": pressure,
        "temperature_role": "profile_metadata_only_not_converted_to_aer_t1_t2",
    }
    return lct, eth


def local_z_dephasing(rho: np.ndarray, qubits: list[int], strength: float, n_qubits: int) -> np.ndarray:
    """Apply a declared local Z-dephasing channel to selected simulated qubits."""
    if not 0.0 <= strength <= 1.0:
        raise ValueError("strength must be in [0, 1]")
    state = np.asarray(rho, dtype=complex).copy()
    identity = np.eye(2, dtype=complex)
    z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    for qubit in qubits:
        operators = [identity for _ in range(n_qubits)]
        operators[qubit] = z
        operator = operators[-1]
        for index in range(n_qubits - 2, -1, -1):
            operator = np.kron(operator, operators[index])
        state = (1.0 - strength) * state + strength * (operator @ state @ operator)
    return state


def _advance_density(rho: np.ndarray, gate: Any, simulation: Any, config: Any, noisy: bool) -> np.ndarray:
    """Advance one density-matrix step with the same Aer gate/noise contract as the engine."""
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    circuit = QuantumCircuit(config.n_qubits)
    circuit.set_density_matrix(rho)
    simulation._apply_gate(circuit, gate)
    circuit.save_density_matrix(label="rho")
    kwargs = {"noise_model": simulation._noise_model(config)} if noisy else {}
    result = AerSimulator(method="density_matrix", **kwargs).run(circuit).result()
    return np.asarray(result.data(0)["rho"], dtype=complex)


def _step_topology(step_artifact: Any) -> tuple[float, float | None, float | None, np.ndarray]:
    exported = step_artifact.to_dict()
    graph_psig = float(exported["topology"]["psig"])
    logical = exported["logical_topology"]
    raw_logical_psig = logical.get("P_sig")
    logical_psig = None if raw_logical_psig is None else float(raw_logical_psig)
    raw_logical_coherence = logical.get("coherence")
    logical_coherence = None if raw_logical_coherence is None else float(raw_logical_coherence)
    return graph_psig, logical_psig, logical_coherence, np.asarray(exported["cube_slice"], dtype=float)


def run_profile(gates: list[Any], config: Any, simulation: Any, profile: IncubatorProfile) -> dict[str, Any]:
    """Run one baseline or explicit-intervention scenario and emit every step."""
    dimension = 2 ** config.n_qubits
    rho_noisy = np.zeros((dimension, dimension), dtype=complex)
    rho_ideal = np.zeros((dimension, dimension), dtype=complex)
    rho_noisy[0, 0] = 1.0
    rho_ideal[0, 0] = 1.0
    positions = simulation.deterministic_positions(config.n_qubits)
    logical_qubit = simulation.TopologicalQubit(seed=42)
    previous_edges: set[tuple[int, int]] = set()
    previous_entropy_bits: float | None = None
    previous_correlation: np.ndarray | None = None
    reference_graph_psig: float | None = None
    reference_logical_psig: float | None = None
    reference_tryperposition_psig: float | None = None
    records: list[dict[str, Any]] = []

    for prefix in range(len(gates) + 1):
        gate = None if prefix == 0 else gates[prefix - 1]
        if gate is not None:
            rho_ideal = _advance_density(rho_ideal, gate, simulation, config, noisy=False)
            rho_noisy = _advance_density(rho_noisy, gate, simulation, config, noisy=True)
        gate_label = "initial" if gate is None else gate.label()
        logical_topology = simulation._advance_logical_topology(logical_qubit, gate, config)

        pre_density = von_neumann_metrics(rho_noisy, config.n_qubits)
        pre_artifact, _ = simulation._step_artifact(
            step=prefix,
            gate=gate_label,
            rho_noisy=rho_noisy,
            rho_ideal=rho_ideal,
            positions=positions,
            config=config,
            previous_edges=previous_edges,
            logical_topology=logical_topology,
        )
        graph_psig, logical_psig, logical_coherence, pre_correlation = _step_topology(pre_artifact)
        pre_tryperposition = tryperposition_signal(pre_density, graph_psig, logical_psig, pre_correlation)
        if reference_graph_psig is None:
            reference_graph_psig = graph_psig
            reference_logical_psig = logical_psig
            reference_tryperposition_psig = pre_tryperposition["P_sig_tryperposition"]
        gradient = frobenius_gradient(pre_correlation, previous_correlation, profile.timestep)
        impacts = impact_by_qubit(pre_correlation, previous_correlation, profile.timestep)
        lct, eth = lct_eth_terms(
            step=prefix,
            density=pre_density,
            graph_psig=graph_psig,
            logical_psig=logical_psig,
            logical_coherence=logical_coherence,
            tryperposition_psig=pre_tryperposition["P_sig_tryperposition"],
            reference_graph_psig=reference_graph_psig,
            reference_logical_psig=reference_logical_psig,
            reference_tryperposition_psig=reference_tryperposition_psig,
            previous_entropy_bits=previous_entropy_bits,
            gradient_frobenius=gradient,
            correlation_matrix=pre_correlation,
            profile=profile,
        )
        eligible_qubits = [] if impacts is None else [index for index, impact in enumerate(impacts) if impact > profile.impact_threshold]
        active_tension = eth["active_tension"]
        collapse_condition_met = bool(active_tension is not None and active_tension > profile.collapse_threshold)
        dephasing_strength = None
        applied_qubits: list[int] = []
        if profile.apply_local_dephasing and collapse_condition_met and eligible_qubits and active_tension is not None:
            dephasing_strength = float(min(1.0, (active_tension - 1.0) / active_tension))
            rho_noisy = local_z_dephasing(rho_noisy, eligible_qubits, dephasing_strength, config.n_qubits)
            applied_qubits = eligible_qubits

        output_density = von_neumann_metrics(rho_noisy, config.n_qubits)
        output_artifact, previous_edges = simulation._step_artifact(
            step=prefix,
            gate=gate_label,
            rho_noisy=rho_noisy,
            rho_ideal=rho_ideal,
            positions=positions,
            config=config,
            previous_edges=previous_edges,
            logical_topology=logical_topology,
        )
        output = output_artifact.to_dict()
        output_graph_psig, output_logical_psig, output_logical_coherence, output_correlation = _step_topology(output_artifact)
        output_tryperposition = tryperposition_signal(output_density, output_graph_psig, output_logical_psig, output_correlation)
        eth["collapse_condition_met"] = collapse_condition_met
        eth["collapse_threshold"] = profile.collapse_threshold
        eth["collapse_observed"] = collapse_condition_met
        impact_route = simulation.inspection_route(positions, eligible_qubits)
        records.append({
            "step": prefix,
            "time_step": float(prefix * profile.timestep),
            "gate": gate_label,
            "density": output_density,
            "pre_intervention_density": pre_density,
            "topology": {
                "graph_P_sig": output_graph_psig,
                "graph_betti": output["topology"]["betti"],
                "graph_finite_h1": output["topology"]["n_finite_h1"],
                "logical_P_sig": output_logical_psig,
                "logical_coherence": output_logical_coherence,
                "logical_scope": output["logical_topology"].get("scope"),
                "P_sig_tryperposition": output_tryperposition["P_sig_tryperposition"],
            },
            "pre_intervention_topology": {
                "graph_P_sig": graph_psig,
                "graph_betti": pre_artifact.to_dict()["topology"]["betti"],
                "graph_finite_h1": pre_artifact.to_dict()["topology"]["n_finite_h1"],
                "logical_P_sig": logical_psig,
                "logical_coherence": logical_coherence,
                "P_sig_tryperposition": pre_tryperposition["P_sig_tryperposition"],
            },
            "tryperposition": output_tryperposition,
            "lct": lct,
            "eth": eth,
            "impact": {
                "per_qubit": impacts,
                "impact_threshold": profile.impact_threshold,
                "eligible_qubits": eligible_qubits,
            },
            "intervention": {
                "mode": "baseline_observational" if not profile.apply_local_dephasing else "lct_eth_local_dephasing_experimental",
                "applied": bool(applied_qubits),
                "channel": None if not applied_qubits else "local_z_dephasing",
                "strength": dephasing_strength,
                "affected_qubits": applied_qubits,
                "baseline_density_overwritten": False,
            },
            "tsp_inspection": impact_route,
            "correlation_matrix": output["cube_slice"],
        })
        previous_entropy_bits = output_density["entropy_bits"]
        previous_correlation = output_correlation

    return {
        "name": profile.name,
        "profile": asdict(profile),
        "reference": {
            "graph_P_sig_reference": reference_graph_psig,
            "logical_P_sig_reference": reference_logical_psig,
            "P_sig_tryperposition_reference": reference_tryperposition_psig,
            "graph_stable_abscissa_A": None if reference_graph_psig is None else float(profile.alpha_0 * reference_graph_psig),
            "logical_stable_abscissa_A": None if reference_logical_psig is None else float(profile.alpha_0 * reference_logical_psig),
            "tryperposition_stable_abscissa_A": None if reference_tryperposition_psig is None else float(profile.alpha_0 * reference_tryperposition_psig),
        },
        "steps": records,
    }


def default_profiles() -> list[IncubatorProfile]:
    """Return predeclared baseline and sensitivity profiles before any run."""
    common = dict(
        eta_lct=0.1,
        omega_lct=math.pi / 2,
        timestep=1.0,
        collapse_threshold=1.0,
        impact_threshold=0.0,
        temperature_millikelvin=15.0,
        temperature_reference_millikelvin=1_000.0,
        pressure_beta=1.0,
        pressure_gamma=2.0,
        crosstalk_kappa=0.15,
    )
    return [
        IncubatorProfile(name="baseline_observational", alpha_0=1.0, apply_local_dephasing=False, **common),
        IncubatorProfile(name="lct_eth_sensitivity_local_dephasing", alpha_0=0.05, apply_local_dephasing=True, **common),
    ]


def run_incubator(engine_src: str | None = None) -> dict[str, Any]:
    """Run both predeclared scenarios for the five-qubit density-matrix program."""
    simulation = _load_simulation_module(engine_src)
    config = simulation.SimulationConfig(
        n_qubits=5,
        scenario="cosmos_lct_eth_topological_incubator",
        t1_seconds=100e-6,
        t2_seconds=50e-6,
        single_gate_seconds=4e-6,
        two_gate_seconds=12e-6,
        one_qubit_depolarizing=0.001,
        two_qubit_depolarizing=0.01,
    )
    gates = simulation.default_program()
    scenarios = [run_profile(gates, config, simulation, profile) for profile in default_profiles()]
    return {
        "schema": "ratiss.cosmos.incubator.v1",
        "provenance": {
            "execution": "local_qiskit_aer_density_matrix_simulation",
            "validated_on_hardware": False,
            "claim_boundary": "Simulation metrics and an algorithmic sidecar only; no QPU execution, cryogenic calibration, material topological-qubit or error-correction claim.",
            "source_reuse": {
                "ratiss_experimental_ia": "501fd7d0a59123a2b8de95aa3b9c5a98aff7a25a",
                "ratiss_odv_aeon": "3dfe46be82bd340c13ad724e2c0c2b6accf4003a",
                "portfolio_eth": "fb1891f460167d975790fdb4873369e63459c8d4",
            },
        },
        "noise_profile": {
            "t1_seconds": config.t1_seconds,
            "t2_seconds": config.t2_seconds,
            "single_gate_seconds": config.single_gate_seconds,
            "two_gate_seconds": config.two_gate_seconds,
            "one_qubit_depolarizing": config.one_qubit_depolarizing,
            "two_qubit_depolarizing": config.two_qubit_depolarizing,
            "temperature_millikelvin": default_profiles()[0].temperature_millikelvin,
            "temperature_role": "metadata_only_not_used_to_derive_aer_parameters",
        },
        "gates": [gate.label() for gate in gates],
        "scenarios": scenarios,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local COSMOS LCT-ETH topological incubator.")
    parser.add_argument("--engine-src", help="Path to ratiss-topological-decoherence-engine/src.")
    parser.add_argument("--output", default="artifacts/incubator_lct_eth_run.json")
    args = parser.parse_args()
    result = run_incubator(args.engine_src)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {destination} with {len(result['scenarios'])} scenarios.")


if __name__ == "__main__":
    main()
