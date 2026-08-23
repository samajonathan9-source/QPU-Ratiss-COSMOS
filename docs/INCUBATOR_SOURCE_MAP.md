# Carte de réemploi — Incubateur COSMOS

## Révisions auditées

Les sources ci-dessous ont été lues en **lecture seule**. COSMOS réimplémente seulement un adaptateur expérimental : aucun de ces dépôts source n’est modifié par cette extension.

| Dépôt source | Révision auditée | Élément réemployé conceptuellement | Décision pour COSMOS |
|---|---|---|---|
| `Ratiss-experimental-IA-` | `501fd7d0a59123a2b8de95aa3b9c5a98aff7a25a` | `lct_neuron.py` : phase et cohérence ; `lct_network.py` : calcul de `P_sig` par pas ; v2/v3 : historique des essais de gradient/proxy | Reprendre la structure de mesure LCT, pas l’entraînement neuronal ni le bootstrap de `P_sig=0`. |
| `Ratiss-experimental-IA-` | même révision | `lct_collapse.py` : événement conditionné, cohérence oscillante, marque topologique distincte d’énergie | Conserver l’idée d’événement tracé ; ne jamais effacer la valeur de `P_sig` observée. |
| `RATISS-ODV-AEON` | `3dfe46be82bd340c13ad724e2c0c2b6accf4003a` | `ttf_compute.py` : graphe intriqué, oscillation, porteuse, Rips, impact, micro-update et route TSP | Reprendre l’ordre d’observation et la séparation oscillation → topologie → impact → TSP. |
| `RATISS-ODV-AEON` | même révision | `lct_law.py` : `P_sig` H1, `P_noise`, phase, cohérence, scan de monotonie | Conserver `P_sig=0.0` lorsqu’aucun H1 fini n’existe ; conserver la séparation énergie/forme. |
| `RATISS-ODV-AEON` | même révision | `tryperposition_solver.py` : couches Q × I × M, oscillation et métriques thermodynamiques | Reprendre la séparation de couches sur les valeurs Aer calculées, sans importer les landmarks aléatoires ou un reçu ZK comme observation du circuit. |
| `Porte-folio-Jonathan-` | `fb1891f460167d975790fdb4873369e63459c8d4` | `warp/eth/progressive_collapse.py` : trajectoire progressive, mesures par pas et saut observé | Réutiliser le patron de trajectoire, sans importer ses objectifs de convergence ou ses seuils vers le circuit Aer. |

## Ce qui est hérité fidèlement

Le facteur LCT est hérité comme instrument de mesure : une phase `phi`, une cohérence `C`, un `P_sig` calculé et une amplitude candidate `eta × phi × P_sig × C`. Le noyau TTF confirme également qu’une topologie peut être calculée après oscillation et que l’impact peut guider une route TSP d’inspection. [1] [2]

Le sidecar `TopologicalQubit` du moteur de décohérence est lui aussi réemployé sans modification. Il est algorithmique et demeure distinct de la matrice densité : ses champs logique, phase, twist et cohérence enrichissent l’artefact sans devenir des observations matérielles. [3]

## Ce qui est nouveau et explicitement expérimental

La mesure de von Neumann, le `delta_entropy_bits`, le taux ETH et le rapport de tension construits à partir de la matrice densité sont de nouveaux adaptateurs COSMOS. Aucun module lu ne fournit une implémentation de l’ETH des feuilles qui combine directement entropie de matrice densité Aer, `P_sig` de graphe et tension LCT. L’incubateur les implémente donc comme une hypothèse instrumentée, avec un modèle de données qui conserve les échecs et les indéterminations.

Le `P_sig_tryperposition` est un adaptateur supplémentaire. Il conserve la forme Q × I × M du solveur AEON, avec une couche Q issue de la cohérence de densité Aer, une couche I composée de `graph_P_sig`, `logical_P_sig` et de l’amplitude de corrélation, puis une couche M issue de l’intégrité de trace de `rho`. Cette voie active LCT/ETH quand `graph_P_sig=0.0` sans modifier ce zéro brut.

L’équation de pression contenant température et diaphonie est également introduite comme **indicateur expérimental de profil**. Les sources auditées n’établissent pas de loi qui transforme une température exprimée en mK en `T1`, `T2` ou temps de porte Aer. Ces paramètres restent indépendants et déclarés.

## Ce qui est volontairement exclu

| Élément source ou proposition | Motif d’exclusion de la baseline |
|---|---|
| Bootstrap aléatoire lorsque `P_sig=0` de LCT v2 | Il changerait une sortie nulle réelle, contraire au contrat de l’incubateur. |
| Optimisation ou maximisation de `P_sig` | L’incubateur mesure la trajectoire ; il ne pilote pas le résultat vers une topologie cible. |
| Collapse qui modifie immédiatement l’état de baseline | Un éventuel canal local sera un scénario séparé et comparé à une baseline immuable. |
| Interprétation de la température en calibration QPU | Aucun lien de calibration audité ne le justifie. |
| TSP comme solveur d’avantage global | Le TSP ne sert qu’à l’inspection d’un sous-graphe dérivé. |

## Références

[1] [RATISS-Experimental-IA — LCT et collapse](https://github.com/evinajonathan13-max/Ratiss-experimental-IA-/tree/main/ratis_net)

[2] [RATISS-ODV-AEON — TTF, LCT et TSP](https://github.com/evinajonathan13-max/RATISS-ODV-AEON/tree/main/kernel)

[3] [Moteur RATISS — qubit topologique algorithmique](https://github.com/evinajonathan13-max/ratiss-topological-decoherence-engine/blob/main/src/ratiss_topological_decoherence/logical_qubit.py)

[4] [RATISS-ODV-AEON — solveur de tryperposition](https://github.com/evinajonathan13-max/RATISS-ODV-AEON/blob/main/kernel/solvers/tryperposition_solver.py)
