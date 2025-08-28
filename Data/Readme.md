# Synthèse : Projet Data Lake NBA

## 1. Liste des questions d'analyse

1. **Quels sont les joueurs ayant le plus progressé statistiquement sur les 5 dernières saisons ?**
2. **Quels sont les matchs les plus spectaculaires en termes de scoring, de rebonds, d’assists, etc. ?**
3. **Quels sont les joueurs les plus décisifs dans les derniers quarts-temps ?**
4. **Quelles sont les tendances d’affluence dans les salles NBA, et leur relation avec la performance des équipes ?**
5. **Quels sont les records individuels et collectifs et comment ont-ils évolué au fil des décennies ?**
6. **Analyse de la parité salariale entre joueurs, équipes, et son impact sur le jeu ?**

---

## 2. Mapping : Questions <-> Sources de données

| Question | Sources principales & Récupération |
|----------|----------------------------------------------------------------|
| 1. Progression joueurs | NBA Stats API se trouve dans (Player/General/Traditional) et filtré sur (Regular Season/Totals/All Season Segment)
| 2. Matchs spectaculaires | Kaggle | plus de statistiques retrouver dans ces games |
| 3. Joueurs décisifs | NBA Stats API se trouve dans (Player/Clutch/Traditional) et filtré sur (Regular Season/Totals/All Season Segment) |
| 4. Affluence salles | Kaggle Avec le csv game_info |
| 5. Records | NBA Stats API & Kaggle |
| 6. Salaires | Hoopshype |

---

## 3. Exemples de sources de données

- **NBA Stats API** : [stats.nba.com](https://stats.nba.com/)
- **Kaggle Datasets NBA** : [kaggle.com/datasets?search=nba](https://www.kaggle.com/datasets?search=nba)
- **ESPN NBA** : [espn.com/nba](https://www.espn.com/nba/)
- **Hoopshype Salaries** : [hoopshype.com/salaries](https://hoopshype.com/salaries/)
