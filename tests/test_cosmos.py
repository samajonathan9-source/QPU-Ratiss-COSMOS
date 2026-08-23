from pathlib import Path
import importlib.util


MODULE = Path(__file__).resolve().parents[1] / "scripts" / "run_cosmos.py"
SPEC = importlib.util.spec_from_file_location("run_cosmos", MODULE)
cosmos = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(cosmos)


def test_prefix_circuit_contains_requested_chain_depth():
    circuit = cosmos.build_prefix_circuit(5, 4)
    assert circuit.num_qubits == 5
    assert circuit.count_ops()["cx"] == 4


def test_dominant_mass_preserves_observed_counts():
    assert cosmos._dominant_mass({"00": 3, "11": 1}) == 0.75
    assert cosmos._dominant_mass({}) == 0.0
