#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collecteur de données NBA pour DataLake - Version corrigée
Récupère et structure les données depuis l'API NBA officielle
Toutes les valeurs sont configurables via config.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nba_api.stats.endpoints import (
    playercareerstats, teamyearbyyearstats, leagueleaders,
    playergamelog, teamgamelog, commonplayerinfo,
    leaguedashplayerstats,  # Pour Player/General/Traditional
    playerdashboardbyclutch,  # Pour Player/Clutch/Traditional
    leaguedashplayerclutch,  # Pour stats clutch league-wide
    leaguedashteamstats  # Pour Team/Traditional
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
    
    def collect_player_career_stats(self) -> pd.DataFrame:
        """Collecte des statistiques de carrière pour tous les joueurs actifs"""
        logger.info("Collecte des statistiques de carrière des joueurs...")
        
        try:
            # Récupération des joueurs actifs uniquement
            active_players = [p for p in players.get_players() if p['is_active']]
            max_players = min(self.config['max_players'], len(active_players))
            
            logger.info(f"Collecte des statistiques pour {max_players} joueurs actifs...")
            
            all_career_stats = []
            
            for i, player in enumerate(active_players[:max_players]):
                try:
                    logger.info(f"Collecte joueur {i+1}/{max_players}: {player['full_name']}")
                    
                    career = playercareerstats.PlayerCareerStats(player_id=player['id'])
                    career_df = career.get_data_frames()[0]
                    
                    # Ajout des informations du joueur
                    career_df['PLAYER_NAME'] = player['full_name']
                    career_df['PLAYER_ID'] = player['id']
                    all_career_stats.append(career_df)
                    
                    logger.info(f"✅ {player['full_name']}: {len(career_df)} saisons collectées")
                    
                    # Pause configurable pour éviter la surcharge de l'API
                    time.sleep(self.config['delay'])
                    
                except Exception as e:
                    logger.warning(f"Erreur joueur {player['full_name']}: {e}")
                    continue
            
            if all_career_stats:
                # Consolidation de toutes les statistiques de carrière
                combined_career = pd.concat(all_career_stats, ignore_index=True)
                
                # Sauvegarde des données brutes
                raw_path = f'{self.output_dir}/raw/api_nba/player_career_stats_{self.metadata["session_id"]}.csv'
                combined_career.to_csv(raw_path, index=False)
                
                # Ajout aux métadonnées
                self.metadata['collected_data']['player_career_stats'] = {
                    'players_processed': len(all_career_stats),
                    'total_seasons': len(combined_career),
                    'raw_file': raw_path,
                    'columns': list(combined_career.columns)
                }
                
                logger.info(f"✅ {len(combined_career)} entrées collectées")
                return combined_career
            
            return pd.DataFrame()
            
        except Exception as e:
            error_msg = f"Erreur collecte statistiques de carrière: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return pd.DataFrame()
    
    def collect_team_season_stats(self) -> pd.DataFrame:
        """Collecte des statistiques par saison pour toutes les équipes"""
        logger.info("Collecte des statistiques par saison des équipes...")
        
        try:
            all_teams = teams.get_teams()
            all_season_stats = []
            
            # Collecte pour les dernières saisons configurées (limite raisonnable pour éviter la surcharge)
            seasons_to_collect = self.config.get('collection_limits', {}).get('team_season_stats', 10)
            seasons_to_collect = self.config['seasons'][-seasons_to_collect:]
            
            for season in seasons_to_collect:
                try:
                    logger.info(f"Collecte saison {season}...")
                    
                    season_stats = teamyearbyyearstats.TeamYearByYearStats(
                        team_id=all_teams[0]['id'],  # Utilise la première équipe comme référence
                        season_type_all_star='Regular Season'  # Paramètre correct selon l'API
                    )
                    
                    # Récupération des données pour cette saison
                    season_data = season_stats.get_data_frames()[0]
                    season_data['SEASON'] = season
                    all_season_stats.append(season_data)
                    
                    logger.info(f"✅ Saison {season}: {len(season_data)} équipes collectées")
                    time.sleep(self.config['delay'])
                    
                except Exception as e:
                    logger.warning(f"Erreur saison {season}: {e}")
                    continue
            
            if all_season_stats:
                # Consolidation de toutes les saisons
                combined_seasons = pd.concat(all_season_stats, ignore_index=True)
                
                # Sauvegarde des données brutes
                raw_path = f'{self.output_dir}/raw/api_nba/team_season_stats_{self.metadata["session_id"]}.csv'
                combined_seasons.to_csv(raw_path, index=False)
                
                # Ajout aux métadonnées
                self.metadata['collected_data']['team_season_stats'] = {
                    'seasons_processed': len(all_season_stats),
                    'total_entries': len(combined_seasons),
                    'raw_file': raw_path,
                    'columns': list(combined_seasons.columns)
                }
                
                logger.info(f"✅ {len(combined_seasons)} entrées collectées")
                return combined_seasons
            
            return pd.DataFrame()
            
        except Exception as e:
            error_msg = f"Erreur collecte statistiques par saison: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return pd.DataFrame()
    
    def collect_current_leaders(self) -> Dict[str, pd.DataFrame]:
        """Collecte des leaders actuels dans différentes catégories"""
        logger.info("Collecte des leaders actuels...")
        
        try:
            # Utiliser la configuration pour la saison des leaders
            if 'leaders_season' in self.config:
                season_to_use = self.config['leaders_season']
            else:
                # Fallback intelligent : utiliser la dernière saison avec des données
                season_to_use = self.config['seasons'][-1]
            
            logger.info(f"Collecte des leaders pour la saison: {season_to_use}")
            
            leaders_data = {}
            
            for category in self.config['leader_categories']:
                try:
                    logger.info(f"Collecte leaders {category}...")
                    
                    leaders = leagueleaders.LeagueLeaders(
                        season=season_to_use,
                        season_type_all_star='Regular Season'
                    )
                    
                    leaders_df = leaders.get_data_frames()[0]
                    
                    # Vérifier que les données ne sont pas vides
                    if not leaders_df.empty:
                        leaders_data[category] = leaders_df
                        logger.info(f"✅ Leaders {category}: {len(leaders_df)} joueurs collectés")
                    else:
                        logger.warning(f"Aucun leader trouvé pour {category} en saison {season_to_use}")
                    
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
            else:
                logger.warning("Aucun leader collecté - création d'un fichier vide")
                # Créer un DataFrame vide avec les bonnes colonnes
                empty_df = pd.DataFrame(columns=['PLAYER_ID', 'RANK', 'PLAYER', 'TEAM_ID', 'TEAM', 'GP', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'EFF', 'AST_TOV', 'STL_TOV'])
                raw_path = f'{self.output_dir}/raw/api_nba/leaders_ALL_{self.metadata["session_id"]}.csv'
                empty_df.to_csv(raw_path, index=False)
            
            # Ajout aux métadonnées
            self.metadata['collected_data']['current_leaders'] = {
                'categories_processed': len(leaders_data),
                'total_players': sum(len(df) for df in leaders_data.values()),
                'total_file': raw_path,
                'season_used': season_to_use
            }
            
            return leaders_data
        
        except Exception as e:
            error_msg = f"Erreur collecte leaders: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return {}
    
    def collect_player_traditional_stats(self) -> pd.DataFrame:
        """Collecte des statistiques traditionnelles des joueurs via NBA Stats API"""
        if not self.config.get('advanced_stats', {}).get('player_traditional', {}).get('enabled', False):
            logger.info("Statistiques traditionnelles des joueurs désactivées dans la configuration")
            return pd.DataFrame()
        
        logger.info("Collecte des statistiques traditionnelles des joueurs...")
        
        try:
            config = self.config['advanced_stats']['player_traditional']
            
            # Récupérer d'abord les informations des joueurs pour enrichir les données
            all_players = players.get_players()
            players_dict = {p['id']: p['full_name'] for p in all_players}
            
            # Récupération des statistiques pour TOUTES les saisons depuis 2000
            # Suppression de la limitation artificielle seasons_to_collect
            seasons_to_collect = self.config['seasons']  # Depuis 2000
            all_stats = []
            
            logger.info(f"Collecte des stats traditionnelles pour {len(seasons_to_collect)} saisons depuis {seasons_to_collect[0]}")
            
            for season in seasons_to_collect:
                try:
                    logger.info(f"Collecte stats traditionnelles saison {season}...")
                    
                    # Utilisation de leaguedashplayerstats pour les stats league-wide
                    stats = leaguedashplayerstats.LeagueDashPlayerStats(
                        season=f"{season}-{str(season + 1)[-2:]}",
                        measure_type_detailed_defense=config['measure_type'],
                        per_mode_detailed=config['per_mode'],
                        season_type_all_star=config['season_type']
                    )
                    
                    stats_df = stats.get_data_frames()[0]
                    
                    # Enrichir les données avec les noms des joueurs
                    if not stats_df.empty:
                        # Ajouter le nom du joueur depuis les données statiques
                        stats_df['PLAYER_NAME_ENRICHED'] = stats_df['PLAYER_ID'].map(players_dict)
                        
                        # Si PLAYER_NAME est vide, utiliser PLAYER_NAME_ENRICHED
                        if 'PLAYER_NAME' in stats_df.columns:
                            stats_df['PLAYER_NAME'] = stats_df['PLAYER_NAME'].fillna(stats_df['PLAYER_NAME_ENRICHED'])
                        else:
                            stats_df['PLAYER_NAME'] = stats_df['PLAYER_NAME_ENRICHED']
                        
                        # Supprimer la colonne temporaire
                        stats_df = stats_df.drop('PLAYER_NAME_ENRICHED', axis=1)
                        
                        stats_df['SEASON'] = season
                        all_stats.append(stats_df)
                        
                        logger.info(f"✅ Saison {season}: {len(stats_df)} joueurs collectés")
                    else:
                        logger.warning(f"Aucune donnée trouvée pour la saison {season}")
                    
                    time.sleep(self.config['delay'])
                    
                except Exception as e:
                    logger.warning(f"Erreur saison {season}: {e}")
                    continue
            
            if all_stats:
                # Consolidation de toutes les saisons
                combined_stats = pd.concat(all_stats, ignore_index=True)
                
                # Sauvegarde des données brutes
                raw_path = f'{self.output_dir}/raw/api_nba/player_traditional_stats_{self.metadata["session_id"]}.csv'
                combined_stats.to_csv(raw_path, index=False)
                
                # Ajout aux métadonnées
                self.metadata['collected_data']['player_traditional_stats'] = {
                    'seasons_processed': len(all_stats),
                    'total_players': len(combined_stats),
                    'raw_file': raw_path,
                    'columns': list(combined_stats.columns),
                    'seasons_range': f"{seasons_to_collect[0]} - {seasons_to_collect[-1]}"
                }
                
                logger.info(f"✅ {len(combined_stats)} entrées collectées sur {len(all_stats)} saisons")
                return combined_stats
            
            return pd.DataFrame()
            
        except Exception as e:
            error_msg = f"Erreur collecte statistiques traditionnelles: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return pd.DataFrame()
    
    def collect_player_clutch_stats(self) -> pd.DataFrame:
        """Collecte des statistiques en situation de clutch des joueurs via NBA Stats API"""
        if not self.config.get('advanced_stats', {}).get('player_clutch', {}).get('enabled', False):
            logger.info("Statistiques clutch des joueurs désactivées dans la configuration")
            return pd.DataFrame()
        
        logger.info("Collecte des statistiques clutch des joueurs...")
        
        try:
            config = self.config['advanced_stats']['player_clutch']
            
            # Récupérer d'abord les informations des joueurs pour enrichir les données
            all_players = players.get_players()
            players_dict = {p['id']: p['full_name'] for p in all_players}
            
            # Récupération des statistiques clutch pour TOUTES les saisons depuis 2000
            # Suppression de la limitation artificielle seasons_to_collect
            seasons_to_collect = self.config['seasons']  # Depuis 2000
            all_clutch_stats = []
            
            logger.info(f"Collecte des stats clutch pour {len(seasons_to_collect)} saisons depuis {seasons_to_collect[0]}")
            
            for season in seasons_to_collect:
                try:
                    logger.info(f"Collecte stats clutch saison {season}...")
                    
                    # Utilisation de leaguedashplayerclutch pour les stats clutch league-wide
                    clutch_stats = leaguedashplayerclutch.LeagueDashPlayerClutch(
                        season=f"{season}-{str(season + 1)[-2:]}",
                        measure_type_detailed_defense=config['measure_type'],
                        per_mode_detailed=config['per_mode'],
                        season_type_all_star=config['season_type'],
                        clutch_time=config['clutch_time'],
                        ahead_behind=config['ahead_behind']
                    )
                    
                    clutch_df = clutch_stats.get_data_frames()[0]
                    
                    # Enrichir les données avec les noms des joueurs
                    if not clutch_df.empty:
                        # Ajouter le nom du joueur depuis les données statiques
                        clutch_df['PLAYER_NAME_ENRICHED'] = clutch_df['PLAYER_ID'].map(players_dict)
                        
                        # Si PLAYER_NAME est vide, utiliser PLAYER_NAME_ENRICHED
                        if 'PLAYER_NAME' in clutch_df.columns:
                            clutch_df['PLAYER_NAME'] = clutch_df['PLAYER_NAME'].fillna(clutch_df['PLAYER_NAME_ENRICHED'])
                        else:
                            clutch_df['PLAYER_NAME'] = clutch_df['PLAYER_NAME_ENRICHED']
                        
                        # Supprimer la colonne temporaire
                        clutch_df = clutch_df.drop('PLAYER_NAME_ENRICHED', axis=1)
                        
                        clutch_df['SEASON'] = season
                        clutch_df['CLUTCH_TIME'] = config['clutch_time']
                        clutch_df['AHEAD_BEHIND'] = config['ahead_behind']
                        all_clutch_stats.append(clutch_df)
                        
                        logger.info(f"✅ Saison {season}: {len(clutch_df)} joueurs clutch collectés")
                    else:
                        logger.warning(f"Aucune donnée clutch trouvée pour la saison {season}")
                    
                    time.sleep(self.config['delay'])
                    
                except Exception as e:
                    logger.warning(f"Erreur clutch saison {season}: {e}")
                    continue
            
            if all_clutch_stats:
                # Consolidation de toutes les saisons
                combined_clutch = pd.concat(all_clutch_stats, ignore_index=True)
                
                # Sauvegarde des données brutes
                raw_path = f'{self.output_dir}/raw/api_nba/player_clutch_stats_{self.metadata["session_id"]}.csv'
                combined_clutch.to_csv(raw_path, index=False)
                
                # Ajout aux métadonnées
                self.metadata['collected_data']['player_clutch_stats'] = {
                    'seasons_processed': len(all_clutch_stats),
                    'total_players': len(combined_clutch),
                    'raw_file': raw_path,
                    'columns': list(combined_clutch.columns),
                    'seasons_range': f"{seasons_to_collect[0]} - {seasons_to_collect[-1]}"
                }
                
                logger.info(f"✅ {len(combined_clutch)} entrées collectées sur {len(all_clutch_stats)} saisons")
                return combined_clutch
            
            return pd.DataFrame()
            
        except Exception as e:
            error_msg = f"Erreur collecte statistiques clutch: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return pd.DataFrame()
    
    def collect_team_traditional_stats(self) -> pd.DataFrame:
        """Collecte des statistiques traditionnelles des équipes via NBA Stats API"""
        if not self.config.get('advanced_stats', {}).get('team_traditional', {}).get('enabled', False):
            logger.info("Statistiques traditionnelles des équipes désactivées dans la configuration")
            return pd.DataFrame()
        
        logger.info("Collecte des statistiques traditionnelles des équipes...")
        
        try:
            config = self.config['advanced_stats']['team_traditional']
            
            # Récupération des statistiques pour TOUTES les saisons depuis 2000
            # Suppression de la limitation artificielle seasons_to_collect
            seasons_to_collect = self.config['seasons']  # Depuis 2000
            all_team_stats = []
            
            logger.info(f"Collecte des stats équipes pour {len(seasons_to_collect)} saisons depuis {seasons_to_collect[0]}")
            
            for season in seasons_to_collect:
                try:
                    logger.info(f"Collecte équipes saison {season}...")
                    
                    # Utilisation de leaguedashteamstats pour les stats d'équipes
                    team_stats = leaguedashteamstats.LeagueDashTeamStats(
                        season=f"{season}-{str(season + 1)[-2:]}",
                        measure_type_detailed_defense=config['measure_type'],
                        per_mode_detailed=config['per_mode'],
                        season_type_all_star=config['season_type']
                    )
                    
                    team_df = team_stats.get_data_frames()[0]
                    team_df['SEASON'] = season
                    all_team_stats.append(team_df)
                    
                    logger.info(f"✅ Équipes saison {season}: {len(team_df)} équipes collectées")
                    time.sleep(self.config['delay'])
                    
                except Exception as e:
                    logger.warning(f"Erreur équipes saison {season}: {e}")
                    continue
            
            if all_team_stats:
                # Consolidation de toutes les saisons
                combined_teams = pd.concat(all_team_stats, ignore_index=True)
                
                # Sauvegarde des données brutes
                raw_path = f'{self.output_dir}/raw/api_nba/team_traditional_stats_{self.metadata["session_id"]}.csv'
                combined_teams.to_csv(raw_path, index=False)
                
                # Ajout aux métadonnées
                self.metadata['collected_data']['team_traditional_stats'] = {
                    'seasons_processed': len(all_team_stats),
                    'total_teams': len(combined_teams),
                    'raw_file': raw_path,
                    'columns': list(combined_teams.columns),
                    'seasons_range': f"{seasons_to_collect[0]} - {seasons_to_collect[-1]}"
                }
                
                logger.info(f"✅ {len(combined_teams)} entrées collectées sur {len(all_team_stats)} saisons")
                return combined_teams
            
            return pd.DataFrame()
            
        except Exception as e:
            error_msg = f"Erreur collecte statistiques équipes: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return pd.DataFrame()
    
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
        logger.info(f"Démarrage de la collecte complète des données NBA (limite: {max_players} joueurs actifs)")
        
        try:
            # Collecte des données statiques
            players_static = self.collect_players_static()
            teams_static = self.collect_teams_static()
            
            # Collecte des statistiques détaillées
            player_career = self.collect_player_career_stats()
            team_season = self.collect_team_season_stats()
            current_leaders = self.collect_current_leaders()
            
            # Nouvelles collectes de statistiques avancées
            player_traditional = self.collect_player_traditional_stats()
            player_clutch = self.collect_player_clutch_stats()
            team_traditional = self.collect_team_traditional_stats()
            
            # Sauvegarde des métadonnées
            metadata_path = self.save_metadata()
            
            # Mise à jour des index et métadonnées globales
            try:
                from ingestion.metadata_manager import MetadataManager
                metadata_manager = MetadataManager()
                metadata_manager.update_all_metadata()
                logger.info("✅ Index et métadonnées globales mis à jour")
            except Exception as e:
                logger.warning(f"Erreur mise à jour métadonnées globales: {e}")
            
            # Résumé de la collecte
            summary = {
                'session_id': self.metadata['session_id'],
                'players_static': len(players_static),
                'teams_static': len(teams_static),
                'player_careers': len(player_career),
                'team_seasons': len(team_season),
                'leader_categories': len(current_leaders),
                'player_traditional_stats': len(player_traditional),
                'player_clutch_stats': len(player_clutch),
                'team_traditional_stats': len(team_traditional),
                'errors_count': len(self.metadata['errors']),
                'metadata_file': metadata_path
            }
            
            logger.info("✅ Collecte complète terminée avec succès")
            logger.info(f"Résumé: {summary}")
            
            return summary
            
        except Exception as e:
            error_msg = f"Erreur critique lors de la collecte: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            self.save_metadata()
            raise
