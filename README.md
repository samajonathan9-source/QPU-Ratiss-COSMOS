<p align="center">
  <img src="docs/brand/cosmos-logo.png" alt="COSMOS — correlation ring, density core and Q×I×M tryperposition channel" width="240"/>
</p>

<h1 align="center">QPU-Ratiss-COSMOS</h1>

<p align="center">
  <strong>Local QPU simulation laboratory</strong><br/>
  Noisy circuits · density-matrix trajectories · RATISS algorithmic topology —<br/>
  reproducible, verifiable CPU artifacts.
</p>

<p align="center">
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/License-MIT-42d6ad?style=for-the-badge"></a>
  <img alt="Python ≥ 3.11" src="https://img.shields.io/badge/Python-%E2%89%A5%203.11-79b8ff?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Qiskit 2.5.2" src="https://img.shields.io/badge/Qiskit-2.5.2-6929c4?style=for-the-badge&logo=ibm&logoColor=white">
  <img alt="Qiskit Aer 0.17.2" src="https://img.shields.io/badge/Qiskit%20Aer-0.17.2-6929c4?style=for-the-badge&logo=ibm&logoColor=white">
  <img alt="NumPy ≥ 1.26" src="https://img.shields.io/badge/NumPy-%E2%89%A5%201.26-79b8ff?style=for-the-badge&logo=numpy&logoColor=white">
  <img alt="Deterministic reproducibility" src="https://img.shields.io/badge/Reproducibility-deterministic-ff927d?style=for-the-badge">
</p>

<p align="center">
  <em>Architect & principal investigator: <strong>Jonathan Evina</strong> ·
  <a href="https://orcid.org/0009-0000-4092-5313">ORCID 0009-0000-4092-5313</a></em>
</p>

---

## Table of contents

1. [Nature of the instrument](#1-nature-of-the-instrument)
2. [Claim boundary](#2-claim-boundary)
3. [Three experimental regimes](#3-three-experimental-regimes)
4. [Computed and reproduced results](#4-computed-and-reproduced-results)
5. [The LCT-ETH incubator](#5-the-lct-eth-incubator)
6. [Technology stack](#6-technology-stack)
7. [Quick start and reproduction](#7-quick-start-and-reproduction)
8. [Tests and verification](#8-tests-and-verification)
9. [LCT-ETH coupling and real-QPU validation](#9-lct-eth-coupling-and-real-qpu-validation)
10. [Laboratory documents](#10-laboratory-documents)
11. [Citation and license](#11-citation-and-license)

---

## 1. Nature of the instrument

COSMOS is a **software measurement instrument**, not a hardware simulator. It examines a single question:

> **How can a noisy circuit trajectory, its associations and the RATISS software topological states be made visible, without ever confusing these objects with a physical QPU?**

It retains every quantity genuinely computed by the simulator — including when a topological signal is zero, when a tension is indeterminate, or when a sidecar does not apply. A field that cannot be computed within the contract stays `null`, with an explicit reason, rather than a convenience value.

| Project type | Execution | Main inputs | Main output |
|---|---|---|---|
| Reproducible quantum simulation | Qiskit Aer local (`density_matrix`, `stabilizer`) | GHZ circuit, five-qubit program, declared LCT-ETH profiles | Raw counts, correlations, topology, logical sidecar, instrumented thermodynamic trajectories |

## 2. Claim boundary

> **This repository is a virtual QPU simulation.** It runs no hardware job, reproduces no hardware calibration, claims neither the fabrication of a topological qubit nor error correction, and demonstrates no supremacy over a TSP instance.

The provenance of every artifact carries `validated_on_hardware = false`. This boundary is a methodological requirement of the laboratory, not a rhetorical hedge.

## 3. Three experimental regimes

Three distinct data contracts, deliberately not merged:

| Regime | Inputs | Computed quantities | Deliberately absent |
|---|---|---|---|
| `counts_scaling` | GHZ Aer counts, 8 → 20 qubits | Dominant mass, RATISS association, graph topology | Density matrix, logical `P_sig` |
| `density_topology` | Five-qubit program under declared noise | Density, correlations, graph topology, `TopologicalQubit` sidecar | QPU proof, error correction, device model |
| `incubator_lct_eth` | Same density program, two profiles | Entropy, ETH rate, LCT factors, impacts, TSP route, separate scenarios | Real cryogenic calibration, statistical ETH, hardware control |

A counts vector is a sampled observation: it does not authorise implicitly reconstructing a full density matrix. The incubator keeps graph `P_sig` and logical `P_sig` in two distinct fields and never substitutes one for the other.

## 4. Computed and reproduced results

### 4.1 GHZ counts scaling

![Dominant GHZ mass, ideal and noisy Aer](docs/assets/cosmos-counts-scaling.png)

The mass of the most frequent result is computed from raw Aer counts (seed `42`, depolarising CX channel `p=0.02`, 256 shots). Across the four tested sizes, the noisy curve stays below the ideal curve. Data: [`artifacts/cosmos_run.json`](artifacts/cosmos_run.json).

| Qubits | CX depth | Ideal mass | Noisy mass | Graph `P_sig` (counts) |
|---:|---:|---:|---:|---:|
| 8 | 7 | 0.523438 | 0.457031 | 0.0 |
| 12 | 11 | 0.550781 | 0.425781 | 0.0 |
| 16 | 15 | 0.507812 | 0.425781 | 0.0 |
| 20 | 19 | 0.515625 | 0.406250 | 0.0 |

### 4.2 Logical sidecar of the density trajectory

![RATISS logical sidecar](docs/assets/cosmos-density-sidecar.png)

Five-qubit density regime (do not read as a metric from the GHZ counts): software coherence and algorithmic `P_sig` of the sidecar across the actually executed gates.

### 4.3 Recorded observations

| Observation | Value | Authorised reading |
|---|---:|---|
| Counts 20 qubits, ideal mass | 0.515625 | Sampling for this seed and shot count |
| Counts 20 qubits, noisy mass | 0.406250 | Effect of the declared channel, not on real hardware |
| Graph topology in counts | `P_sig = 0.0` | Retained, not corrected or replaced |
| Final density step, logical `P_sig` | `0.4948611575` | Sidecar output, separate from the graph |
| Incubator baseline, final entropy | `3.9055306800` bits | Simulation under the declared noise profile |
| Incubator tryperposition, max tension (baseline) | `17.3833666846` | Q×I×M channel, during the deterministic `P_sig` oscillation |
| Incubator tryperposition, max tension (sensitivity) | `356.9757698741` | `alpha_0=0.05` scenario, not a calibrated hardware tension |
| Incubator, graph `P_sig` | Deterministic oscillation `0 → 0.133231 → 0` | Uncontrolled tryperposition, LCT equivalent |

## 5. The LCT-ETH incubator

![Entropy and LCT-ETH tension](docs/assets/incubator-entropy-eth.png)

The incubator links a five-qubit Aer trajectory to the computed von Neumann entropy, the per-step entropic variation, the LCT factors and the RATISS logical sidecar. Its active channel is the **tryperposition** `Psi = Q x I x M`: an amplitude from the simulated density (Q), the two already-computed topological signals (I) and a trace-integrity witness (M). It overwrites neither the graph `P_sig` nor the logical `P_sig`. It provides two versioned scenarios — a **strictly observational baseline** and a **sensitivity with explicit local dephasing** — the second never overwriting the first.

![Separation of the three P_sig](docs/assets/incubator-topology-lct.png)

**The `P_sig` oscillation is the phenomenon under study, not an artefact.** Across the eleven gate boundaries, the graph persistence follows `0 → 0.033454 → 0.133231 → 0.025041 → 0.065933 → 0.111181 → 0.041562 → 0 → 0.015558 → 0.0048 → 0`. This is the **uncontrolled tryperposition** regime — the equivalent, for a universal information system, of what LCT describes for entangled systems: persistence is born, grows and dies along the trajectory without being driven. It is produced by a **deterministic** decoherence noise (seed fixed per step): the same run always yields the same oscillation, making it replayable and auditable. Its own tension stays `null` (zero initial reference) — this absence is honestly retained, with no division by epsilon. In baseline, the tryperposition channel goes from `0.1879842865` to `0.1299670353` (max tension `17.3833666846`); the logical sidecar, separately, from `0.1821619076` to `0.5893783934`.

**ETH is the instrument's virtual cryogenic environment.** The term denotes the internal metric of entropic variation ("thermodynamic collapse"), not the *Eigenstate Thermalization Hypothesis*. At each gate boundary, ETH measures how much entropy the surrounding "bath" exchanges with the simulated logical qubit — just as a cryostat encloses a real device. The `15 mK` temperature is the metadata of this envelope; the Aer parameters actually used are `T1`, `T2`, gate durations and depolarising probabilities. This is an **instrumented software equivalence**, not a hardware cryogenic calibration. [1]

## 6. Technology stack

| Layer | Technology | Role |
|---|---|---|
| Language | Python ≥ 3.11 | Full instrument |
| Quantum simulation | Qiskit 2.5.2 · Qiskit Aer 0.17.2 | Density matrices (`density_matrix`), counts (`stabilizer`), noise channels |
| Numerical computing | NumPy ≥ 1.26 | Dense linear algebra, spectral decomposition |
| Topology | Vietoris-Rips (GF(2), in-house) | H0/H1 persistence, `P_sig` |
| Inspection routing | Held-Karp exact ≤ 10 nodes, 2-opt beyond | TSP inspection routes, never a TSP advantage |
| Visualisation | Matplotlib | Figures derived exclusively from JSON artifacts |
| Tests | pytest | Data contracts and reproducibility |
| Artifacts | Versioned JSON | `ratiss.cosmos.run.v1`, `ratiss.cosmos.incubator.v1` |

The source topological engine ([`ratiss-topological-decoherence-engine`](https://github.com/evinajonathan13-max/ratiss-topological-decoherence-engine)) is an **explicit local-path** dependency — provenance stays visible, no divergent implementation is hidden inside COSMOS.

## 7. Quick start and reproduction

```bash
git clone https://github.com/evinajonathan13-max/QPU-Ratiss-COSMOS.git
git clone https://github.com/evinajonathan13-max/ratiss-topological-decoherence-engine.git
cd QPU-Ratiss-COSMOS
python3 -m pip install -e .

# Counts + density regimes
PYTHONPATH=../ratiss-topological-decoherence-engine/src \
python3 scripts/run_cosmos.py \
  --engine-src ../ratiss-topological-decoherence-engine/src \
  --output artifacts/cosmos_run.json --shots 256

# LCT-ETH incubator (baseline + sensitivity)
PYTHONPATH=../ratiss-topological-decoherence-engine/src \
python3 scripts/run_incubator.py \
  --engine-src ../ratiss-topological-decoherence-engine/src \
  --output artifacts/incubator_lct_eth_run.json

# Figures derived from artifacts only
python3 scripts/generate_docs_figures.py
python3 scripts/generate_incubator_figures.py
```

Two successive runs of the same artifact produce **bit-for-bit identical** content: reproducibility is a verifiable property of the instrument, not a promise.

## 8. Tests and verification

```bash
PYTHONPATH=../ratiss-topological-decoherence-engine/src python3 -m pytest -q
```

Tests check the requested GHZ chain, raw-counts reading, the counts/density contract separation, the preservation of a zero graph `P_sig`, the honest unavailability of a tension at zero reference, the baseline/sensitivity separation, the stabilised LCT-ETH coupling and the existence of documentation figures.

## 9. LCT-ETH coupling and real-QPU validation

### 9.1 Stabilised LCT-ETH coupling

The incubator now couples the two pillars — superposition (LCT) and thermodynamic collapse (ETH, the virtual cryogenics) — via a **stabilised** modulation of the learning amplitude:

```text
eth_modulation = exp(-|eth_rate|)          # strictly positive, bounded in (0, 1]
delta_w_coupled = η · φ · P_sig · C · eth_modulation
```

When the virtual cryogenic bath is calm (`|ΔS/Δt| ≈ 0`), the modulation is `1` (full learning authorised). When it is agitated (large `|ΔS/Δt|`), it tends toward `0` (learning is suspended). This factor can **neither invert the gradient sign nor amplify it**: it only damps, which guarantees learning-amplitude stability — whereas the naïve coupling `ΔW · ETH(t)` would diverge when `ETH(t) < 0`. Measured in baseline: at step 2, `eth_rate = 0.94` → modulation `0.39` → delta damped from `-0.041` to `-0.016`.

### 9.2 Validation against a real IBM QPU

A two-qubit Bell circuit (`h(0) ; cx(0,1) ; measure`) was submitted **once** to the real backend `ibm_marrakesh` (156 qubits, IBM Quantum Platform). The artifact [`artifacts/qpu_validation.json`](artifacts/qpu_validation.json) retains the **traceable Job ID** `da5u376vhnc73fmhnug`, the hardware counts, and compares the LCT divergence between the local Aer simulation and the real QPU outcome.

| Source | Counts | Marked mass `|11⟩` | LCT divergence |
|---|---|---:|---:|
| Ideal (pure Bell) | `{00:256, 11:256}` | 0.500 | — |
| Noisy Aer (CX p=0.02) | `{00:265, 11:243, 01:2, 10:2}` | 0.4746 | 0.000309 |
| **Real QPU ibm_marrakesh** | `{00:255, 11:243, 01:9, 10:5}` | 0.4746 | 0.000309 |

> **Honest reading.** The marked masses coincide (`0.4746`), so the computed LCT divergence is identical (ratio 1.0). The sidecar does not capture the difference between the `01`/`10` errors of Aer (2/2) and the real QPU (9/5): it reacts to the global mass, not to the error structure. This is a **documented limitation** of the current coupling, not a claim of perfect correspondence. The QPU validates that the real hardware stays within the band predicted by the simulation for a Bell state; it does not certify that the sidecar predicts detailed hardware noise.

### 9.3 Classical counts diagnostic

To capture what the dominant mass cannot see, a **classical diagnostic** complements the validation. It measures, from counts only:

- **Shannon entropy** (classical disorder of the distribution, in bits) — `1.0646` (Aer) vs `1.1789` (QPU).
- **Total variation distance** (TVD, fraction of probability that leaked from the ideal, bounded `[0,1]`) — `0.0254` (Aer) vs `0.0273` (QPU).
- **Diagnostic score** (`0.5·mass_gap + 0.5·TVD`) — `0.0254` (Aer) vs `0.0264` (QPU).

> **Critical boundary.** This diagnostic is explicitly labelled `classical_counts_diagnostic_not_quantum_entropy`. The Shannon entropy of counts **is not** the von Neumann entropy of the density matrix: counts are projected measurement outcomes that have already destroyed coherence information. One therefore **cannot** approximate `ETH = dS_vN/dt` from counts without quantum state tomography — and tomography is exactly the exponential explosion the instrument refuses. The diagnostic measures **classical probability leakage**, not quantum coherence loss. This is the honest boundary between "what counts tell us" and "what they cannot tell us".

The IBM token is read **only** from the `IBM_QUANTUM_TOKEN` environment variable; it is never written into the artifact, the repository or any log.

## 10. Laboratory documents

| Document | Role |
|---|---|
| [`PROTOCOL.md`](docs/PROTOCOL.md) | Hypotheses, three regimes, claim boundaries |
| [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Data flow and separation of analysed objects |
| [`RESULTS.md`](docs/RESULTS.md) | Actually observed values and reproduction recipe |
| [`INCUBATOR_CONTRACT.md`](docs/INCUBATOR_CONTRACT.md) | Variables, time conventions, non-substitution rules |
| [`INCUBATOR_SOURCE_MAP.md`](docs/INCUBATOR_SOURCE_MAP.md) | RATISS-Net / ODV-AEON reuse and excluded elements |
| [`JOINT_TEST_SESSION.md`](docs/JOINT_TEST_SESSION.md) | Replay the baseline and prepare a hypothesis |
| [`VISUAL_AUDIT.md`](docs/VISUAL_AUDIT.md) | Verification of versioned figures |

## 11. Citation and license

Distributed under the [MIT License](LICENSE) — © 2026 Jonathan Evina.

```bibtex
@software{evina_cosmos_2026,
  author  = {Evina, Jonathan},
  title   = {QPU-Ratiss-COSMOS: Local QPU Simulation Laboratory
             with RATISS Topological Instrumentation},
  year    = {2026},
  url     = {https://github.com/evinajonathan13-max/QPU-Ratiss-COSMOS},
  note    = {Reproducible software simulation; no hardware execution.}
}
```

## References

[1] [Qiskit Aer — Building Noise Models](https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html)
