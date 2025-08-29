# Organisation des Données - NBA DataLake

## Structure des dossiers

```
data/
├── raw/                    # Données brutes
│   ├── api_nba/           # Données collectées via l'API NBA
│   │   ├── player_career_stats/
│   │   ├── team_year_by_year_stats/
│   │   ├── league_leaders/
│   │   ├── player_traditional_stats/
│   │   ├── player_clutch_stats/
│   │   └── team_traditional_stats/
│   └── kaggle/            # Dataset basketball Kaggle
│       ├── *.csv          # Fichiers CSV du dataset
│       └── metadata/      # Métadonnées spécifiques Kaggle
├── processed/              # Données traitées et transformées
│   ├── fusion/            # Données fusionnées API + Kaggle
│   └── analytics/         # Données d'analyse
└── metadata/               # Métadonnées globales et index
    ├── metadata_globale.json
    ├── index_donnees.json
    └── sessions/           # Métadonnées par session
```

## Sources de données

### API NBA (data/raw/api_nba/)
- **Collecteur** : `nba_data_collector.py`
- **Période** : 2000-2025 (26 saisons)
- **Types** : Statistiques joueurs, équipes, leaders, traditionnelles, clutch
- **Format** : CSV avec métadonnées enrichies
- **Volume** : ~18.2 MB par session complète

### Dataset Kaggle (data/raw/kaggle/)
- **Intégrateur** : `kaggle_integrator.py`
- **Source** : wyattowalsh/basketball
- **Contenu** : Données historiques NBA
- **Format** : CSV natif
- **Intégration** : Automatique via kagglehub

## Gestion des métadonnées

### Métadonnées globales
- **Fichier** : `data/metadata/metadata_globale.json`
- **Contenu** : Configuration, paramètres, statistiques globales
- **Mise à jour** : Automatique après chaque session

### Index des données
- **Fichier** : `data/metadata/index_donnees.json`
- **Contenu** : Inventaire complet des fichiers et leurs métadonnées
- **Mise à jour** : Automatique après chaque collecte

### Métadonnées de session
- **Dossier** : `data/metadata/sessions/`
- **Format** : `{type}_session_{timestamp}.json`
- **Contenu** : Détails de chaque session de collecte

## Flux de données

1. **Collecte API NBA** → `data/raw/api_nba/`
2. **Intégration Kaggle** → `data/raw/kaggle/`
3. **Génération métadonnées** → `data/metadata/`
4. **Traitement** → `data/processed/`
5. **Validation** → Logs et rapports

## Qualité des données

### Validation automatique
- **Complétude** : Vérification des valeurs manquantes
- **Cohérence** : Validation des types de données
- **Intégrité** : Vérification des relations entre fichiers

### Enrichissement
- **Noms des joueurs** : Complétion automatique des PLAYER_NAME
- **Métadonnées** : Ajout de timestamps et sources
- **Index** : Création automatique des index de recherche

## Maintenance

### Nettoyage automatique
- **Logs** : Rotation automatique des fichiers de log
- **Métadonnées** : Archivage des anciennes sessions
- **Données temporaires** : Suppression automatique

### Sauvegarde
- **Structure** : Préservation de l'organisation des dossiers
- **Métadonnées** : Sauvegarde des index et configurations
- **Données** : Protection contre la corruption

## Utilisation

### Accès aux données
```python
# Données API NBA
api_data_path = "data/raw/api_nba/"

# Données Kaggle
kaggle_data_path = "data/raw/kaggle/"

# Métadonnées
metadata_path = "data/metadata/"
```

### Consultation des métadonnées
```python
import json

# Métadonnées globales
with open("data/metadata/metadata_globale.json", "r") as f:
    global_metadata = json.load(f)

# Index des données
with open("data/metadata/index_donnees.json", "r") as f:
    data_index = json.load(f)
```

## Bonnes pratiques

1. **Ne jamais modifier manuellement** la structure des dossiers
2. **Utiliser les outils** de collecte et d'intégration
3. **Consulter les métadonnées** avant d'accéder aux données
4. **Respecter la séparation** raw/processed/metadata
5. **Valider la qualité** des données avant traitement

---

**Dernière mise à jour** : Intégration Kaggle fonctionnelle
**Statut** : Production ready
