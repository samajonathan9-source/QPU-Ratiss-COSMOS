# Architecture COSMOS

```mermaid
flowchart LR
  A[GHZ circuit specification] --> B[Aer local simulator]
  B --> C[Raw counts by regime]
  C --> D[RATISS counts association adapter]
  E[Five qubit gate program] --> F[Density matrix simulation]
  F --> G[Correlation cube and graph topology]
  F --> H[Algorithmic TopologicalQubit sidecar]
  D --> I[Versioned JSON artifact]
  G --> I
  H --> I
```

COSMOS deliberately preserves two analysis paths. Counts become a declared association structure; they do not silently become a density matrix. The five-qubit trajectory, in contrast, carries density-derived correlations and a separate algorithmic logical sidecar. The JSON keeps both paths rather than forcing them into one metric.
