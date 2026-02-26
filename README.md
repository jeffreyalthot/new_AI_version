# new_AI_version

Prototype d'**IA locale** orientée vers une dynamique bio-inspirée avec cinq propriétés clés :

1. **Système auto-organisé** (priorités internes adaptatives)
2. **Continuité temporelle** (mémoire d'état sur chaque pas)
3. **Régulation corporelle** (homéostasie énergie/température/hydratation)
4. **Intégration hormonale** (cortisol, dopamine, sérotonine, mélatonine)
5. **Auto-modélisation constante** (mise à jour continue de la cohérence et des priorités)

## Lancer localement

```bash
python3 src/local_ai.py
```

## Structure

- `LocalOrganizingAI` : boucle principale (perception → hormones → action → corps → mémoire → auto-modèle)
- `BodyState` : état corporel et régulation
- `HormonalState` : signaux hormonaux
- `SelfModel` : auto-évaluation et priorités émergentes

## Personnaliser

Tu peux modifier :
- les règles de mise à jour hormonale (`HormonalState.integrate`)
- les coûts métaboliques (`BodyState.regulate`)
- la politique de décision (`LocalOrganizingAI.decide_actions`)
- la fonction de récompense interne (`compute_internal_reward`)
