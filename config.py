#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration simple du projet NBA DataLake
"""

from pathlib import Path
from datetime import datetime

# Chemins du projet
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"

# Dossiers de données
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Configuration API NBA
NBA_API_CONFIG = {
    "timeout": 30,
    "delay": 0.3,
    "max_players": 500,  # Augmenté de 300 à 500
    "start_year": 2000,  # Depuis l'année 2000 (plus fiable et complet)
    "current_year": datetime.now().year,
    "seasons": list(range(2000, datetime.now().year + 1)),  # 2000 à aujourd'hui
    "collect_all_players": True,  # Collecter tous les joueurs (pas que actifs)
    "collect_all_seasons": True,  # Collecter toutes les saisons disponibles
    "leader_categories": [
        "PTS", "REB", "AST", "STL", "BLK", "FG_PCT", "FG3_PCT", 
        "FT_PCT", "MIN", "GP", "EFF", "AST_TOV", "STL_TOV"
    ],
    "season_types": ["Regular Season", "Playoffs", "All Star"],  # Types de saison
    "batch_size": 50,  # Traitement par lots de 50 joueurs
    "retry_attempts": 3,  # Nombre de tentatives en cas d'erreur
    "max_concurrent": 1  # Pas de concurrence pour éviter les timeouts
}

# Configuration Kaggle
KAGGLE_CONFIG = {
    "dataset": "wyattowalsh/basketball"
}

def create_directories():
    """Crée les dossiers nécessaires"""
    for directory in [DATA_DIR, RAW_DIR, PROCESSED_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Dossier créé : {directory}")

if __name__ == "__main__":
    print("Configuration NBA DataLake")
    print(f"Période de collecte : {NBA_API_CONFIG['start_year']} - {NBA_API_CONFIG['current_year']}")
    print(f"Nombre de saisons : {len(NBA_API_CONFIG['seasons'])}")
    create_directories()
