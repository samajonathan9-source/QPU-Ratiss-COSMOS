import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cosmos_artifact_keeps_counts_and_density_contracts_separate():
    document = json.loads((ROOT / "artifacts" / "cosmos_run.json").read_text(encoding="utf-8"))
    assert document["provenance"]["validated_on_hardware"] is False
    assert len(document["counts_scaling"]) == 4
    assert all("ideal_counts" in item and "noisy_counts" in item for item in document["counts_scaling"])
    assert document["density_topology"]["steps"][-1]["logical_topology"]["P_sig"] >= 0.0


def test_cosmos_documentation_figures_exist():
    assets = ROOT / "docs" / "assets"
    assert (assets / "cosmos-counts-scaling.png").is_file()
    assert (assets / "cosmos-density-sidecar.png").is_file()
    assert (assets / "incubator-entropy-eth.png").is_file()
    assert (assets / "incubator-topology-lct.png").is_file()


def test_incubator_artifact_preserves_zero_graph_psig_and_unavailable_tension():
    document = json.loads((ROOT / "artifacts" / "incubator_lct_eth_run.json").read_text(encoding="utf-8"))
    assert document["schema"] == "ratiss.cosmos.incubator.v1"
    assert document["provenance"]["validated_on_hardware"] is False
    assert document["noise_profile"]["temperature_role"] == "metadata_only_not_used_to_derive_aer_parameters"
    baseline = next(item for item in document["scenarios"] if item["name"] == "baseline_observational")
    assert len(baseline["steps"]) == len(document["gates"]) + 1
    assert all(step["intervention"]["applied"] is False for step in baseline["steps"])
    for step in baseline["steps"]:
        if step["topology"]["graph_P_sig"] == 0.0:
            assert step["eth"]["graph_tension"] is None
    assert baseline["steps"][0]["eth"]["delta_entropy_bits"] is None
    assert baseline["steps"][0]["impact"]["per_qubit"] is None


def test_incubator_sensitivity_is_declared_as_a_separate_intervention_scenario():
    document = json.loads((ROOT / "artifacts" / "incubator_lct_eth_run.json").read_text(encoding="utf-8"))
    sensitivity = next(item for item in document["scenarios"] if item["name"] == "lct_eth_sensitivity_local_dephasing")
    assert sensitivity["profile"]["apply_local_dephasing"] is True
    assert all(step["lct"]["measurement_state"] == "pre_intervention_density" for step in sensitivity["steps"])
    assert all(step["eth"]["measurement_state"] == "pre_intervention_density" for step in sensitivity["steps"])
    assert all(step["intervention"]["baseline_density_overwritten"] is False for step in sensitivity["steps"])
