#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collecte intelligente des données NBA avec gestion des timeouts
Collecte par phases pour maximiser les données récupérées
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nba_data_collector import NBADataCollector
import time
import logging
from datetime import datetime, timedelta
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/ingestion_intelligente.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CollecteIntelligente:
    """Collecte intelligente avec gestion des timeouts et collecte par phases"""
    
    def __init__(self):
        self.collector = NBADataCollector()
        self.session_start = datetime.now()
        self.phases_completed = []
        self.errors = []
        
    def collecte_phase_1_static(self):
        """Phase 1: Données statiques (pas de timeouts)"""
        logger.info("🔄 PHASE 1: Collecte des données statiques...")
        
        try:
            # Collecte des joueurs (tous, pas que actifs)
            players = self.collector.collect_players_static()
            logger.info(f"✅ Phase 1 - Joueurs: {len(players)} collectés")
            
            # Collecte des équipes
            teams = self.collector.collect_teams_static()
            logger.info(f"✅ Phase 1 - Équipes: {len(teams)} collectées")
            
            self.phases_completed.append("phase_1_static")
            return True
            
        except Exception as e:
            error_msg = f"Erreur Phase 1: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def collecte_phase_2_players_batch(self):
        """Phase 2: Stats des joueurs par lots de 50"""
        logger.info("🔄 PHASE 2: Collecte des stats joueurs par lots...")
        
        try:
            from nba_api.stats.static import players
            
            # Récupérer TOUS les joueurs (pas que actifs)
            all_players = players.get_players()
            logger.info(f"Total joueurs disponibles: {len(all_players)}")
            
            # Traitement par lots de 50
            batch_size = 50
            total_batches = (len(all_players) + batch_size - 1) // batch_size
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(all_players))
                batch_players = all_players[start_idx:end_idx]
                
                logger.info(f"📦 Lot {batch_num + 1}/{total_batches}: {len(batch_players)} joueurs")
                
                # Collecte du lot
                player_ids = [p['id'] for p in batch_players]
                career_stats = self.collector.collect_player_career_stats(
                    player_ids=player_ids, 
                    limit=len(batch_players)
                )
                
                logger.info(f"✅ Lot {batch_num + 1} terminé: {len(career_stats)} joueurs traités")
                
                # Pause entre lots pour éviter les timeouts
                if batch_num < total_batches - 1:
                    logger.info("⏳ Pause de 2 minutes entre lots...")
                    time.sleep(120)
            
            self.phases_completed.append("phase_2_players_batch")
            return True
            
        except Exception as e:
            error_msg = f"Erreur Phase 2: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def collecte_phase_3_teams_seasons(self):
        """Phase 3: Stats des équipes par saison (1946-2025)"""
        logger.info("🔄 PHASE 3: Collecte des stats équipes par saison...")
        
        try:
            # Collecte de TOUTES les saisons depuis 1946
            team_stats = self.collector.collect_team_season_stats(
                seasons=[f"{year}-{str(year+1)[-2:]}" for year in range(1946, 2026)]
            )
            
            logger.info(f"✅ Phase 3 - Stats équipes: {len(team_stats)} équipes traitées")
            self.phases_completed.append("phase_3_teams_seasons")
            return True
            
        except Exception as e:
            error_msg = f"Erreur Phase 3: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def collecte_phase_4_leaders_multi_seasons(self):
        """Phase 4: Leaders sur plusieurs saisons"""
        logger.info("🔄 PHASE 4: Collecte des leaders sur plusieurs saisons...")
        
        try:
            from nba_api.stats.endpoints import leagueleaders
            import pandas as pd
            
            # Collecte des leaders sur les 5 dernières saisons
            seasons = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
            all_leaders = {}
            
            for season in seasons:
                logger.info(f"📊 Collecte leaders saison {season}")
                season_leaders = {}
                
                for category in self.collector.metadata.get('leader_categories', []):
                    try:
                        leaders = leagueleaders.LeagueLeaders(
                            stat_category_abbreviation=category,
                            season=season,
                            season_type_all_star='Regular Season'
                        )
                        
                        df = leaders.get_data_frames()[0]
                        df['SEASON'] = season  # Ajouter la saison
                        season_leaders[category] = df
                        
                        logger.info(f"✅ {season} - {category}: {len(df)} joueurs")
                        time.sleep(0.5)  # Pause entre catégories
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur {season} - {category}: {e}")
                        continue
                
                all_leaders[season] = season_leaders
                time.sleep(1)  # Pause entre saisons
            
            # Sauvegarde consolidée
            if all_leaders:
                all_data = []
                for season, categories in all_leaders.items():
                    for category, df in categories.items():
                        all_data.append(df)
                
                if all_data:
                    consolidated = pd.concat(all_data, ignore_index=True)
                    raw_path = f'data/raw/api_nba/leaders_multi_seasons_{self.collector.metadata["session_id"]}.csv'
                    consolidated.to_csv(raw_path, index=False)
                    logger.info(f"✅ Leaders multi-saisons sauvegardés: {raw_path}")
            
            self.phases_completed.append("phase_4_leaders_multi_seasons")
            return True
            
        except Exception as e:
            error_msg = f"Erreur Phase 4: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def run_collecte_complete(self):
        """Exécute la collecte complète par phases"""
        logger.info("🚀 DÉMARRAGE DE LA COLLECTE INTELLIGENTE COMPLÈTE")
        logger.info(f"⏰ Début: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        
        phases = [
            ("Phase 1 - Données statiques", self.collecte_phase_1_static),
            ("Phase 2 - Stats joueurs par lots", self.collecte_phase_2_players_batch),
            ("Phase 3 - Stats équipes par saison", self.collecte_phase_3_teams_seasons),
            ("Phase 4 - Leaders multi-saisons", self.collecte_phase_4_leaders_multi_seasons)
        ]
        
        for phase_name, phase_func in phases:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 DÉBUT: {phase_name}")
            logger.info(f"{'='*60}")
            
            start_time = datetime.now()
            success = phase_func()
            duration = (datetime.now() - start_time).total_seconds()
            
            if success:
                logger.info(f"✅ {phase_name} - TERMINÉ en {duration:.1f}s")
            else:
                logger.error(f"❌ {phase_name} - ÉCHOUÉ en {duration:.1f}s")
            
            # Pause entre phases
            if phase_name != phases[-1][0]:
                logger.info("⏳ Pause de 5 minutes entre phases...")
                time.sleep(300)
        
        # Résumé final
        self.save_resume_final()
        
        logger.info(f"\n{'='*60}")
        logger.info("🎯 COLLECTE INTELLIGENTE TERMINÉE")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Phases réussies: {len(self.phases_completed)}")
        logger.info(f"❌ Erreurs: {len(self.errors)}")
        logger.info(f"⏱️ Durée totale: {(datetime.now() - self.session_start).total_seconds() / 3600:.1f}h")
        
        return {
            "success": len(self.phases_completed),
            "errors": len(self.errors),
            "phases_completed": self.phases_completed,
            "duration_hours": (datetime.now() - self.session_start).total_seconds() / 3600
        }
    
    def save_resume_final(self):
        """Sauvegarde du résumé final de la session"""
        resume = {
            "session_id": self.collector.metadata["session_id"],
            "start_time": self.session_start.isoformat(),
            "end_time": datetime.now().isoformat(),
            "phases_completed": self.phases_completed,
            "errors": self.errors,
            "total_duration_hours": (datetime.now() - self.session_start).total_seconds() / 3600
        }
        
        resume_path = f'data/metadata/resume_intelligent_{self.collector.metadata["session_id"]}.json'
        with open(resume_path, 'w', encoding='utf-8') as f:
            json.dump(resume, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Résumé final sauvegardé: {resume_path}")

if __name__ == "__main__":
    collecte = CollecteIntelligente()
    resultat = collecte.run_collecte_complete()
    print(f"\n🎯 Résultat final: {resultat}")
