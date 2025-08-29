#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration centralisée pour le projet NBA DataLake
Tous les paramètres sont configurables ici
"""

# Configuration principale de l'API NBA
NBA_API_CONFIG = {
    # Paramètres de base
    'max_players': 5,           # Limite de joueurs par session
    'start_year': 2000,         # Année de début des données
    'delay': 0.5,               # Délai entre requêtes API (secondes)
    'leaders_season': '2023-24', # Saison pour les leaders
    
    # Saisons à collecter
    'seasons': list(range(2000, 2026)),  # 2000-2025
    
    # Catégories de leaders à collecter
    'leader_categories': [
        'PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT', 'FT_PCT'
    ],
    
    # Paramètres avancés
    'advanced_stats': {
        'player_traditional': {
            'enabled': True,
            'measure_type': 'Base',
            'per_mode': 'Totals',
            'season_type': 'Regular Season'
        },
        'player_clutch': {
            'enabled': True,
            'clutch_time': 'Last 5 Minutes',
            'ahead_behind': 'Ahead or Behind'
        },
        'team_traditional': {
            'enabled': True,
            'measure_type': 'Base',
            'per_mode': 'Totals',
            'season_type': 'Regular Season'
        }
    },
    
    # Limites de collecte
    'collection_limits': {
        'team_season_stats': 10,
        'player_clutch_stats': 5,
        'team_traditional_stats': 10
    },
    
    # Paramètres de performance
    'timeout': 30,              # Timeout en secondes
    'retry_count': 3,           # Nombre de tentatives
    'batch_size': 100           # Taille des lots de traitement
}

# Configuration des chemins
PATHS_CONFIG = {
    'data_dir': 'data',
    'raw_dir': 'data/raw',
    'processed_dir': 'data/processed',
    'metadata_dir': 'data/metadata',
    'logs_dir': 'data/logs'
}

# Configuration du logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'data/ingestion.log'
}

# Configuration Kaggle
KAGGLE_CONFIG = {
    'dataset': 'wyattowalsh/basketball',
    'force_download': False,
    'auto_extract': True
}

# Configuration de la base de données (pour la phase future)
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'nba_datalake',
    'username': 'postgres',
    'password': 'password'
}
