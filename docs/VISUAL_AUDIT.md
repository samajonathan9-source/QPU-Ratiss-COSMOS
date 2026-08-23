# Vérification visuelle des figures

## `cosmos-counts-scaling.png`

La figure affiche quatre tailles de registre réellement présentes dans `artifacts/cosmos_run.json`. Les deux courbes restent distinguables : la masse dominante Aer idéale est en vert et la masse sous bruit CX déclaré est en corail. Les axes, les unités de masse et la légende sont lisibles sur fond sombre ; aucun point ou texte ne sort du cadre.

La figure ne montre pas de métrique topologique et ne suggère pas une validation sur matériel.

## `incubator-entropy-eth.png`

La première figure représente directement les deux scénarios de `artifacts/incubator_lct_eth_run.json`. Les courbes d’entropie distinguent la baseline, la mesure de sensibilité avant intervention et la sortie après intervention. Les lignes verticales rouges sont les pas où la condition candidate de tension logique est satisfaite dans le scénario de sensibilité ; elles ne représentent pas une mesure QPU ni une loi physique validée.

Le panneau inférieur conserve ensemble le taux ETH de la baseline, la tension logique du scénario de sensibilité et son seuil paramétré. Les deux échelles restent lisibles, les légendes ne recouvrent pas les données et les différences de trajectoire ne sont pas lissées.

## `incubator-topology-lct.png`

La seconde figure conserve visiblement séparés `P_sig` de graphe, `P_sig` logique du sidecar et cohérence logique. La courbe de graphe est bien affichée à `0.0` pour tous les pas : elle n’est pas remplacée par la signature logique. Les croix rouges du panneau inférieur signalent que la tension de graphe est indisponible lorsque son dénominateur dépend d’un `P_sig` de référence nul.

Les axes et légendes sont lisibles. La figure visualise des métriques d’une simulation locale et d’un sidecar algorithmique ; elle ne suggère ni qubit topologique matériel ni calibration cryogénique.
