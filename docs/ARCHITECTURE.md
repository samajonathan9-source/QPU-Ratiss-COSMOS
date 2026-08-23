# Architecture COSMOS

```mermaid
flowchart LR
  A[GHZ circuit specification] --> B[Aer local simulator]
  B --> C[Raw counts by regime]
  C --> D[RATISS counts association adapter]
  E[Five qubit gate program] --> F[Density matrix simulation]
  F --> G[Correlation cube and graph topology]
  F --> H[Algorithmic TopologicalQubit sidecar]
  F --> J[Density entropy and purity]
  G --> K[LCT and ETH metric adapter]
  H --> K
  J --> K
  K --> L[Baseline observational scenario]
  K --> M[Declared local dephasing scenario]
  L --> N[Impact-derived TSP inspection]
  M --> N
  D --> I[Versioned JSON artifact]
  G --> I
  H --> I
  L --> O[Incubator JSON artifact]
  M --> O
  N --> O
  O --> P[Deterministic figures]
```

COSMOS deliberately preserves three analysis contracts. Counts become a declared association structure; they do not silently become a density matrix. The five-qubit trajectory carries density-derived correlations and a separate algorithmic logical sidecar. The incubator instruments this trajectory with entropy, LCT and ETH candidate metrics while retaining the two topological planes independently.

The baseline scenario only observes the candidate collapse condition. The sensitivity scenario is a separate run: it records the pre-intervention metrics, then applies a declared local dephasing channel only where its own condition is met. The inspection route is derived from impact-selected nodes after measurement and never feeds back as a TSP correction command. The full variable contract is in [`INCUBATOR_CONTRACT.md`](INCUBATOR_CONTRACT.md).
