# Synthèse : Projet Data Lake NBA

## 1. Liste des questions d'analyse

1. **Quels sont les joueurs ayant le plus progressé statistiquement sur les 5 dernières saisons ?**
2. **Quels sont les facteurs qui influencent la victoire d’une équipe (statistiques individuelles, collectives, contexte, etc.) ?**
3. **Quelles sont les tendances de blessures par poste, par saison, par équipe ?**
4. **Quels sont les matchs les plus spectaculaires en termes de scoring, de rebonds, d’assists, etc. ?**
6. **Quels sont les joueurs les plus décisifs dans les derniers quarts-temps ?**
8. **Comment les statistiques des rookies évoluent sur leurs premières saisons ?**
9. **Quel est l’impact de la géographie des matchs (domicile/extérieur, fuseau horaire) sur les résultats ?**
10. **Quelles sont les tendances d’affluence dans les salles NBA, et leur relation avec la performance des équipes ?**
12. **Quels sont les records individuels et collectifs et comment ont-ils évolué au fil des décennies ?**
13. **Quels sont les liens entre statistiques avancées (PER, BPM, Win Shares…) et le palmarès des joueurs ?**
14. **Analyse de la parité salariale entre joueurs, équipes, et son impact sur le jeu ?**

---

## 2. Mapping : Questions <-> Sources de données

| Question | Sources principales | Formats possibles | Fréquence de mise à jour |
|----------|--------------------|-------------------|-------------------------|
| 1. Progression joueurs | NBA Stats API, Basketball Reference, Kaggle | API (JSON), CSV | Saison/Année |
| 2. Facteurs de victoire | NBA Stats API, ESPN, Kaggle | API (JSON), CSV | Match/Jour |
| 3. Blessures | Basketball Reference, ESPN, SportsRadar | CSV, API (JSON/XML) | Match/Semaine |
| 4. Matchs spectaculaires | NBA Stats API, Kaggle | API (JSON), CSV | Match/Jour |
| 6. Joueurs décisifs | NBA Stats API, Basketball Reference | API (JSON), CSV | Match/Jour |
| 8. Statistique rookies | NBA Stats API, Kaggle | API (JSON), CSV | Saison/Année |
| 9. Géographie des matchs | NBA Stats API, Basketball Reference | API (JSON), CSV | Match/Jour |
| 10. Affluence salles | NBA Stats API, Data.world | CSV, API (JSON) | Saison/Année |
| 12. Records | NBA Stats API, Basketball Reference | API (JSON), CSV | Saison/Année |
| 13. Stats avancées & palmarès | Basketball Reference, Kaggle | CSV, API (JSON) | Saison/Année |
| 14. Salaires | Hoopshype, Basketball Reference, Kaggle | CSV, API (JSON) | Saison/Année |

---

## 3. Exemples de sources de données

- **NBA Stats API** : [stats.nba.com](https://stats.nba.com/)
- **Kaggle Datasets NBA** : [kaggle.com/datasets?search=nba](https://www.kaggle.com/datasets?search=nba)
- **ESPN NBA** : [espn.com/nba](https://www.espn.com/nba/)
- **Hoopshype Salaries** : [hoopshype.com/salaries](https://hoopshype.com/salaries/)
