# Architecture NBA DataLake

## Vue d'ensemble

Ce document détaille l'architecture technique du projet NBA DataLake, expliquant les choix de conception, l'organisation des composants et les flux de données.

## Principes d'architecture

### **Architecture DataLake en 3 couches**
1. **Ingestion** : Collecte et validation des données
2. **Persistence** : Stockage et organisation des données
3. **Insight** : Analyse et visualisation des données

### **Principes de conception**
- **Modularité** : Composants indépendants et réutilisables
- **Configuration dynamique** : Aucune valeur codée en dur
- **Traçabilité** : Métadonnées complètes pour toutes les opérations
- **Extensibilité** : Architecture prête pour l'évolution future
- **Robustesse** : Gestion des erreurs et validation automatique

## Architecture système

### **Diagramme d'ensemble**
```
┌─────────────────────────────────────────────────────────────┐
│                    NBA DataLake                             │
├─────────────────────────────────────────────────────────────┤
│  Interface Utilisateur                                  │
│  └── src/main.py (Menu principal)                         │
├─────────────────────────────────────────────────────────────┤
│  Couche Ingestion                                      │
│  ├── nba_data_collector.py (API NBA)                      │
│  ├── kaggle_integrator.py (Dataset Kaggle)                │
│  └── metadata_manager.py (Gestion métadonnées)            │
├─────────────────────────────────────────────────────────────┤
│  Couche Persistence                                    │
│  ├── data/raw/ (Données brutes)                           │
│  ├── data/processed/ (Données traitées)                   │
│  └── data/metadata/ (Métadonnées et index)                │
├─────────────────────────────────────────────────────────────┤
│  Couche Insight                                        │
│  ├── Dashboard Dash (Visualisations)                      │
│  ├── Analytics (Métriques et KPIs)                        │
│  └── Machine Learning (Modèles prédictifs)                │
└─────────────────────────────────────────────────────────────┘
```

## Composants techniques

### **1. Couche Ingestion**

#### **NBADataCollector** (`src/ingestion/nba_data_collector.py`)
**Responsabilité** : Collecte principale des données NBA via l'API officielle

**Architecture interne** :
```python
class NBADataCollector:
    def __init__(self):
        self.config = self._load_config()        # Configuration dynamique
        self.session_id = self._generate_session_id()  # Identifiant unique
        self.metadata_manager = MetadataManager()      # Gestion métadonnées
    
    def run_full_collection(self):
        # Orchestration de la collecte complète
        # Gestion des erreurs et validation
        # Mise à jour des métadonnées
```

**Méthodes principales** :
- `collect_players_static()` : Données statiques des joueurs
- `collect_teams_static()` : Données statiques des équipes
- `collect_current_leaders()` : Leaders actuels (toutes catégories)
- `collect_player_traditional_stats()` : Stats traditionnelles (2000-2025)
- `collect_player_clutch_stats()` : Stats en situation de clutch
- `collect_team_traditional_stats()` : Stats équipes par saison

#### **MetadataManager** (`src/ingestion/metadata_manager.py`)
**Responsabilité** : Gestion automatique des métadonnées et index

**Fonctionnalités** :
- Création automatique des métadonnées de session
- Index global des données collectées
- Consolidation des métadonnées
- Traçabilité complète des opérations

#### **KaggleIntegrator** (`src/ingestion/kaggle_integrator.py`)
**Responsabilité** : Intégration du dataset Kaggle basketball

**Fonctionnalités** :
- Téléchargement automatique via kagglehub
- Organisation selon l'architecture DataLake (data/raw/kaggle)
- Analyse de la structure des données
- Validation de la qualité
- Fusion avec les données API NBA

### **2. Couche Persistence**

#### **Structure des données**
```
data/
├── raw/                    # Données brutes non transformées
│   ├── api_nba/           # Données NBA API officielle
│   │   ├── players_static_[session].csv
│   │   ├── teams_static_[session].csv
│   │   ├── leaders_ALL_[session].csv
│   │   ├── player_traditional_stats_[session].csv
│   │   ├── player_clutch_stats_[session].csv
│   │   └── team_traditional_stats_[session].csv
│   └── kaggle/            # Dataset Kaggle basketball
│       ├── players.csv
│       ├── teams.csv
│       ├── games.csv
│       ├── games_details.csv
│       └── ranking.csv
├── processed/              # Données traitées et transformées
│   ├── merged_data/        # Données fusionnées (API + Kaggle)
│   ├── aggregated/         # Données agrégées et calculées
│   └── formatted/          # Données formatées pour le dashboard
└── metadata/               # Métadonnées et index
    ├── session_[timestamp].json  # Métadonnées de session
    ├── index_donnees.json        # Index global des données
    └── metadata_globale.json     # Métadonnées consolidées
```

#### **Gestion des métadonnées**
**Structure des métadonnées de session** :
```json
{
  "session_id": "20250829_010804",
  "timestamp": "2025-08-29T01:08:04",
  "config_used": {
    "max_players": 5,
    "start_year": 2000,
    "delay": 0.5
  },
  "data_collected": {
    "players_static": {
      "file_size": 202239,
      "records_count": 4500,
      "status": "success"
    },
    "player_traditional_stats": {
      "file_size": 8906993,
      "seasons_range": [2000, 2025],
      "status": "success"
    }
  },
  "performance": {
    "total_time": "00:15:30",
    "api_calls": 156,
    "errors_count": 2
  }
}
```

### **3. Couche Insight (En développement)**

#### **Dashboard Dash**
- Interface web interactive
- Visualisations en temps réel
- Filtres et sélections dynamiques
- Export des données

#### **Analytics**
- Métriques de performance
- Tendances historiques
- Comparaisons joueurs/équipes
- KPIs automatisés

#### **Machine Learning**
- Modèles prédictifs
- Découverte de patterns
- Classification automatique
- Recommandations

## Flux de données

### **1. Collecte des données**
```
API NBA → NBADataCollector → Validation → Sauvegarde → Métadonnées
   ↓
Dataset Kaggle → KaggleIntegrator → Validation → Sauvegarde → Métadonnées
```

### **2. Traitement des données**
```
Données brutes → Validation → Transformation → Agrégation → Données traitées
     ↓
Métadonnées → Index global → Dashboard → Analytics → Insights
```

### **3. Gestion des erreurs**
```
Requête API → Timeout/Erreur → Retry automatique → Log → Métadonnées
     ↓
Validation échoue → Notification → Log → Métadonnées → Rapport
```

## Configuration et paramètres

### **Structure de configuration**
```python
NBA_API_CONFIG = {
    # Paramètres de base
    'max_players': 5,           # Limite de joueurs par session
    'start_year': 2000,         # Année de début des données
    'delay': 0.5,               # Délai entre requêtes API
    'leaders_season': '2023-24', # Saison pour les leaders
    
    # Saisons à collecter
    'seasons': list(range(2000, 2026)),  # 2000-2025
    
    # Paramètres avancés
    'advanced_stats': {
        'player_traditional': {
            'measure_type': 'Base',
            'per_mode': 'Totals',
            'season_type': 'Regular Season'
        },
        'player_clutch': {
            'clutch_time': 'Last 5 Minutes',
            'ahead_behind': 'Ahead or Behind'
        }
    },
    
    # Limites de collecte
    'collection_limits': {
        'team_season_stats': 10,
        'player_clutch_stats': 5,
        'team_traditional_stats': 10
    }
}
```

### **Gestion de la configuration**
- **Chargement dynamique** : Lecture depuis `config.py`
- **Validation** : Vérification des paramètres
- **Héritage** : Valeurs par défaut pour les paramètres manquants
- **Flexibilité** : Modification sans redémarrage

## Performance et optimisation

### **Stratégies d'optimisation**
- **Collecte par lots** : Limitation du nombre de requêtes simultanées
- **Délais configurables** : Éviter la surcharge de l'API
- **Gestion de la mémoire** : Utilisation optimisée de pandas
- **Cache des données** : Éviter les requêtes répétées

### **Métriques de performance**
- **Temps de collecte** : ~15-20 minutes pour une session complète
- **Taux de succès** : >95% des requêtes API
- **Utilisation mémoire** : Optimisée avec pandas
- **Stockage** : ~18.2 MB par session de collecte

## Sécurité et robustesse

### **Gestion des erreurs**
- **Timeouts** : 30 secondes par requête
- **Retry automatique** : Gestion des erreurs temporaires
- **Validation** : Vérification de la qualité des données
- **Logging** : Traçabilité complète des erreurs

### **Limitations connues**
- **Rate limiting** : L'API NBA limite les requêtes
- **Serveurs surchargés** : Particulièrement pendant les heures de pointe
- **Timeouts** : Erreurs `HTTPSConnectionPool: Read timed out` communes

### **Stratégies de mitigation**
- **Délais configurables** : Pauses entre requêtes
- **Collecte par lots** : Limitation du volume
- **Monitoring** : Détection des patterns d'erreur
- **Fallbacks** : Stratégies alternatives en cas d'échec

## Évolution future

### **Phase 1 : Intégration Kaggle**
- Téléchargement automatique du dataset
- Fusion avec les données API NBA
- Validation croisée des sources

### **Phase 2 : Couche Persistence**
- Base de données relationnelle
- Optimisation du stockage
- Système de backup automatique

### **Phase 3 : Dashboard et Analytics**
- Interface Dash interactive
- Métriques avancées
- Modèles prédictifs

### **Phase 4 : API REST**
- Interface programmatique
- Intégration avec d'autres systèmes
- Documentation OpenAPI

## Standards et bonnes pratiques

### **Coding standards**
- **PEP 8** : Style de code Python
- **Documentation** : Docstrings en français
- **Tests** : Validation des fonctionnalités
- **Logging** : Traçabilité complète

### **Architecture patterns**
- **MVC** : Séparation des responsabilités
- **Factory** : Création des objets
- **Observer** : Gestion des événements
- **Strategy** : Algorithmes configurables

### **Gestion des versions**
- **Git** : Contrôle de version
- **Semantic versioning** : Numérotation des versions
- **Changelog** : Historique des modifications
- **Releases** : Versions stables

---

**Documentation technique** : Ce document est la référence principale pour comprendre l'architecture du projet NBA DataLake.
