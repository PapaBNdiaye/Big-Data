# Guide d'Utilisation NBA DataLake

## Vue d'ensemble

Ce guide détaille l'utilisation complète du projet NBA DataLake, de l'installation à la configuration avancée, en passant par les opérations quotidiennes.

## Table des matières

1. [Installation et configuration](#-installation-et-configuration)
2. [Premiers pas](#-premiers-pas)
3. [Interface utilisateur](#-interface-utilisateur)
4. [Collecte de données](#-collecte-de-données)
5. [Configuration avancée](#-configuration-avancée)
6. [Gestion des données](#-gestion-des-données)
7. [Dépannage](#-dépannage)
8. [Bonnes pratiques](#-bonnes-pratiques)

## Installation et configuration

### **Prérequis système**
- **OS** : Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python** : Version 3.8 ou supérieure
- **RAM** : Minimum 4 GB, recommandé 8 GB
- **Espace disque** : Minimum 2 GB pour les données
- **Connexion internet** : Stable pour l'API NBA

### **Installation étape par étape**

#### **1. Cloner le repository**
```bash
git clone <repository-url>
cd tp_group
```

#### **2. Créer l'environnement virtuel**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

#### **3. Installer les dépendances**
```bash
pip install -r requirements.txt
```

### **Configuration initiale**

#### **Fichier config.py**
Le fichier `config.py` contient tous les paramètres configurables :

```python
NBA_API_CONFIG = {
    # Paramètres de base
    'max_players': 5,           # Limite de joueurs par session
    'start_year': 2000,         # Année de début des données
    'delay': 0.5,               # Délai entre requêtes API (secondes)
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
    }
}
```

#### **Variables d'environnement (optionnel)**
```bash
# Créer un fichier .env
NBA_API_TIMEOUT=30
NBA_API_RETRY_COUNT=3
LOG_LEVEL=INFO
```

## Premiers pas

### **Lancement de l'application**
```bash
# Activer l'environnement virtuel
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # macOS/Linux

# Lancer le menu principal
python src/main.py
```

### **Première collecte de données**
```bash
# Collecte complète (recommandé pour commencer)
python -c "
from src.ingestion.nba_data_collector import NBADataCollector
collector = NBADataCollector()
collector.run_full_collection()
"
```

### **Vérification de l'installation**
```bash
# Vérifier la structure des dossiers
ls data/
ls data/raw/api_nba/
ls data/metadata/

# Vérifier les métadonnées
cat data/metadata/index_donnees.json
```

## Interface utilisateur

### **Menu principal**
Le menu principal offre plusieurs options :

```
NBA DATALAKE - DÉMARRAGE
=====================================
1. Collecte complète des données NBA
2. Collecte sélective par type
3. Gestion des métadonnées
4. Configuration et paramètres
5. Quitter

Votre choix : 
```

### **Navigation dans le menu**

#### **Option 1 : Collecte complète**
- Collecte automatique de toutes les données
- Gestion des erreurs intégrée
- Métadonnées automatiquement mises à jour
- **Temps estimé** : 15-20 minutes

#### **Option 2 : Collecte sélective**
```
Sélectionnez le type de données :
1. Données statiques (joueurs, équipes)
2. Leaders actuels
3. Statistiques traditionnelles
4. Statistiques clutch
5. Statistiques par saison équipes
6. Retour au menu principal
```

#### **Option 3 : Gestion des métadonnées**
```
Gestion des métadonnées :
1. Mettre à jour les métadonnées
2. Consulter l'index des données
3. Nettoyer les métadonnées anciennes
4. Retour au menu principal
```

#### **Option 4 : Configuration**
```
Configuration :
1. Afficher la configuration actuelle
2. Modifier les paramètres
3. Tester la configuration
4. Retour au menu principal
```

## Collecte de données

### **Types de données disponibles**

#### **1. Données statiques**
- **Joueurs** : Informations de base (nom, équipe, position)
- **Équipes** : Informations des équipes (nom, ville, année de création)
- **Taille** : ~200 KB par session
- **Fréquence** : Mise à jour à la demande

#### **2. Leaders actuels**
- **Catégories** : Points, rebonds, passes, etc.
- **Saison** : Configurable via `leaders_season`
- **Taille** : ~1 MB par session
- **Fréquence** : Mise à jour à la demande

#### **3. Statistiques traditionnelles**
- **Joueurs** : Stats complètes par saison (2000-2025)
- **Équipes** : Stats complètes par saison (2000-2025)
- **Taille** : ~9 MB par session
- **Fréquence** : Mise à jour à la demande

#### **4. Statistiques clutch**
- **Joueurs** : Performance en situation critique
- **Période** : 2000-2025
- **Taille** : ~7.5 MB par session
- **Fréquence** : Mise à jour à la demande

### **Collecte sélective par type**

#### **Collecte des leaders uniquement**
```python
from src.ingestion.nba_data_collector import NBADataCollector

collector = NBADataCollector()
leaders = collector.collect_current_leaders()
print(f"Leaders collectés : {len(leaders)} catégories")
```

#### **Collecte des stats traditionnelles**
```python
# Collecte pour une saison spécifique
stats_2020 = collector.collect_player_traditional_stats(season=2020)

# Collecte pour toutes les saisons
all_stats = collector.collect_player_traditional_stats()
```

#### **Collecte des stats clutch**
```python
# Collecte avec paramètres personnalisés
clutch_stats = collector.collect_player_clutch_stats(
    clutch_time='Last 5 Minutes',
    ahead_behind='Ahead or Behind'
)
```

### **Monitoring de la collecte**

#### **Logs en temps réel**
```bash
# Suivre les logs pendant la collecte
tail -f data/ingestion.log
```

#### **Métadonnées de session**
```python
from src.ingestion.metadata_manager import MetadataManager

manager = MetadataManager()
session_metadata = manager.get_session_metadata('20250829_010804')
print(f"Session : {session_metadata['session_id']}")
print(f"Temps total : {session_metadata['performance']['total_time']}")
```

## Configuration avancée

### **Paramètres de performance**

#### **Optimisation de la vitesse**
```python
NBA_API_CONFIG = {
    'delay': 0.1,               # Réduire le délai (attention aux timeouts)
    'max_players': 10,          # Augmenter le nombre de joueurs
    'timeout': 15,              # Réduire le timeout
}
```

#### **Optimisation de la stabilité**
```python
NBA_API_CONFIG = {
    'delay': 1.0,               # Augmenter le délai
    'max_players': 3,           # Réduire le nombre de joueurs
    'timeout': 60,              # Augmenter le timeout
    'retry_count': 5,           # Plus de tentatives
}
```

### **Paramètres de collecte**

#### **Limitation des saisons**
```python
# Collecter seulement les 5 dernières saisons
'seasons': list(range(2020, 2026)),

# Collecter des saisons spécifiques
'seasons': [2000, 2005, 2010, 2015, 2020, 2025],
```

#### **Paramètres des statistiques avancées**
```python
'advanced_stats': {
    'player_traditional': {
        'measure_type': 'Advanced',  # Base, Advanced, Four Factors
        'per_mode': 'PerGame',       # Totals, PerGame, PerMinute
        'season_type': 'Playoffs'    # Regular Season, Playoffs, All Star
    }
}
```

### **Configuration des métadonnées**
```python
METADATA_CONFIG = {
    'retention_days': 30,        # Conserver les métadonnées 30 jours
    'log_level': 'INFO',         # Niveau de log (DEBUG, INFO, WARNING, ERROR)
    'auto_cleanup': True,        # Nettoyage automatique
    'backup_enabled': True       # Sauvegarde automatique
}
```

## Gestion des données

### **Organisation des fichiers**

#### **Structure des dossiers**
```
data/
├── raw/                    # Données brutes
│   ├── api_nba/           # Données NBA API
│   │   ├── players_static_[session].csv
│   │   ├── leaders_ALL_[session].csv
│   │   └── player_traditional_stats_[session].csv
│   └── kaggle/            # Dataset Kaggle (futur)
├── processed/              # Données traitées
└── metadata/               # Métadonnées et index
    ├── session_[timestamp].json
    ├── index_donnees.json
    └── metadata_globale.json
```

#### **Convention de nommage**
- **Format** : `[type]_[session].csv`
- **Session** : Timestamp au format `YYYYMMDD_HHMMSS`
- **Exemple** : `players_static_20250829_010804.csv`

### **Accès aux données**

#### **Lecture des données**
```python
import pandas as pd

# Lire les données des joueurs
players_df = pd.read_csv('data/raw/api_nba/players_static_20250829_010804.csv')

# Lire les stats traditionnelles
stats_df = pd.read_csv('data/raw/api_nba/player_traditional_stats_20250829_010804.csv')

# Filtrer par saison
stats_2020 = stats_df[stats_df['SEASON'] == 2020]
```

#### **Requêtes avancées**
```python
# Top 10 des marqueurs de la saison 2020
top_scorers = stats_df[
    (stats_df['SEASON'] == 2020) & 
    (stats_df['GP'] >= 50)
].nlargest(10, 'PTS')[['PLAYER_NAME', 'TEAM', 'PTS', 'GP']]

# Moyenne des points par équipe
team_avg = stats_df.groupby(['SEASON', 'TEAM'])['PTS'].mean().reset_index()
```

### **Maintenance des données**

#### **Nettoyage automatique**
```python
from src.ingestion.metadata_manager import MetadataManager

manager = MetadataManager()
# Nettoyer les métadonnées anciennes
manager.cleanup_old_metadata(days=30)

# Nettoyer les données anciennes
manager.cleanup_old_data(days=90)
```

#### **Sauvegarde des données**
```bash
# Créer une sauvegarde
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# Restaurer une sauvegarde
tar -xzf backup_20250829.tar.gz
```

## Dépannage

### **Problèmes courants**

#### **1. Erreurs de timeout**
```
HTTPSConnectionPool: Read timed out
```

**Solutions** :
- Augmenter le délai dans `config.py` : `'delay': 1.0`
- Augmenter le timeout : `'timeout': 60`
- Vérifier la connexion internet
- Collecter pendant les heures creuses

#### **2. Erreurs de rate limiting**
```
Too Many Requests
```

**Solutions** :
- Augmenter le délai : `'delay': 2.0`
- Réduire le nombre de joueurs : `'max_players': 3`
- Pauser entre les sessions de collecte

#### **3. Erreurs de validation des données**
```
ValidationError: Missing required columns
```

**Solutions** :
- Vérifier la connectivité API
- Relancer la collecte
- Consulter les logs pour plus de détails

#### **4. Problèmes de mémoire**
```
MemoryError: Unable to allocate array
```

**Solutions** :
- Réduire `max_players` dans la configuration
- Collecter par petits lots
- Augmenter la RAM disponible

### **Diagnostic et logs**

#### **Vérification des logs**
```bash
# Consulter les logs récents
tail -n 100 data/ingestion.log

# Rechercher les erreurs
grep "ERROR" data/ingestion.log

# Rechercher les timeouts
grep "timeout" data/ingestion.log
```

#### **Vérification de la configuration**
```python
# Tester la configuration
python -c "
from src.ingestion.nba_data_collector import NBADataCollector
try:
    collector = NBADataCollector()
    print('✅ Configuration valide')
    print(f'Start year: {collector.config[\"start_year\"]}')
    print(f'Delay: {collector.config[\"delay\"]}')
except Exception as e:
    print(f'❌ Erreur de configuration: {e}')
"
```

#### **Test de connectivité API**
```python
# Tester la connectivité NBA API
python -c "
import requests
try:
    response = requests.get('https://stats.nba.com/stats/leaguedashplayerstats', timeout=10)
    print(f'✅ API accessible: {response.status_code}')
except Exception as e:
    print(f'❌ API inaccessible: {e}')
"
```

## Bonnes pratiques

### **Collecte de données**

#### **Optimisation des performances**
- **Collecter pendant les heures creuses** (nuit US)
- **Utiliser des délais appropriés** (0.5-1.0 seconde)
- **Limiter le nombre de joueurs** par session (3-10)
- **Surveiller les logs** pour détecter les patterns d'erreur

#### **Gestion de l'espace disque**
- **Surveiller l'espace** disponible
- **Nettoyer régulièrement** les anciennes sessions
- **Compresser** les données historiques si nécessaire
- **Sauvegarder** les données importantes

### **Configuration**

#### **Paramètres recommandés**
```python
# Configuration équilibrée (performance + stabilité)
NBA_API_CONFIG = {
    'max_players': 5,           # Bon équilibre
    'start_year': 2000,         # Couverture complète
    'delay': 0.5,               # Délai optimal
    'timeout': 30,              # Timeout raisonnable
    'retry_count': 3            # Tentatives de retry
}

# Configuration pour la stabilité
NBA_API_CONFIG = {
    'max_players': 3,           # Plus stable
    'delay': 1.0,               # Plus lent mais stable
    'timeout': 60,              # Plus de patience
    'retry_count': 5            # Plus de tentatives
}
```

#### **Maintenance de la configuration**
- **Documenter** les changements de configuration
- **Tester** les modifications sur de petits volumes
- **Sauvegarder** les configurations qui fonctionnent
- **Versionner** les changements importants

### **Monitoring et maintenance**

#### **Surveillance continue**
- **Vérifier les logs** quotidiennement
- **Surveiller l'espace disque** régulièrement
- **Tester la connectivité API** avant les collectes importantes
- **Valider la qualité** des données collectées

#### **Maintenance préventive**
- **Nettoyer les logs** anciens
- **Vérifier la cohérence** des métadonnées
- **Tester les fonctionnalités** régulièrement
- **Mettre à jour** la documentation

---

**Support** : En cas de problème, consultez les logs dans `data/ingestion.log` et les métadonnées dans `data/metadata/`.
