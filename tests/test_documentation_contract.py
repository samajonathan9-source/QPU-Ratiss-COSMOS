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
