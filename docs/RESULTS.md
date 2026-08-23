# Résultats observés — COSMOS v1

Le fichier [`artifacts/cosmos_run.json`](../artifacts/cosmos_run.json) a été produit localement avec Qiskit Aer, seed `42`, un canal dépolarisant CX de `0.02` et `256` tirs par régime de counts. Il ne contient aucun identifiant de job QPU ; `validated_on_hardware=false` est enregistré dans la provenance.

## Counts GHZ et associations RATISS

| Qubits | Profondeur CX | Masse dominante idéale | Masse dominante bruitée | P sig du graphe d’associations |
|---:|---:|---:|---:|---:|
| 8 | 7 | 0.523438 | 0.457031 | 0.0 |
| 12 | 11 | 0.550781 | 0.425781 | 0.0 |
| 16 | 15 | 0.507812 | 0.425781 | 0.0 |
| 20 | 19 | 0.515625 | 0.406250 | 0.0 |

La masse dominante diminue ici sous le modèle de bruit déclaré. Les quatre valeurs `P sig = 0.0` du graphe sont conservées telles que calculées. Les timelines issues des counts exposent `logical_topology.P_sig=null`, car des associations de counts ne constituent pas une matrice densité ni le noyau logique RATISS.

## Trajectoire densité à cinq qubits

La trajectoire séparée à cinq qubits se termine après `cz(2,3)` avec un `P sig` de graphe `0.0`, un `P sig` logique RATISS de `0.7344459623`, une cohérence logicielle de `0.792` et une phase de `1.3744467859`. Ces deux signatures concernent des objets différents : le graphe de corrélations de la matrice densité et le sidecar `TopologicalQubit` algorithmique.

> Ces résultats caractérisent une exécution Aer locale dans ce protocole. Ils ne certifient ni un appareil physique, ni une correction d’erreur, ni une performance sur un QPU réel.

## Reproduction

```bash
PYTHONPATH=/path/to/ratiss-topological-decoherence-engine/src \
python3 scripts/run_cosmos.py \
  --engine-src /path/to/ratiss-topological-decoherence-engine/src \
  --output artifacts/cosmos_run.json --shots 256
```

## Référence

[1] [Qiskit Aer — Exact and noisy simulation](https://quantum.cloud.ibm.com/docs/guides/simulate-with-qiskit-aer)
