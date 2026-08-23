# Session conjointe — Incubateur topologique quantique COSMOS

## But de la session

Cette session sert à rejouer exactement les artefacts versionnés, à inspecter les relations réellement produites par Aer et à formuler la prochaine hypothèse de manière traçable. Elle ne cherche pas à faire monter `P_sig`, à masquer une tension `null` ou à utiliser la température comme un raccourci pour modifier `T1` ou `T2`.

> La baseline est la référence à préserver. Toute hypothèse active doit créer un nouveau fichier de sortie et un nom de scénario distinct.

## Étape 1 — Rejouer la référence

Depuis la racine du dépôt, installer les dépendances puis relancer les deux scénarios avec le chemin local vers le moteur topologique.

```bash
python3 -m pip install -e .

PYTHONPATH=/chemin/vers/ratiss-topological-decoherence-engine/src \
python3 scripts/run_incubator.py \
  --engine-src /chemin/vers/ratiss-topological-decoherence-engine/src \
  --output artifacts/incubator_lct_eth_replay.json

python3 scripts/generate_incubator_figures.py \
  --input artifacts/incubator_lct_eth_replay.json \
  --output-dir docs/assets/replay \
  --summary artifacts/incubator_lct_eth_replay_summary.json

pytest -q
```

La référence actuelle compte onze frontières de porte par scénario. Elle conserve `graph_P_sig=0.0` à chaque pas, une tension de graphe `null` avec une raison explicitement enregistrée et une signature logique séparée. Une différence doit être notée avant toute interprétation.

## Étape 2 — Lire les quatre contrastes utiles

| Contraste à lire | Où le trouver | Question de test |
|---|---|---|
| Baseline vs sensibilité | `scenarios` dans l’artefact | L’intervention déclarée modifie-t-elle l’entropie post-intervention, sans réécrire la baseline ? |
| Graphe vs sidecar | `topology.graph_P_sig` et `topology.logical_P_sig` | Les deux plans restent-ils distincts lorsque le graphe ne contient aucun H1 fini ? |
| Avant vs après intervention | `pre_intervention_density` et `density` | Le canal local n’est-il appliqué qu’aux pas ayant `intervention.applied=true` ? |
| Impact vs TSP | `impact.eligible_qubits` et `tsp_inspection` | La route inspecte-t-elle seulement les nœuds réellement sélectionnés, sans prétendre résoudre un TSP global ? |

## Étape 3 — Préparer une nouvelle hypothèse

Une expérimentation doit partir d’un duplicat nommé du profil, modifier un seul paramètre à la fois, puis écrire un nouvel artefact. Les paramètres investigables sont `alpha_0`, `collapse_threshold`, `impact_threshold`, `omega_lct`, les paramètres de bruit Aer et les paramètres de pression de profil. La température reste une métadonnée tant qu’une relation de calibration indépendante vers `T1`, `T2` ou les durées de porte n’est pas apportée.

Avant de considérer un résultat, comparer les tableaux récapitulatifs et poser quatre questions : le `P_sig` de graphe est-il calculé ou substitué ; une tension est-elle une valeur finie ou `null` ; une intervention a-t-elle été appliquée ; et les variations concernent-elles la simulation ou un matériel réel ?

## Issue attendue de la session

La sortie utile est un court journal avec le nom d’artefact, le profil modifié, les pas concernés, les valeurs inattendues et une décision claire : conserver, investiguer ou invalider l’hypothèse. Une valeur nulle, une instabilité ou une absence de collapse constituent des résultats à conserver.
