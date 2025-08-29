#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire de métadonnées et index pour DataLake NBA
Crée et maintient les index globaux et métadonnées consolidées
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd

class MetadataManager:
    """Gestionnaire des métadonnées et index du DataLake"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.metadata_dir = f'{data_dir}/metadata'
        self.raw_dir = f'{data_dir}/raw'
        
        # Création des dossiers nécessaires
        os.makedirs(self.metadata_dir, exist_ok=True)
    
    def scan_data_files(self) -> Dict[str, List[str]]:
        """Scanne tous les fichiers de données et les classe par type"""
        data_files = {
            'api_nba': [],
            'kaggle': [],
            'processed': [],
            'metadata': []
        }
        
        # Scan des fichiers API NBA
        api_files = glob.glob(f'{self.raw_dir}/api_nba/*.csv')
        data_files['api_nba'] = [os.path.basename(f) for f in api_files]
        
        # Scan des fichiers Kaggle
        kaggle_files = glob.glob(f'{self.raw_dir}/kaggle/*.csv')
        data_files['kaggle'] = [os.path.basename(f) for f in kaggle_files]
        
        # Scan des fichiers traités
        processed_files = glob.glob(f'{self.data_dir}/processed/**/*.csv', recursive=True)
        data_files['processed'] = [os.path.relpath(f, self.data_dir) for f in processed_files]
        
        # Scan des métadonnées
        metadata_files = glob.glob(f'{self.metadata_dir}/session_*.json')
        data_files['metadata'] = [os.path.basename(f) for f in metadata_files]
        
        return data_files
    
    def create_data_index(self) -> Dict[str, Any]:
        """Crée l'index global des données"""
        data_files = self.scan_data_files()
        
        # Calcul des statistiques
        total_files = sum(len(files) for files in data_files.values())
        total_size = 0
        
        # Calcul de la taille totale
        for category, files in data_files.items():
            for file in files:
                if category == 'processed':
                    file_path = f'{self.data_dir}/{file}'
                elif category == 'metadata':
                    file_path = f'{self.metadata_dir}/{file}'
                else:
                    file_path = f'{self.raw_dir}/{category}/{file}'
                
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        
        # Création de l'index
        data_index = {
            'created_at': datetime.now().isoformat(),
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'categories': {
                'api_nba': {
                    'count': len(data_files['api_nba']),
                    'files': data_files['api_nba']
                },
                'kaggle': {
                    'count': len(data_files['kaggle']),
                    'files': data_files['kaggle']
                },
                'processed': {
                    'count': len(data_files['processed']),
                    'files': data_files['processed']
                },
                'metadata': {
                    'count': len(data_files['metadata']),
                    'files': data_files['metadata']
                }
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return data_index
    
    def consolidate_session_metadata(self) -> Dict[str, Any]:
        """Consolide les métadonnées de toutes les sessions"""
        metadata_files = glob.glob(f'{self.metadata_dir}/session_*.json')
        
        if not metadata_files:
            return {}
        
        all_sessions = []
        total_players = 0
        total_teams = 0
        total_seasons = 0
        total_errors = 0
        
        for metadata_file in metadata_files:
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    all_sessions.append(session_data)
                    
                    # Accumulation des statistiques
                    if 'collected_data' in session_data:
                        data = session_data['collected_data']
                        
                        if 'players_static' in data:
                            total_players = max(total_players, data['players_static'].get('count', 0))
                        
                        if 'teams_static' in data:
                            total_teams = max(total_teams, data['teams_static'].get('count', 0))
                        
                        if 'player_career_stats' in data:
                            total_seasons += data['player_career_stats'].get('total_seasons', 0)
                        
                        if 'team_season_stats' in data:
                            total_seasons += data['team_season_stats'].get('total_seasons', 0)
                    
                    if 'errors' in session_data:
                        total_errors += len(session_data['errors'])
                        
            except Exception as e:
                print(f"Erreur lecture {metadata_file}: {e}")
                continue
        
        # Tri par date de création
        all_sessions.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        
        # Métadonnées consolidées
        consolidated_metadata = {
            'created_at': datetime.now().isoformat(),
            'total_sessions': len(all_sessions),
            'latest_session': all_sessions[0] if all_sessions else None,
            'statistics': {
                'total_players_collected': total_players,
                'total_teams_collected': total_teams,
                'total_seasons_collected': total_seasons,
                'total_errors': total_errors
            },
            'sessions': all_sessions,
            'last_updated': datetime.now().isoformat()
        }
        
        return consolidated_metadata
    
    def update_global_metadata(self) -> Dict[str, Any]:
        """Met à jour les métadonnées globales consolidées"""
        try:
            print("Mise à jour des métadonnées globales...")
            
            # Consolidation des métadonnées de session
            consolidated_metadata = self.consolidate_session_metadata()
            
            # Sauvegarde des métadonnées consolidées
            metadata_path = f'{self.metadata_dir}/metadata_globale.json'
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(consolidated_metadata, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Métadonnées globales mises à jour: {metadata_path}")
            
            return {
                'success': True,
                'metadata_path': metadata_path,
                'summary': consolidated_metadata
            }
            
        except Exception as e:
            error_msg = f"Erreur mise à jour métadonnées globales: {e}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    
    def update_data_index(self) -> Dict[str, Any]:
        """Met à jour l'index global des données"""
        try:
            print("Mise à jour de l'index des données...")
            
            # Création de l'index
            data_index = self.create_data_index()
            
            # Sauvegarde de l'index
            index_path = f'{self.metadata_dir}/index_donnees.json'
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(data_index, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Index des données mis à jour: {index_path}")
            
            return {
                'success': True,
                'index_path': index_path,
                'summary': data_index
            }
            
        except Exception as e:
            error_msg = f"Erreur mise à jour index des données: {e}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    
    def update_all_metadata(self) -> Dict[str, Any]:
        """Mise à jour complète de toutes les métadonnées et index"""
        try:
            print("🔄 Mise à jour complète des métadonnées et index...")
            
            # Mise à jour des métadonnées globales
            metadata_result = self.update_global_metadata()
            
            # Mise à jour de l'index des données
            index_result = self.update_data_index()
            
            # Résumé de la mise à jour
            summary = {
                'total_files': index_result['summary']['total_files'] if index_result['success'] else 0,
                'total_size_mb': index_result['summary']['total_size_mb'] if index_result['success'] else 0,
                'categories': index_result['summary']['categories'] if index_result['success'] else {}
            }
            
            print(f"\n✅ Mise à jour terminée avec succès!")
            print(f"  - Métadonnées: {'✅' if metadata_result['success'] else '❌'}")
            print(f"  - Index: {'✅' if index_result['success'] else '❌'}")
            
            return {
                'success': True,
                'metadata_path': metadata_result.get('metadata_path'),
                'index_path': index_result.get('index_path'),
                'summary': summary
            }
            
        except Exception as e:
            error_msg = f"Erreur lors de la mise à jour complète: {e}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }

if __name__ == "__main__":
    # Test du gestionnaire
    manager = MetadataManager()
    result = manager.update_all_metadata()
    print(f"\n🎯 Mise à jour terminée avec succès!")
