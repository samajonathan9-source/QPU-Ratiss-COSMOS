import importlib.util
from pathlib import Path
import sys

import numpy as np


MODULE = Path(__file__).resolve().parents[1] / "scripts" / "run_incubator.py"
SPEC = importlib.util.spec_from_file_location("run_incubator", MODULE)
incubator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = incubator
SPEC.loader.exec_module(incubator)


def test_von_neumann_metrics_of_pure_state_are_observed_without_floor():
    rho = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    metrics = incubator.von_neumann_metrics(rho, n_qubits=1)
    assert metrics["entropy_bits"] == 0.0
    assert metrics["purity_global"] == 1.0
    assert metrics["density_coherence_proxy"] == 1.0


def test_graph_tension_is_none_when_reference_psig_is_real_zero():
    tension, reason = incubator._tension(stress=0.4, alpha_0=1.0, reference_psig=0.0, current_psig=0.7)
    assert tension is None
    assert reason == "reference_psig_is_zero"


def test_initial_gradient_and_impact_remain_not_applicable():
    current = np.eye(3)
    assert incubator.frobenius_gradient(current, None, 1.0) is None
    assert incubator.impact_by_qubit(current, None, 1.0) is None


def test_local_z_dephasing_changes_off_diagonal_amplitude_without_breaking_trace():
    plus = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex)
    output = incubator.local_z_dephasing(plus, [0], strength=0.25, n_qubits=1)
    assert np.isclose(np.trace(output), 1.0)
    assert np.isclose(output[0, 1], 0.25)


def test_default_profiles_keep_baseline_separate_from_intervention():
    baseline, sensitivity = incubator.default_profiles()
    assert baseline.name == "baseline_observational"
    assert baseline.apply_local_dephasing is False
    assert sensitivity.apply_local_dephasing is True
    assert baseline.collapse_threshold == sensitivity.collapse_threshold == 1.0


def test_lct_terms_mark_their_pre_intervention_measurement_state():
    profile = incubator.default_profiles()[0]
    density = {"entropy_bits": 0.5, "purity_global": 0.75, "density_coherence_proxy": 0.9}
    lct, eth = incubator.lct_eth_terms(
        step=1,
        density=density,
        graph_psig=0.0,
        logical_psig=0.8,
        logical_coherence=0.9,
        reference_graph_psig=0.0,
        reference_logical_psig=1.0,
        previous_entropy_bits=0.1,
        gradient_frobenius=0.4,
        correlation_matrix=np.eye(2),
        profile=profile,
    )
    assert lct["measurement_state"] == "pre_intervention_density"
    assert eth["measurement_state"] == "pre_intervention_density"
    assert eth["graph_tension"] is None
    assert eth["logical_tension"] is not None
