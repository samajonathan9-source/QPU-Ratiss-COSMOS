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
  G --> K[Tryperposition information layer]
  H --> K
  J --> L[Tryperposition quantum layer]
  F --> M[Trace integrity layer]
  K --> N[Tryperposition P sig]
  L --> N
  M --> N
  G --> O[LCT and ETH metric adapter]
  H --> O
  J --> O
  N --> O
  O --> P[Baseline observational scenario]
  O --> Q[Declared local dephasing scenario]
  P --> R[Impact-derived TSP inspection]
  Q --> R
  D --> I[Versioned JSON artifact]
  G --> I
  H --> I
  P --> S[Incubator JSON artifact]
  Q --> S
  R --> S
  S --> T[Deterministic figures]
```

COSMOS deliberately preserves three analysis contracts. Counts become a declared association structure; they do not silently become a density matrix. The five-qubit trajectory carries density-derived correlations and a separate algorithmic logical sidecar. The incubator instruments this trajectory with entropy, LCT and ETH candidate metrics while retaining `graph_P_sig`, `logical_P_sig` and `P_sig_tryperposition` independently.

The `P_sig_tryperposition` path composes the density, information and trace-integrity layers and supplies the declared active tension without overwriting the `P_sig` graph value. The baseline scenario only observes the candidate collapse condition. The sensitivity scenario is a separate run: it records the pre-intervention metrics, then applies a declared local dephasing channel only where its own condition is met. The inspection route is derived from impact-selected nodes after measurement and never feeds back as a TSP correction command. The full variable contract is in [`INCUBATOR_CONTRACT.md`](INCUBATOR_CONTRACT.md).
