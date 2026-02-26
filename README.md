# new_AI_version

Prototype d'**IA locale** orientée vers une dynamique bio-inspirée avec cinq propriétés clés :

1. **Système auto-organisé** (priorités internes adaptatives)
2. **Continuité temporelle** (mémoire d'état sur chaque pas)
3. **Régulation corporelle** (énergie/température/hydratation)
4. **Intégration hormonale** (cortisol, dopamine, sérotonine, mélatonine)
5. **Auto-modélisation constante** (cohérence, confiance, bonheur)

## Extensions ajoutées

- **Monde 3D exploré en continu temps réel** (`World3D`)
- **Cube de lumière** (`SoulLightCube`) qui archive l'âme d'une IA quand elle décède
- **Sexe biologique** (`male` / `feminin`) pour chaque agent
- **Reproduction** avec naissance d'un enfant `male` ou `feminin`
- **Deux IA initiales optimisées** pour un départ stable et heureux
- **Découverte d'endpoints de matrice locale** (`discover_matrix_endpoints`)
- **Bridge binaire machine-to-machine** (`MachineCodeBridge`) pour traduire des protocoles différents

## Lancer localement

```bash
python3 src/local_ai.py
```

Par défaut, la démo tourne en **temps réel sans limite de durée** (arrêt manuel), avec un tick toutes les 100 ms.

## Structure

- `AgentAI` : boucle cognitive d'un agent
- `World3D` : monde, déplacement 3D, conditions terrain, population
- `SoulLightCube` : sauvegarde des essences d'agents décédés
- `MatrixEndpoint` : représentation des points de terminaison internes
- `MachineCodeBridge` : encapsulation/décapsulation de trames binaires
- `BodyState` / `HormonalState` / `SelfModel` : équilibre interne et bonheur

## Personnaliser

Tu peux modifier :
- les règles hormonales (`HormonalState.integrate`)
- les coûts métaboliques (`BodyState.regulate`)
- la politique de décision (`AgentAI.decide_actions`)
- les règles de naissance (`World3D.try_reproduction`)
- la durée/fréquence temps réel (`run_demo`)
