# Module d'Ingestion - NBA DataLake

## Vue d'ensemble

Ce module gère l'ingestion de toutes les données NBA depuis l'API officielle et le dataset Kaggle. Il implémente une architecture modulaire avec gestion automatique des métadonnées et de la traçabilité.

## Composants

### 1. NBADataCollector (`nba_data_collector.py`)

**Responsabilité** : Collecte principale des données NBA via l'API officielle

**Fonctionnalités** :
- Collecte des données statiques (joueurs, équipes)
- Collecte des statistiques de carrière
- Collecte des leaders actuels
- Collecte des statistiques avancées (traditionnelles, clutch)
- Gestion automatique des erreurs et timeouts
- Configuration dynamique via `config.py`

**Méthodes principales** :
```python
collector = NBADataCollector()
collector.run_full_collection()  # Collecte complète
collector.collect_players_static()  # Données statiques
collector.collect_current_leaders()  # Leaders actuels
```

**Configuration** :
- `max_players` : Limite de joueurs par session
- `start_year` : Année de début (2000)
- `delay` : Délai entre requêtes API
- `leaders_season` : Saison pour les leaders

### 2. MetadataManager (`metadata_manager.py`)

**Responsabilité** : Gestion automatique des métadonnées et index

**Fonctionnalités** :
- Création automatique des métadonnées de session
- Index global des données collectées
- Consolidation des métadonnées
- Traçabilité complète des opérations

**Utilisation** :
```python
from metadata_manager import MetadataManager
manager = MetadataManager()
manager.update_all_metadata()  # Mise à jour complète
```

### 3. KaggleIntegrator (`kaggle_integrator.py`)

**Responsabilité** : Intégration du dataset Kaggle NBA

**Fonctionnalités** :
- Téléchargement automatique via Kaggle CLI
- Organisation selon l'architecture DataLake
- Analyse de la structure des données
- Validation de la qualité
- Planification de la fusion avec l'API

**Utilisation** :
```python
from kaggle_integrator import KaggleIntegrator
integrator = KaggleIntegrator()
integrator.run_full_integration()  # Intégration complète
```

## Architecture des données

### Structure des dossiers
```
data/
├── raw/
│   ├── api_nba/           # Données NBA API
│   └── kaggle/            # Dataset Kaggle
├── processed/              # Données traitées
└── metadata/              # Métadonnées et index
```

### Types de données collectées

#### API NBA
- **Données statiques** : Joueurs, équipes
- **Statistiques de carrière** : Performance par joueur
- **Leaders actuels** : Classements par catégorie
- **Stats traditionnelles** : Joueurs et équipes (2000-2025)
- **Stats clutch** : Performance en situation critique

#### Dataset Kaggle
- **Données historiques** : 1946-2023
- **Statistiques complètes** : Joueurs, équipes, matchs
- **Métadonnées** : Informations contextuelles

## Configuration

### Paramètres principaux (`config.py`)
```python
NBA_API_CONFIG = {
    'max_players': 5,           # Limite de joueurs
    'start_year': 2000,         # Année de début
    'delay': 0.5,               # Délai entre requêtes
    'leaders_season': '2023-24', # Saison des leaders
    'seasons': list(range(2000, 2026))  # Saisons à collecter
}
```

### Paramètres avancés
```python
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
}
```

## Gestion des erreurs

### Stratégies implémentées
- **Timeouts** : 30 secondes par requête
- **Retry automatique** : Gestion des erreurs temporaires
- **Délais** : Pauses entre requêtes pour éviter la surcharge
- **Logging** : Traçabilité complète des erreurs
- **Validation** : Vérification de la qualité des données

### Types d'erreurs gérées
- `HTTPSConnectionPool: Read timed out`
- `Rate limiting` de l'API
- Erreurs de validation des données
- Problèmes de réseau temporaires

## Utilisation

### Collecte complète
```bash
# Via le menu principal
python src/main.py

# Directement via Python
python -c "
from src.ingestion.nba_data_collector import NBADataCollector
collector = NBADataCollector()
collector.run_full_collection()
"
```

### Collecte sélective
```python
collector = NBADataCollector()

# Collecte des leaders uniquement
leaders = collector.collect_current_leaders()

# Collecte des stats traditionnelles
traditional = collector.collect_player_traditional_stats()

# Collecte des stats clutch
clutch = collector.collect_player_clutch_stats()
```

### Gestion des métadonnées
```python
from src.ingestion.metadata_manager import MetadataManager

manager = MetadataManager()
manager.update_all_metadata()  # Mise à jour complète
```

## Monitoring et logs

### Fichiers de log
- `data/ingestion.log` : Logs détaillés des opérations
- `data/metadata/session_*.json` : Métadonnées de session
- `data/index_donnees.json` : Index global des données

### Informations tracées
- Début et fin de chaque opération
- Nombre de données collectées
- Erreurs rencontrées
- Temps d'exécution
- Configuration utilisée

## Bonnes pratiques

### Collecte de données
- Respecter les délais entre requêtes
- Surveiller les logs pour détecter les patterns d'erreur
- Utiliser la collecte par lots pour les gros volumes
- Valider la qualité des données collectées

### Configuration
- Modifier uniquement `config.py` pour ajuster les paramètres
- Tester les modifications sur de petits volumes
- Documenter les changements de configuration
- Sauvegarder les configurations qui fonctionnent

### Maintenance
- Surveiller l'espace disque
- Nettoyer régulièrement les logs anciens
- Vérifier la cohérence des métadonnées
- Tester régulièrement la connectivité API

## Développement

### Ajout de nouvelles sources
1. Créer une nouvelle classe dans le module approprié
2. Implémenter les méthodes de collecte
3. Ajouter la gestion des métadonnées
4. Intégrer dans le menu principal
5. Tester et valider

### Extension des fonctionnalités
1. Identifier le composant à étendre
2. Maintenir la compatibilité avec l'existant
3. Ajouter la configuration nécessaire
4. Mettre à jour la documentation
5. Tester les nouvelles fonctionnalités

## Support et dépannage

### Problèmes courants
- **Timeouts API** : Augmenter le délai dans la configuration
- **Erreurs de réseau** : Vérifier la connectivité internet
- **Limitations de rate** : Réduire le nombre de requêtes simultanées
- **Problèmes de mémoire** : Limiter la taille des lots de données

### Ressources utiles
- Logs détaillés dans `data/ingestion.log`
- Métadonnées de session dans `data/metadata/`
- Configuration dans `config.py`
- Documentation de l'API NBA
