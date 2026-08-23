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

## Incubateur LCT-ETH à cinq qubits

Le fichier [`artifacts/incubator_lct_eth_run.json`](../artifacts/incubator_lct_eth_run.json) a été généré après les deux régimes historiques. Il réutilise le même programme densité de cinq qubits, `T1=100 µs`, `T2=50 µs`, durées `4 µs` et `12 µs`, dépolarisation une porte `0.001` et deux portes `0.01`. La température déclarée de `15 mK` n’est pas convertie vers ces paramètres : elle reste la métadonnée d’un profil de comparaison. [1]

| Observation calculée | Baseline observationnelle | Sensibilité au déphasage local déclaré | Lecture autorisée |
|---|---:|---:|---|
| Nombre de frontières de porte | 11 | 11 | Trajectoires complètes du programme d’origine |
| Entropie initiale | `-0.0` bits | `-0.0` bits | Valeur numérique brute de l’état pur initial |
| Entropie finale | `3.9055306800` bits | `3.9824933490` bits | Résultat de simulation, pas température matérielle |
| Plage du taux ETH interne | `0.0207208246` à `0.9384926798` bits/pas | `0.0121234561` à `0.9384926798` bits/pas | Variation de von Neumann par pas dans ce contrat |
| `P_sig` de graphe | `0.0` aux 11 pas | `0.0` aux 11 pas | Valeur conservée ; aucune tension graphe finie n’est fabriquée |
| `P_sig` logique du sidecar | `1.2144127174 → 0.7660314642` | même sidecar algorithmique | Objet séparé du graphe de corrélation |
| `P_sig` tryperposition | `1.2144127174 → 0.1677871984` | `1.2144127174 → 0.1559818058` | Troisième canal Q × I × M, distinct des deux P sig bruts |
| Tension tryperposition maximale | `1.3591909615` | `27.8677038941` | Canal actif ; la seconde valeur dépend du profil `alpha_0=0.05` |
| Pas de condition de collapse | `5, 6` sans intervention | `2, 3, 5, 6, 7, 9, 10` | Conditions de scénario, pas effondrements matériels observés |

Le `P_sig` de graphe n’a produit aucun cycle H1 fini dans cette exécution ; sa référence initiale est donc zéro. Conformément au contrat, `graph_tension=null` aux onze pas avec une raison explicite. Il aurait été incorrect de diviser par un epsilon ou de remplacer cette signature par le `P_sig` logique. Cette valeur nulle est une information utile sur ce graphe de corrélation et ce seuil Rips précis.

Le canal de tryperposition maintient cependant la dynamique active sans altérer ce constat. Il combine la cohérence de densité `Q`, une amplitude informationnelle `I` calculée à partir du `P_sig` graphe, du `P_sig` logique et de la corrélation, puis `M`, un témoin d’intégrité de trace. Il ne constitue ni une correction d’erreur, ni une preuve ZK, ni une équivalence physique à une superposition matérielle. Il est la voie instrumentée du scénario LCT-ETH, tandis que les trois signaux source sont conservés dans chaque pas.

Le profil de sensibilité possède une abscisse active `alpha_0=0.05`, distincte de `alpha_0=1.0` pour la baseline. Ses sept conditions de tension tryperposition ont effectivement déclenché le canal local de déphasage déclaré dans ce **seul** scénario. La baseline a franchi sa propre condition aux pas 5 et 6 mais ne déclenche aucun canal, car elle est observationnelle. Les métriques LCT et ETH portent l’étiquette `pre_intervention_density`, tandis que l’état de sortie et l’entropie post-intervention restent dans des champs séparés. Le résultat ne démontre donc pas une protection, une correction ou un mécanisme cryogénique ; il documente l’effet de cette hypothèse de scénario sur la simulation.

Les figures [`incubator-entropy-eth.png`](assets/incubator-entropy-eth.png) et [`incubator-topology-lct.png`](assets/incubator-topology-lct.png) sont dérivées exclusivement de cet artefact. La première rend visible les entropies, le taux ETH et les seuils candidats. La seconde montre explicitement la séparation entre `P_sig` logique et `P_sig` de graphe nul.

## Reproduction

```bash
PYTHONPATH=/path/to/ratiss-topological-decoherence-engine/src \
python3 scripts/run_cosmos.py \
  --engine-src /path/to/ratiss-topological-decoherence-engine/src \
  --output artifacts/cosmos_run.json --shots 256

PYTHONPATH=/path/to/ratiss-topological-decoherence-engine/src \
python3 scripts/run_incubator.py \
  --engine-src /path/to/ratiss-topological-decoherence-engine/src \
  --output artifacts/incubator_lct_eth_run.json

python3 scripts/generate_incubator_figures.py \
  --input artifacts/incubator_lct_eth_run.json \
  --output-dir docs/assets \
  --summary artifacts/incubator_lct_eth_summary.json
```

## Référence

[1] [Qiskit Aer — Exact and noisy simulation](https://quantum.cloud.ibm.com/docs/guides/simulate-with-qiskit-aer)
