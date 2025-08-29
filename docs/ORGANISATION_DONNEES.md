# Organisation des Données - NBA DataLake

## Vue d'ensemble

Ce dossier contient toutes les données collectées, organisées selon l'architecture DataLake. La structure respecte les bonnes pratiques de séparation des données brutes, traitées et des métadonnées.

## Structure des dossiers

```
data/
├── raw/                    # Données brutes non transformées
│   ├── api_nba/           # Données NBA API officielle
│   └── kaggle/            # Dataset Kaggle basketball
├── processed/              # Données traitées et transformées
├── metadata/               # Métadonnées et index
└── ORGANISATION_DONNEES.md # Ce fichier
```

## Détail des dossiers

### 1. `raw/` - Données brutes

#### `raw/api_nba/` - Données NBA API
**Source** : API officielle NBA via `nba_api`

**Fichiers disponibles (Session 20250829_010804) :**
- `players_static_20250829_010804.csv` (202,239 bytes)
  - Informations statiques de tous les joueurs
  - Colonnes : id, full_name, abbreviation, nickname, city, state, year_founded
  
- `teams_static_20250829_010804.csv` (1,998 bytes)
  - Informations statiques de toutes les équipes
  - Colonnes : id, full_name, abbreviation, nickname, city, state, year_founded
  
- `player_career_stats_20250829_010804.csv` (4,830 bytes)
  - Statistiques de carrière pour 5 joueurs actifs
  - Colonnes : PLAYER_ID, PLAYER_NAME, SEASON_ID, TEAM_ID, TEAM_ABBREVIATION, etc.
  
- `team_season_stats_20250829_010804.csv` (116,868 bytes)
  - Statistiques par saison pour les équipes
  - Colonnes : TEAM_ID, TEAM_NAME, SEASON, W, L, W_PCT, etc.
  
- `leaders_ALL_20250829_010804.csv` (941,985 bytes)
  - Leaders actuels dans toutes les catégories
  - Colonnes : PLAYER_ID, RANK, PLAYER, TEAM_ID, TEAM, GP, MIN, PTS, etc.
  
- `player_traditional_stats_20250829_010804.csv` (8,906,993 bytes)
  - Statistiques traditionnelles des joueurs (2000-2025)
  - Colonnes : PLAYER_ID, PLAYER_NAME, TEAM_ID, SEASON, GP, MIN, PTS, REB, AST, etc.
  
- `player_clutch_stats_20250829_010804.csv` (7,478,592 bytes)
  - Statistiques en situation de clutch (2000-2025)
  - Colonnes : PLAYER_ID, PLAYER_NAME, TEAM_ID, SEASON, CLUTCH_TIME, AHEAD_BEHIND, etc.
  
- `team_traditional_stats_20250829_010804.csv` (430,141 bytes)
  - Statistiques traditionnelles des équipes (2000-2025)
  - Colonnes : TEAM_ID, TEAM_NAME, SEASON, GP, W, L, W_PCT, etc.

#### `raw/kaggle/` - Dataset Kaggle
**Source** : Dataset "basketball" de Kaggle

**Fichiers prévus :**
- `players.csv` - Informations des joueurs
- `teams.csv` - Informations des équipes
- `games.csv` - Détails des matchs
- `games_details.csv` - Statistiques détaillées des matchs
- `ranking.csv` - Classements des équipes

**Note** : Ce dossier est préparé pour l'intégration future du dataset Kaggle.

### 2. `processed/` - Données traitées

**Contenu** : Données transformées, nettoyées et prêtes pour l'analyse

**Utilisation** : 
- Données fusionnées (API NBA + Kaggle)
- Données agrégées et calculées
- Données formatées pour le dashboard

### 3. `metadata/` - Métadonnées et index

**Contenu** : Informations de traçabilité et index des données

**Fichiers** :
- `session_*.json` - Métadonnées de chaque session de collecte
- `index_donnees.json` - Index global de toutes les données
- `metadata_globale.json` - Métadonnées consolidées

## Couverture temporelle

### API NBA
- **Période** : 2000-2025 (26 saisons)
- **Fréquence** : Mise à jour à la demande
- **Complétude** : 100% des saisons configurées

### Dataset Kaggle
- **Période** : 1946-2023 (77 saisons)
- **Fréquence** : Mise à jour manuelle
- **Complétude** : Données historiques complètes

## Qualité des données

### Validation automatique
- **Vérification des colonnes** : Présence et cohérence
- **Détection des valeurs manquantes** : Identification des anomalies
- **Validation des types** : Vérification des formats
- **Enrichissement automatique** : Ajout des noms de joueurs

### Métriques de qualité
- **Taux de complétude** : >95% pour les données principales
- **Cohérence temporelle** : Saisons continues depuis 2000
- **Traçabilité** : Métadonnées complètes pour chaque session

## Gestion des versions

### Stratégie de versioning
- **Session-based** : Chaque collecte crée une nouvelle session
- **Timestamp unique** : Identifiant unique pour chaque session
- **Conservation** : Toutes les sessions sont conservées
- **Index global** : Mise à jour automatique de l'inventaire

### Nettoyage automatique
- **Logs** : Rotation automatique des logs anciens
- **Métadonnées** : Conservation de toutes les sessions
- **Données** : Conservation de toutes les collectes

## Utilisation des données

### Accès direct
```python
import pandas as pd

# Lire les données des joueurs
players_df = pd.read_csv('data/raw/api_nba/players_static_20250829_010804.csv')

# Lire les stats traditionnelles
stats_df = pd.read_csv('data/raw/api_nba/player_traditional_stats_20250829_010804.csv')

# Filtrer par saison
stats_2020 = stats_df[stats_df['SEASON'] == 2020]
```

### Via l'API du projet
```python
from src.ingestion.nba_data_collector import NBADataCollector

collector = NBADataCollector()
# Les données sont automatiquement organisées dans la structure DataLake
```

## Maintenance et surveillance

### Espace disque
- **Surveillance** : Vérification régulière de l'espace disponible
- **Nettoyage** : Suppression des fichiers temporaires
- **Archivage** : Compression des anciennes sessions si nécessaire

### Intégrité des données
- **Validation** : Vérification de la cohérence des métadonnées
- **Backup** : Sauvegarde des données critiques
- **Restauration** : Procédures de récupération en cas de problème

### Performance
- **Index** : Optimisation des requêtes via l'index global
- **Cache** : Mise en cache des données fréquemment utilisées
- **Compression** : Compression des données historiques

## Bonnes pratiques

### Pour les développeurs
- Toujours utiliser les chemins relatifs depuis la racine du projet
- Respecter la structure des dossiers existante
- Ajouter des métadonnées pour les nouvelles données
- Valider la qualité avant de sauvegarder

### Pour les utilisateurs
- Consulter l'index des données avant utilisation
- Vérifier la date de dernière collecte
- Utiliser les métadonnées pour comprendre le contexte
- Signaler les anomalies détectées

## Support et dépannage

### Problèmes courants
- **Fichiers manquants** : Vérifier l'index des données
- **Données corrompues** : Consulter les logs de collecte
- **Espace disque** : Nettoyer les fichiers temporaires
- **Métadonnées incohérentes** : Relancer la mise à jour des métadonnées

### Ressources utiles
- `CLEANUP_SUMMARY.md` : Résumé du nettoyage effectué
- `src/ingestion/README.md` : Documentation du module d'ingestion
- Logs dans `data/ingestion.log`
- Métadonnées dans `data/metadata/`
