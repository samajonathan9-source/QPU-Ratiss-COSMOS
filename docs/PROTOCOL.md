# Protocole COSMOS — QPU virtuel RATISS

## Question expérimentale

Mesurer comment un circuit GHZ distribué évolue sous un **modèle de bruit explicitement déclaré** dans Qiskit Aer, puis transformer uniquement les *counts* obtenus en une timeline RATISS d’associations. Une seconde piste, à cinq qubits, emploie la matrice densité et le noyau `TopologicalQubit` algorithmique RATISS afin de conserver séparées la trajectoire de circuit et la signature logique simulée.

## Deux régimes complémentaires

| Régime | Taille | Sortie observée | Ce qui est calculé | Ce qui n’est pas affirmé |
|---|---:|---|---|---|
| `counts_scaling` | 8, 12, 16, 20 qubits | Counts Aer à plusieurs profondeurs | Masse de parité GHZ et associations normalisées | Tomographie, persistance logique ou comportement d’un appareil IBM réel |
| `density_topology` | 5 qubits | Matrices densité idéale et bruitée à chaque porte | Fidélité, pureté, cube de corrélations, topologie de graphe et sidecar RATISS | Qubit topologique matériel, correction d’erreur ou calibration QPU |

Le modèle de bruit est un canal Pauli/dépolarisant déclaré dans l’artefact. Il n’est pas nommé « IBM-like » et ne provient d’aucune calibration de périphérique.

## Critères de sortie

Chaque exécution écrit sa configuration exacte, les versions logicielles, le seed éventuel, les counts bruts et les métriques dérivées. Une valeur `P_sig` reste celle produite par son calcul : aucune valeur n’est remplacée lorsque le résultat est nul, faible ou inattendu. Les erreurs d’exécution, sorties vides et écarts entre bruit faible et bruit fort sont conservés comme résultats.

## Références de mise en œuvre

Qiskit Aer documente les modèles de bruit configurables et `AerSimulator` [1]. La conversion des counts au format d’association RATISS reste une analyse structurelle, distincte d’une matrice densité.

[1] [Qiskit Aer — Building Noise Models](https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html)
