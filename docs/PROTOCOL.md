# Protocole COSMOS — QPU virtuel RATISS

## Question expérimentale

Mesurer comment un circuit GHZ distribué évolue sous un **modèle de bruit explicitement déclaré** dans Qiskit Aer, puis transformer uniquement les *counts* obtenus en une timeline RATISS d’associations. Une seconde piste, à cinq qubits, emploie la matrice densité et le noyau `TopologicalQubit` algorithmique RATISS afin de conserver séparées la trajectoire de circuit et la signature logique simulée.

## Trois régimes complémentaires

| Régime | Taille | Sortie observée | Ce qui est calculé | Ce qui n’est pas affirmé |
|---|---:|---|---|---|
| `counts_scaling` | 8, 12, 16, 20 qubits | Counts Aer à plusieurs profondeurs | Masse de parité GHZ et associations normalisées | Tomographie, persistance logique ou comportement d’un appareil IBM réel |
| `density_topology` | 5 qubits | Matrices densité idéale et bruitée à chaque porte | Fidélité, pureté, cube de corrélations, topologie de graphe et sidecar RATISS | Qubit topologique matériel, correction d’erreur ou calibration QPU |
| `incubator_lct_eth` | 5 qubits | Deux trajectoires densité à chaque frontière de porte | Entropie, taux ETH interne, facteur LCT, impacts, tension et route TSP d’inspection | ETH statistique, QPU, calibration en température ou correction d’erreur |

Le modèle de bruit est un canal Pauli/dépolarisant déclaré dans l’artefact. Il n’est pas nommé « IBM-like » et ne provient d’aucune calibration de périphérique.

## Critères de sortie

Chaque exécution écrit sa configuration exacte, les versions logicielles, le seed éventuel, les counts bruts et les métriques dérivées. Une valeur `P_sig` reste celle produite par son calcul : aucune valeur n’est remplacée lorsque le résultat est nul, faible ou inattendu. Les erreurs d’exécution, sorties vides et écarts entre bruit faible et bruit fort sont conservés comme résultats.

## Extension incubateur : baseline et sensibilité distinctes

L’incubateur enregistre une baseline `baseline_observational` qui observe le circuit Aer sans modifier sa matrice densité lorsque la condition de tension est satisfaite. La dérive de cette trajectoire est l’objet de mesure. La condition active est issue de `P_sig_tryperposition`, calculé par la composition Q × I × M ; `graph_P_sig` reste publié séparément, y compris lorsqu’il vaut zéro et que `graph_tension=null`. Un second scénario, `lct_eth_sensitivity_local_dephasing`, peut appliquer un canal local `Z` uniquement après avoir enregistré les métriques de pré-intervention. Le canal, sa force, les qubits affectés et chaque pas de condition satisfaite sont versionnés dans l’artefact ; la baseline n’est ni réécrite ni remplacée.

Le contrat complet, les conventions d’entropie, la règle de `null` pour un dénominateur nul et le statut de la température figurent dans [`INCUBATOR_CONTRACT.md`](INCUBATOR_CONTRACT.md). Le contrat ne transforme pas `temperature_millikelvin` en `T1`, `T2` ou durée de porte : ces derniers restent des paramètres Aer déclarés distinctement. [1]

## Références de mise en œuvre

Qiskit Aer documente les modèles de bruit configurables et `AerSimulator` [1]. La conversion des counts au format d’association RATISS reste une analyse structurelle, distincte d’une matrice densité.

[1] [Qiskit Aer — Building Noise Models](https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html)
