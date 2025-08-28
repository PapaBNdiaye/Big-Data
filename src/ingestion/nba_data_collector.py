#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collecteur de données NBA pour DataLake
Récupère et structure les données depuis l'API NBA officielle
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nba_api.stats.endpoints import (
    playercareerstats, teamyearbyyearstats, leagueleaders,
    playergamelog, teamgamelog, commonplayerinfo
)
from nba_api.stats.static import players, teams
from nba_api.live.nba.endpoints import scoreboard
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Optional, Tuple

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/ingestion.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NBADataCollector:
    """Collecteur principal de données NBA pour DataLake"""
    
    def __init__(self, output_dir: str = 'data'):
        # Import de la configuration
        import sys
        import os
        # Ajouter le répertoire racine au path pour trouver config.py
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
        
        from config import NBA_API_CONFIG
        self.config = NBA_API_CONFIG
        self.output_dir = output_dir
        self.metadata = {
            'session_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'start_time': datetime.now().isoformat(),
            'api_version': 'nba_api 1.10.0',
            'collected_data': {},
            'errors': []
        }
        
        # Création du dossier de sortie avec séparation par source
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f'{output_dir}/raw/api_nba', exist_ok=True)  # Données NBA API
        os.makedirs(f'{output_dir}/raw/kaggle', exist_ok=True)   # Données Kaggle
        os.makedirs(f'{output_dir}/processed', exist_ok=True)
        os.makedirs(f'{output_dir}/metadata', exist_ok=True)
        
        logger.info(f"Collecteur NBA initialisé - Session: {self.metadata['session_id']}")
    
    def collect_players_static(self) -> pd.DataFrame:
        """Collecte des informations statiques sur tous les joueurs"""
        logger.info("Collecte des informations statiques des joueurs...")
        
        try:
            all_players = players.get_players()
            players_df = pd.DataFrame(all_players)
            
            # Sauvegarde des données brutes
            raw_path = f'{self.output_dir}/raw/api_nba/players_static_{self.metadata["session_id"]}.csv'
            players_df.to_csv(raw_path, index=False)
            
            # Ajout aux métadonnées
            self.metadata['collected_data']['players_static'] = {
                'count': len(players_df),
                'raw_file': raw_path,
                'columns': list(players_df.columns)
            }
            
            logger.info(f"✅ {len(players_df)} joueurs collectés et sauvegardés")
            return players_df
            
        except Exception as e:
            error_msg = f"Erreur collecte joueurs statiques: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return pd.DataFrame()
    
    def collect_teams_static(self) -> pd.DataFrame:
        """Collecte des informations statiques sur toutes les équipes"""
        logger.info("Collecte des informations statiques des équipes...")
        
        try:
            all_teams = teams.get_teams()
            teams_df = pd.DataFrame(all_teams)
            
            # Sauvegarde des données brutes
            raw_path = f'{self.output_dir}/raw/api_nba/teams_static_{self.metadata["session_id"]}.csv'
            teams_df.to_csv(raw_path, index=False)
            
            # Ajout aux métadonnées
            self.metadata['collected_data']['teams_static'] = {
                'count': len(teams_df),
                'raw_file': raw_path,
                'columns': list(teams_df.columns)
            }
            
            logger.info(f"✅ {len(teams_df)} équipes collectées et sauvegardées")
            return teams_df
            
        except Exception as e:
            error_msg = f"Erreur collecte équipes statiques: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return pd.DataFrame()
    
    def collect_player_career_stats(self, player_ids: List[str] = None, limit: int = None) -> Dict[str, pd.DataFrame]:
        """Collecte des statistiques de carrière pour les joueurs actifs (limite configurable)"""
        
        # Utiliser la configuration pour la limite
        max_players = limit if limit is not None else self.config['max_players']
        
        logger.info(f"Collecte des statistiques de carrière pour les {max_players} premiers joueurs actifs...")
        
        if player_ids is None:
            # Collecte des joueurs actifs selon la limite configurée
            all_players = players.get_active_players()
            player_ids = [player['id'] for player in all_players[:max_players]]
            logger.info(f"Collecte des stats de carrière pour {len(player_ids)} joueurs actifs (limite: {max_players})")
        elif limit:
            player_ids = player_ids[:limit]
        
        career_stats = {}
        total_processed = 0
        
        for i, player_id in enumerate(player_ids):
            try:
                if i % 10 == 0:  # Log tous les 10 joueurs
                    logger.info(f"Collecte joueur {i+1}/{len(player_ids)} - ID: {player_id}")
                
                # Récupération des stats de carrière
                stats = playercareerstats.PlayerCareerStats(player_id=player_id)
                stats_df = stats.get_data_frames()[0]
                
                if not stats_df.empty:
                    # Récupération des infos du joueur
                    player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
                    info_df = player_info.get_data_frames()[0]
                    
                    if not info_df.empty:
                        player_name = info_df.iloc[0]['DISPLAY_FIRST_LAST']
                        career_stats[player_name] = stats_df
                        total_processed += 1
                        
                        logger.info(f"✅ {player_name}: {len(stats_df)} saisons collectées")
                
                # Pause pour éviter la surcharge de l'API
                time.sleep(self.config['delay'])
                
            except Exception as e:
                error_msg = f"Erreur collecte stats joueur {player_id}: {e}"
                logger.error(error_msg)
                self.metadata['errors'].append(error_msg)
                continue
        
        # Sauvegarde de TOUTES les stats de carrière dans un seul fichier
        if career_stats:
            all_career_stats = pd.concat(career_stats.values(), ignore_index=True)
            raw_path = f'{self.output_dir}/raw/api_nba/career_stats_ALL_{self.metadata["session_id"]}.csv'
            all_career_stats.to_csv(raw_path, index=False)
            logger.info(f"✅ Toutes les stats de carrière sauvegardées: {raw_path}")
        
        # Ajout aux métadonnées
        self.metadata['collected_data']['player_career_stats'] = {
            'players_processed': total_processed,
            'total_seasons': sum(len(df) for df in career_stats.values()),
            'total_file': raw_path if career_stats else None
        }
        
        return career_stats
    
    def collect_team_season_stats(self, team_ids: List[str] = None, seasons: List[str] = None) -> Dict[str, pd.DataFrame]:
        """Collecte des statistiques saisonnières pour TOUTES les équipes"""
        logger.info("Collecte des statistiques saisonnières pour TOUTES les équipes...")
        
        if team_ids is None:
            # Collecte de TOUTES les équipes actuelles
            all_teams = teams.get_teams()
            team_ids = [team['id'] for team in all_teams]
            logger.info(f"Collecte des stats pour {len(team_ids)} équipes")
        
        if seasons is None:
            # Utiliser la configuration pour les saisons
            start_year = self.config['start_year']
            current_year = self.config['current_year']
            seasons = [f"{year}-{str(year+1)[-2:]}" for year in range(start_year, current_year+1)]
        
        team_stats = {}
        total_processed = 0
        
        for team_id in team_ids:
            try:
                logger.info(f"Collecte équipe ID: {team_id}")
                
                # Récupération des stats par saison
                stats = teamyearbyyearstats.TeamYearByYearStats(team_id=team_id)
                stats_df = stats.get_data_frames()[0]
                
                # Filtrage par saisons demandées
                if seasons:
                    stats_df = stats_df[stats_df['YEAR'].isin(seasons)]
                
                if not stats_df.empty:
                    team_stats[team_id] = stats_df
                    
                    # Sauvegarde des données brutes
                    raw_path = f'{self.output_dir}/raw/api_nba/team_stats_{team_id}_{self.metadata["session_id"]}.csv'
                    stats_df.to_csv(raw_path, index=False)
                    
                    logger.info(f"✅ Équipe {team_id}: {len(stats_df)} saisons collectées")
                
                time.sleep(self.config['delay'])
                
            except Exception as e:
                error_msg = f"Erreur collecte stats équipe {team_id}: {e}"
                logger.error(error_msg)
                self.metadata['errors'].append(error_msg)
                continue
        
        # Sauvegarde de TOUTES les stats d'équipes dans un seul fichier
        if team_stats:
            all_team_stats = pd.concat(team_stats.values(), ignore_index=True)
            raw_path = f'{self.output_dir}/raw/api_nba/team_stats_ALL_{self.metadata["session_id"]}.csv'
            all_team_stats.to_csv(raw_path, index=False)
            logger.info(f"✅ Toutes les stats d'équipes sauvegardées: {raw_path}")
        
        # Ajout aux métadonnées
        self.metadata['collected_data']['team_season_stats'] = {
            'teams_processed': len(team_stats),
            'total_seasons': sum(len(df) for df in team_stats.values()),
            'total_file': raw_path if team_stats else None
        }
        
        return team_stats
    
    def collect_current_leaders(self) -> Dict[str, pd.DataFrame]:
        """Collecte des leaders actuels de la NBA pour TOUTES les catégories"""
        logger.info("Collecte des leaders actuels pour TOUTES les catégories...")
        
        leaders_data = {}
        # TOUTES les catégories de leaders disponibles
        stat_categories = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'MIN', 'GP', 'EFF', 'AST_TOV', 'STL_TOV']
        
        for category in stat_categories:
            try:
                logger.info(f"Collecte leaders: {category}")
                
                current_year = datetime.now().year
                current_season = f"{current_year-1}-{str(current_year)[-2:]}"
                
                leaders = leagueleaders.LeagueLeaders(
                    stat_category_abbreviation=category,
                    season=current_season,
                    season_type_all_star='Regular Season'
                )
                
                leaders_df = leaders.get_data_frames()[0]
                leaders_data[category] = leaders_df
                
                # Sauvegarde des données brutes
                raw_path = f'{self.output_dir}/raw/api_nba/leaders_{category}_{self.metadata["session_id"]}.csv'
                leaders_df.to_csv(raw_path, index=False)
                
                logger.info(f"✅ Leaders {category}: {len(leaders_df)} joueurs collectés")
                
                time.sleep(self.config['delay'])  # Pause configurable
                
            except Exception as e:
                error_msg = f"Erreur collecte leaders {category}: {e}"
                logger.error(error_msg)
                self.metadata['errors'].append(error_msg)
                continue
        
        # Sauvegarde de TOUS les leaders dans un seul fichier
        if leaders_data:
            all_leaders = pd.concat(leaders_data.values(), ignore_index=True)
            raw_path = f'{self.output_dir}/raw/api_nba/leaders_ALL_{self.metadata["session_id"]}.csv'
            all_leaders.to_csv(raw_path, index=False)
            logger.info(f"✅ Tous les leaders sauvegardés: {raw_path}")
        
        # Ajout aux métadonnées
        self.metadata['collected_data']['current_leaders'] = {
            'categories_processed': len(leaders_data),
            'total_players': sum(len(df) for df in leaders_data.values()),
            'total_file': raw_path if leaders_data else None
        }
        
        return leaders_data
    
    def save_metadata(self):
        """Sauvegarde des métadonnées de la session"""
        self.metadata['end_time'] = datetime.now().isoformat()
        self.metadata['duration'] = (
            datetime.fromisoformat(self.metadata['end_time']) - 
            datetime.fromisoformat(self.metadata['start_time'])
        ).total_seconds()
        
        metadata_path = f'{self.output_dir}/metadata/session_{self.metadata["session_id"]}.json'
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Métadonnées sauvegardées: {metadata_path}")
        
        return metadata_path
    
    def run_full_collection(self) -> Dict:
        """Exécute la collecte complète des données NBA (limite configurable)"""
        max_players = self.config['max_players']
        logger.info(f"🚀 Démarrage de la collecte complète des données NBA (limite: {max_players} joueurs actifs)")
        
        try:
            # Collecte des données statiques
            players_static = self.collect_players_static()
            teams_static = self.collect_teams_static()
            
            # Collecte des statistiques détaillées
            player_career = self.collect_player_career_stats()
            team_season = self.collect_team_season_stats()
            current_leaders = self.collect_current_leaders()
            
            # Sauvegarde des métadonnées
            metadata_path = self.save_metadata()
            
            # Mise à jour des index et métadonnées globales
            try:
                from ingestion.metadata_manager import MetadataManager
                metadata_manager = MetadataManager()
                metadata_manager.update_all_metadata()
                logger.info("✅ Index et métadonnées globales mis à jour")
            except Exception as e:
                logger.warning(f"⚠️ Erreur mise à jour métadonnées globales: {e}")
            
            # Résumé de la collecte
            summary = {
                'session_id': self.metadata['session_id'],
                'players_static': len(players_static),
                'teams_static': len(teams_static),
                'player_careers': len(player_career),
                'team_seasons': len(team_season),
                'leader_categories': len(current_leaders),
                'errors_count': len(self.metadata['errors']),
                'metadata_file': metadata_path
            }
            
            logger.info("✅ Collecte complète terminée avec succès")
            logger.info(f"📊 Résumé: {summary}")
            
            return summary
            
        except Exception as e:
            error_msg = f"Erreur critique lors de la collecte: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            self.save_metadata()
            raise


