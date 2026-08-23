# QPU-Ratiss-COSMOS

**COSMOS** is a reproducible local experiment harness for RATISS. It couples a Qiskit Aer counts sweep to the existing RATISS association adapter, then runs a separate five-qubit density-matrix trajectory with the source-derived algorithmic `TopologicalQubit` sidecar.

> It is a **virtual-QPU simulation**, not a QPU job, a calibrated-device model, a physical topological qubit or an error-correction demonstration.

## Run

```bash
PYTHONPATH=/path/to/ratiss-topological-decoherence-engine/src \
python3 scripts/run_cosmos.py \
  --engine-src /path/to/ratiss-topological-decoherence-engine/src \
  --output artifacts/cosmos_run.json
```

The JSON keeps raw counts, declared noise, derived association timelines and density-matrix/topological sidecar outputs. It does not replace low or zero values with expected values.

See [`docs/PROTOCOL.md`](docs/PROTOCOL.md) for the two simulation regimes and their claim boundaries.

The first calculated output is summarized in [`docs/RESULTS.md`](docs/RESULTS.md).
