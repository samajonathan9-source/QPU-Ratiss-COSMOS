# Contrat expérimental — Incubateur topologique quantique RATISS

## Statut et objectif

L’incubateur est une **extension expérimentale locale de COSMOS**. Il observe, à chaque frontière de porte d’un circuit à cinq qubits, une matrice densité Aer bruitée, sa topologie de graphe, un sidecar de qubit topologique algorithmique RATISS, des métriques thermodynamiques calculées et des facteurs LCT. Son objectif est de garder ensemble les sorties réellement calculées afin d’explorer des relations, non d’imposer une protection, une correction ou un comportement souhaité.

> **ETH désigne ici « effondrement thermodynamique »**, le nom interne de la métrique de variation d’entropie de cette expérience. Ce terme ne désigne pas l’*Eigenstate Thermalization Hypothesis* de la physique statistique.

Le circuit est simulé par `AerSimulator(method="density_matrix")` avec les canaux `thermal_relaxation_error(T1, T2, gate_time)` et dépolarisants déjà déclarés dans le moteur. La trajectoire est donc une simulation locale de bruit paramétré, et non une exécution QPU, une calibration cryogénique ou une certification de qubit topologique matériel. [1]

## Principes non négociables

Chaque métrique est calculée puis conservée dans l’artefact, y compris `0.0`, valeur négative, liste vide et `null`. Le noyau ne remplace jamais `P_sig`, la cohérence, l’entropie, le taux ETH ou la tension afin de rendre une figure plus lisible. Lorsqu’un dénominateur est nul, la grandeur qui en dépend est `null` avec une raison explicite : elle n’est pas remplacée par un epsilon caché.

| Règle | Conséquence dans l’artefact |
|---|---|
| Les trois `P_sig` sont différents | `graph_P_sig`, `logical_P_sig` et `P_sig_tryperposition` restent séparés à chaque pas. |
| Une grandeur ne s’applique pas | Elle est `null` et son champ `*_scope` explique pourquoi. |
| Une intervention est testée | Elle est une **scénario séparé** qui conserve aussi une baseline observationnelle intacte. |
| Une loi est candidate | Elle est étiquetée `experimental_candidate`, jamais présentée comme une loi matérielle validée. |
| Une température est indiquée | Elle est une métadonnée de profil, sauf si une loi de calibration distincte et vérifiée est apportée. |

## Les trois plans de mesure

L’incubateur ne mélange pas les plans de données. La couche densité provient du simulateur Aer ; la couche logique provient de `TopologicalQubit`, un sidecar algorithmique ; et la couche graphe utilise la persistance H1 des corrélations mutuelles. Le couplage LCT/ETH les observe ensemble, mais n’écrase pas l’une avec l’autre. [2] [3]

| Plan | Source calculée | Champs principaux | Interprétation admise |
|---|---|---|---|
| Densité Aer | `rho_noisy` à chaque préfixe du circuit | entropie, pureté, matrice de corrélation, T1/T2, temps de porte | Simulation locale du canal de bruit déclaré. |
| Graphe de corrélations | Rips sur corrélations de la densité | `graph_topology.P_sig`, Betti, matrice `M` | Signature de persistance du graphe construit pour ce pas. |
| Sidecar logique | `TopologicalQubit` RATISS | `logical_topology.P_sig`, phase, twist, cohérence, état `protected` | Simulation algorithmique séparée, sans revendication de porte topologique matérielle. |
| LCT/ETH | Adaptateur incubateur | phase signée, facteur LCT, delta entropie, tension, impact, route TSP | Instrumentation expérimentale calculée à partir des trois plans précédents. |
| Tryperposition active | Composition `Psi = Q x I x M` | `P_sig_tryperposition`, tension active, facteurs LCT actifs | Canal calculé qui coexiste avec les sorties brutes ; ce n’est ni un fallback ni une preuve ZK. |

## Variables et convention de temps

Un pas `k` correspond à un préfixe du circuit : `k=0` est l’état initial et `k>0` suit l’application de la porte `gate[k-1]`. Le temps discret vaut `t_k = k × dt`, où `dt` est un paramètre de protocole déclaré ; il n’est pas confondu avec le temps de porte utilisé par Aer dans le bruit thermique. Par défaut, `dt=1.0` est une unité de pas de trajectoire, non une seconde physique.

| Champ | Calcul | Domaine et statut |
|---|---|---|
| `entropy_bits` | `-Σ λ log2(λ)` sur les valeurs propres de `rho_noisy` | Entropie de von Neumann de la simulation densité. Les valeurs propres négatives de très faible amplitude numérique sont journalisées dans le diagnostic puis exclues seulement du logarithme. |
| `delta_entropy_bits` | `S_k − S_(k−1)` | `null` à l’initialisation. Le signe est conservé. |
| `eth_rate_bits_per_step` | `delta_entropy_bits / dt` | Mesure interne du changement entropique ; aucune signification d’ETH statistique n’est inférée. |
| `purity_global` | `Re[Tr(rho²)]` | Mesure globale calculée directement sur la matrice densité. |
| `density_coherence_proxy` | `1 − entropy_bits / n_qubits` | Proxy dérivé de la densité, sans seuil, clamp ou remplacement. |
| `M` | matrice de corrélations mutuelles déjà exportée par le moteur | Sert à la variation matricielle et aux impacts ; ce n’est pas une matrice électromagnétique. |
| `gradient_frobenius` | `||M_k − M_(k−1)||_F / dt` | `null` au pas initial. |
| `oscillation_stress` | `gradient_frobenius × (1 − purity_global)` | Transcription expérimentale de la proposition `Ω`; aucune action sur `rho` dans la baseline. |
| `P_sig_tryperposition` | `Q × I × M` décrit ci-dessous | Troisième signature calculée, distincte des signaux graphe et logique. |

## LCT libre : facteur observé, pas commande cachée

Les noyaux RATISS-Net et TTF emploient une phase oscillante et une amplitude modulée par la cohérence dans la règle `ΔW = η × φ × P_sig × C`. [4] [5] L’incubateur reprend cette structure **comme mesure de couplage** et non comme une mise à jour forcée de la densité quantique.

Pour chaque pas, il enregistre trois formulations sans substituer leurs sources :

```text
phase_signed = cos(omega_lct × t_k)
phase_amplitude = abs(phase_signed)
lct_factor_graph = phase_signed × graph_P_sig × density_coherence_proxy
lct_factor_logical = phase_signed × logical_P_sig × logical_coherence
candidate_delta_w_graph = eta_lct × lct_factor_graph
candidate_delta_w_logical = eta_lct × lct_factor_logical
lct_factor_tryperposition = phase_signed × P_sig_tryperposition × density_coherence_proxy
candidate_delta_w_tryperposition = eta_lct × lct_factor_tryperposition
```

`logical_P_sig` et `logical_coherence` sont valides uniquement parce que cette trajectoire est une simulation densité couplée au sidecar. Dans un chemin counts, photonique ou bio non densité, `logical_P_sig` doit rester `null` et les facteurs logiques associés sont eux aussi `null`. [2]

## Tryperposition active : `Psi = Q x I x M`

Le solveur AEON de tryperposition sépare une couche quantique, une couche informationnelle et une couche matérielle, avec une dynamique thermodynamique distincte. [7] COSMOS reprend cette séparation sur les sorties déjà calculées au pas `k`, sans importer les landmarks aléatoires ou un reçu ZK dans la trajectoire Aer :

```text
Q_k = density_coherence_proxy(rho_k)
I_k = sqrt(graph_P_sig_k² + logical_P_sig_k² + correlation_amplitude_k²)
M_k = 1 - abs(Re[Tr(rho_k)] - 1)
P_sig_tryperposition_k = Q_k × I_k × M_k
```

`P_sig_tryperposition` est un troisième signal et non un fallback. Si `graph_P_sig=0.0`, le zéro et sa tension de graphe `null` restent inchangés ; la tryperposition est simplement calculée à partir de Q, I et M observés. Le canal LCT/ETH actif emploie sa propre référence initiale, sa propre tension et l’étiquette `active_tension_channel="tryperposition"`.

## Topologie, tension et condition d’effondrement

La tension de graphe proposée par les feuilles est calculée de façon transparente :

```text
P_sig_reference = graph_P_sig au pas initial
A = alpha_0 × P_sig_reference
tension = oscillation_stress / (A × graph_P_sig)
```

Si `P_sig_reference`, `A` ou `graph_P_sig` vaut zéro, `graph_tension` est `null` et `graph_tension_unavailable_reason` est renseigné. Cette branche est intentionnelle : une persistance H1 nulle est une sortie valide et ne peut pas être remplacée par une référence logique, un plancher ou une constante.

La tension active est calculée indépendamment avec `P_sig_tryperposition_reference` et `P_sig_tryperposition`; elle est enregistrée dans `tryperposition_tension` puis dans `active_tension`. La condition candidate d’un scénario s’appuie sur `active_tension`, jamais sur une valeur de graphe substituée.

L’impact par qubit est calculé sur la matrice `M` :

```text
impact_i = Σ(j != i) abs(M_k[i,j] − M_(k−1)[i,j]) / dt
```

La baseline est **observationnelle**. Même si `tension > collapse_threshold`, elle marque un événement candidat, les impacts et les qubits sélectionnés, mais ne modifie ni `rho`, ni les deux `P_sig`, ni la cohérence. Un scénario `lct_eth_local_dephasing_experimental` pourra appliquer un canal de déphasage local aux qubits sélectionnés ; ce scénario sera exécuté séparément, portera l’opérateur, le taux et les indices réellement appliqués, et ne remplacera jamais la baseline.

## Pression ETH et profil cryogénique

Le profil contient `temperature_millikelvin`, `T1`, `T2`, les durées de portes, le bruit dépolarisant et le coefficient `kappa`. `T1`, `T2` et les durées de portes alimentent réellement le modèle Aer. La température est à ce stade une métadonnée de protocole : l’incubateur ne dérive pas `T1` ou `T2` de sa valeur sans modèle de matériau et calibration vérifiés.

La pression candidate est seulement un indicateur documenté :

```text
crosstalk_proxy = moyenne(abs(M[i,j])) pour i != j
eth_pressure_indicator = beta × (temperature_mK / temperature_reference_mK)^gamma × (1 + kappa × crosstalk_proxy)
```

`crosstalk_proxy` est une statistique de corrélation de simulation et **pas** une mesure électromagnétique. `eth_pressure_indicator` n’est pas envoyé au bruit Aer dans la baseline. Il sert à comparer des trajectoires explicitement paramétrées.

Dans l’architecture de l’incubateur, ETH joue le rôle d’**environnement virtuel de cryogénie** qui encapsule le QPU logiciel : la variation d’entropie par pas mesure ce que le « bain » environnant échange avec le qubit logique simulé, et la température de `15 mK` est la métadonnée de cette enveloppe. Cette équivalence est **instrumentée et logicielle** : elle structure la lecture des trajectoires (baseline versus sensibilité) comme un cryostat structure une expérience, sans jamais prétendre reproduire la thermodynamique d’un dispositif réel ni calibrer un cryostat.

## Rôle du TSP

Le TSP reste un outil de **sélection et d’inspection postérieure**. À partir des qubits d’impact ou critiques réellement calculés, le moteur produit une route courte d’inspection. Sur un ensemble petit, une recherche exacte peut être utilisée ; au-delà, une heuristique doit annoncer son nom. Cette route n’est ni une correction de l’état ni une preuve d’avantage sur une instance TSP globale. [6]

## Schéma minimal d’artefact

```json
{
  "schema": "ratiss.cosmos.incubator.v1",
  "provenance": {"validated_on_hardware": false, "scenario": "baseline_observational"},
  "noise_profile": {"temperature_millikelvin": 15.0, "temperature_role": "metadata_only", "t1_seconds": 0.0001},
    "reference": {"graph_P_sig_reference": 0.0, "P_sig_tryperposition_reference": 0.0},
  "steps": [{
    "step": 0,
    "gate": "initial",
    "density": {"entropy_bits": 0.0, "delta_entropy_bits": null, "purity_global": 1.0},
    "topology": {"graph_P_sig": 0.0, "logical_P_sig": 0.0, "P_sig_tryperposition": 0.0},
    "lct": {"phase_signed": 1.0, "lct_factor_graph": 0.0, "active_P_sig_channel": "tryperposition"},
    "eth": {"eth_rate_bits_per_step": null, "graph_tension": null, "active_tension": null, "collapse_observed": false},
    "tsp_inspection": {"method": "none", "route": []}
  }]
}
```

Ce fragment illustre que `0.0` et `null` sont des sorties différentes. Il n’annonce pas une valeur attendue pour une exécution future.

## Critères de test

Les tests de contrat devront vérifier que l’artefact contient tous les pas, que `delta_entropy_bits` est nul uniquement à l’initialisation, que les valeurs calculées ne sont pas substituées, que les branches à dénominateur nul produisent `null`, et que la baseline ne modifie pas la densité après détection. Les tests distinguent `graph_P_sig`, `logical_P_sig` et `P_sig_tryperposition`, ainsi que la température-métadonnée des paramètres Aer réellement appliqués.

## Références

[1] [Qiskit Aer — modèles de bruit](https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html)

[2] [Moteur RATISS — import de corrélations et scopes non densité](https://github.com/evinajonathan13-max/ratiss-topological-decoherence-engine/blob/main/src/ratiss_topological_decoherence/correlation_import.py)

[3] [Moteur RATISS — simulation densité et sidecar topologique](https://github.com/evinajonathan13-max/ratiss-topological-decoherence-engine/blob/main/src/ratiss_topological_decoherence/simulation.py)

[4] [RATISS-Experimental-IA — neurone LCT](https://github.com/evinajonathan13-max/Ratiss-experimental-IA-/blob/main/ratis_net/lct_neuron.py)

[5] [RATISS-ODV-AEON — moteur TTF et micro-update LCT](https://github.com/evinajonathan13-max/RATISS-ODV-AEON/blob/main/kernel/ttf/ttf_compute.py)

[6] [RATISS-ODV-AEON — audit TSP](https://github.com/evinajonathan13-max/RATISS-ODV-AEON/blob/main/kernel/redteam/tsp_attacker.py)

[7] [RATISS-ODV-AEON — solveur de tryperposition](https://github.com/evinajonathan13-max/RATISS-ODV-AEON/blob/main/kernel/solvers/tryperposition_solver.py)
