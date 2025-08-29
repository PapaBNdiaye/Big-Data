#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intégrateur du dataset Kaggle NBA
Gère le téléchargement, l'analyse et l'intégration des données historiques
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import json
import zipfile
import requests
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KaggleIntegrator:
    """Intégrateur du dataset Kaggle NBA"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.kaggle_dir = f'{data_dir}/kaggle'
        self.raw_dir = f'{data_dir}/raw/kaggle'  # Données Kaggle dans raw/kaggle
        self.processed_dir = f'{data_dir}/processed'
        
        # Création des dossiers nécessaires
        os.makedirs(self.kaggle_dir, exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Métadonnées de l'intégration
        self.metadata = {
            'session_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'start_time': datetime.now().isoformat(),
            'kaggle_dataset': 'basketball',
            'source_url': 'https://www.kaggle.com/datasets/wyattowalsh/basketball/data',
            'integration_status': 'pending',
            'files_processed': [],
            'errors': []
        }
        
        logger.info(f"Intégrateur Kaggle initialisé - Session: {self.metadata['session_id']}")
        
        # Vérifier et corriger l'organisation des données existantes
        self._verifier_organisation_donnees()
    
    def _verifier_organisation_donnees(self):
        """Vérifie et corrige l'organisation des données Kaggle"""
        try:
            # Vérifier si les données sont dans raw/kaggle
            if os.path.exists(self.raw_dir) and len(os.listdir(self.raw_dir)) > 0:
                logger.info("✅ Données Kaggle déjà organisées dans la structure DataLake")
                return
            
            # Si pas dans raw/kaggle mais dans kaggle/, les réorganiser
            if os.path.exists(self.kaggle_dir) and len(os.listdir(self.kaggle_dir)) > 0:
                logger.info("🔄 Réorganisation des données Kaggle existantes...")
                self._reorganiser_donnees_existantes()
            else:
                logger.info("📁 Aucune donnée Kaggle trouvée, prêt pour téléchargement")
                
        except Exception as e:
            logger.warning(f"Erreur vérification organisation: {e}")
    
    def _reorganiser_donnees_existantes(self):
        """Réorganise les données Kaggle existantes dans la structure DataLake"""
        try:
            import shutil
            
            # Créer le dossier raw/kaggle
            os.makedirs(self.raw_dir, exist_ok=True)
            
            # Copier tous les fichiers de kaggle/ vers raw/kaggle/
            for item in os.listdir(self.kaggle_dir):
                src = os.path.join(self.kaggle_dir, item)
                dst = os.path.join(self.raw_dir, item)
                
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    logger.info(f"  📄 Fichier réorganisé: {item}")
                elif os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    logger.info(f"  📁 Dossier réorganisé: {item}")
            
            logger.info("✅ Données Kaggle réorganisées dans la structure DataLake")
            
        except Exception as e:
            logger.error(f"Erreur réorganisation données existantes: {e}")
    
    def telecharger_dataset_kaggle(self, force_download: bool = False) -> bool:
        """
        Télécharge le dataset Kaggle NBA
        Utilise kagglehub pour un téléchargement moderne et simple
        """
        logger.info("Téléchargement du dataset Kaggle NBA via kagglehub...")
        
        try:
            # Vérification si le dataset existe déjà
            if os.path.exists(self.kaggle_dir) and len(os.listdir(self.kaggle_dir)) > 1 and not force_download:
                logger.info("Dataset Kaggle déjà présent, téléchargement ignoré")
                return True
            
            # Téléchargement via kagglehub
            try:
                import kagglehub
                logger.info("Tentative de téléchargement via kagglehub...")
                
                # Téléchargement du dataset
                dataset_path = kagglehub.dataset_download("wyattowalsh/basketball")
                
                logger.info(f"✅ Dataset téléchargé via kagglehub: {dataset_path}")
                
                # Copie des fichiers vers notre dossier kaggle
                self._copier_fichiers_kaggle(dataset_path)
                
                return True
                
            except ImportError:
                logger.warning("Module kagglehub non installé, téléchargement manuel requis")
                self._instructions_telechargement_manuel()
                return False
                
            except Exception as e:
                logger.warning(f"Erreur kagglehub: {e}")
                self._instructions_telechargement_manuel()
                return False
                
        except Exception as e:
            error_msg = f"Erreur téléchargement dataset: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return False
    
    def _instructions_telechargement_manuel(self):
        """Affiche les instructions pour le téléchargement manuel"""
        print("\n📥 TÉLÉCHARGEMENT MANUEL REQUIS")
        print("="*50)
        print("1. Allez sur : https://www.kaggle.com/datasets/wyattowalsh/basketball/data")
        print("2. Cliquez sur 'Download' (bouton bleu)")
        print("3. Placez le fichier ZIP dans le dossier : data/kaggle/")
        print("4. Renommez-le en : basketball_dataset.zip")
        print("5. Relancez l'intégration")
        print("="*50)
        
        # Création du fichier d'instructions
        instructions_path = f'{self.kaggle_dir}/INSTRUCTIONS_TELECHARGEMENT.txt'
        with open(instructions_path, 'w', encoding='utf-8') as f:
            f.write("Instructions de téléchargement manuel du dataset Kaggle NBA\n")
            f.write("="*50 + "\n")
            f.write("1. Allez sur : https://www.kaggle.com/datasets/wyattowalsh/basketball/data\n")
            f.write("2. Cliquez sur 'Download' (bouton bleu)\n")
            f.write("3. Placez le fichier ZIP dans ce dossier\n")
            f.write("4. Renommez-le en : basketball_dataset.zip\n")
            f.write("5. Relancez l'intégration\n")
    
    def _copier_fichiers_kaggle(self, dataset_path: str):
        """Copie les fichiers du dataset téléchargé vers la structure DataLake"""
        try:
            logger.info(f"Copie des fichiers depuis {dataset_path} vers la structure DataLake...")
            
            # Création des dossiers de destination
            os.makedirs(self.kaggle_dir, exist_ok=True)  # Backup original
            os.makedirs(self.raw_dir, exist_ok=True)     # Données brutes DataLake
            
            # Copie des fichiers vers raw/kaggle (structure DataLake)
            import shutil
            for item in os.listdir(dataset_path):
                src = os.path.join(dataset_path, item)
                dst_raw = os.path.join(self.raw_dir, item)  # data/raw/kaggle/
                dst_backup = os.path.join(self.kaggle_dir, item)  # data/kaggle/ (backup)
                
                if os.path.isfile(src):
                    # Copier vers raw/kaggle (structure DataLake)
                    shutil.copy2(src, dst_raw)
                    logger.info(f"  📄 Fichier copié vers DataLake: {item}")
                    
                    # Copier aussi vers backup
                    shutil.copy2(src, dst_backup)
                    logger.info(f"  📄 Fichier copié vers backup: {item}")
                    
                elif os.path.isdir(src):
                    # Copier vers raw/kaggle (structure DataLake)
                    shutil.copytree(src, dst_raw, dirs_exist_ok=True)
                    logger.info(f"  📁 Dossier copié vers DataLake: {item}")
                    
                    # Copier aussi vers backup
                    shutil.copytree(src, dst_backup, dirs_exist_ok=True)
                    logger.info(f"  📁 Dossier copié vers backup: {item}")
            
            logger.info("✅ Copie des fichiers terminée - Structure DataLake respectée")
            logger.info(f"   📁 Données brutes: {self.raw_dir}")
            logger.info(f"   📁 Backup original: {self.kaggle_dir}")
            
        except Exception as e:
            logger.warning(f"Erreur lors de la copie des fichiers: {e}")
    
    def extraire_dataset(self) -> bool:
        """Extrait le dataset ZIP téléchargé (si nécessaire)"""
        logger.info("Vérification de l'extraction du dataset Kaggle...")
        
        try:
            # kagglehub extrait automatiquement les fichiers, vérifions s'ils sont présents
            csv_files = [f for f in os.listdir(self.kaggle_dir) if f.endswith('.csv')]
            
            if csv_files:
                logger.info(f"✅ Dataset déjà extrait - {len(csv_files)} fichiers CSV trouvés")
                return True
            
            # Si pas de fichiers CSV, vérifions s'il y a un ZIP à extraire
            zip_path = f'{self.kaggle_dir}/basketball_dataset.zip'
            
            if os.path.exists(zip_path):
                logger.info("Extraction du fichier ZIP...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.kaggle_dir)
                logger.info("✅ Dataset extrait avec succès")
                return True
            else:
                logger.warning("Aucun fichier CSV ou ZIP trouvé")
                return False
            
        except Exception as e:
            error_msg = f"Erreur extraction dataset: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return False
    
    def analyser_structure_dataset(self) -> Dict:
        """Analyse la structure et le contenu du dataset"""
        logger.info("Analyse de la structure du dataset...")
        
        try:
            analysis = {
                'files_found': [],
                'file_sizes': {},
                'dataframes_info': {},
                'sample_data': {},
                'columns_summary': {}
            }
            
            # Recherche des fichiers CSV dans le dossier Kaggle
            kaggle_files = []
            for root, dirs, files in os.walk(self.kaggle_dir):
                for file in files:
                    if file.endswith('.csv'):
                        kaggle_files.append(os.path.join(root, file))
            
            if not kaggle_files:
                logger.warning("Aucun fichier CSV trouvé dans le dataset")
                return analysis
            
            logger.info(f"📁 {len(kaggle_files)} fichiers CSV trouvés")
            
            for file_path in kaggle_files:
                try:
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    
                    analysis['files_found'].append(file_name)
                    analysis['file_sizes'][file_name] = f"{file_size:.2f} MB"
                    
                    # Lecture et analyse du fichier
                    logger.info(f"Analyse de {file_name}...")
                    
                    # Lecture par chunks pour les gros fichiers
                    chunk_size = 10000
                    df_sample = pd.read_csv(file_path, nrows=chunk_size)
                    
                    # Informations sur le DataFrame
                    analysis['dataframes_info'][file_name] = {
                        'rows_sample': len(df_sample),
                        'columns': list(df_sample.columns),
                        'dtypes': df_sample.dtypes.to_dict(),
                        'memory_usage': df_sample.memory_usage(deep=True).sum() / (1024 * 1024)  # MB
                    }
                    
                    # Échantillon de données
                    analysis['sample_data'][file_name] = df_sample.head(3).to_dict('records')
                    
                    # Résumé des colonnes
                    analysis['columns_summary'][file_name] = {
                        'total_columns': len(df_sample.columns),
                        'numeric_columns': len(df_sample.select_dtypes(include=[np.number]).columns),
                        'text_columns': len(df_sample.select_dtypes(include=['object']).columns),
                        'date_columns': len(df_sample.select_dtypes(include=['datetime']).columns)
                    }
                    
                    logger.info(f"✅ {file_name} analysé - {len(df_sample.columns)} colonnes")
                    
                except Exception as e:
                    error_msg = f"Erreur analyse {file_name}: {e}"
                    logger.error(error_msg)
                    self.metadata['errors'].append(error_msg)
                    continue
            
            # Sauvegarde de l'analyse
            analysis_path = f'{self.kaggle_dir}/structure_analysis_{self.metadata["session_id"]}.json'
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Analyse de structure sauvegardée: {analysis_path}")
            
            return analysis
            
        except Exception as e:
            error_msg = f"Erreur analyse structure: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return {}
    
    def valider_qualite_donnees(self) -> Dict:
        """Valide la qualité des données du dataset"""
        logger.info("Validation de la qualité des données...")
        
        try:
            validation_report = {
                'files_validated': [],
                'quality_metrics': {},
                'issues_found': [],
                'recommendations': []
            }
            
            # Recherche des fichiers CSV
            csv_files = [f for f in os.listdir(self.kaggle_dir) if f.endswith('.csv')]
            
            for csv_file in csv_files:
                file_path = os.path.join(self.kaggle_dir, csv_file)
                logger.info(f"Validation de {csv_file}...")
                
                try:
                    # Lecture par chunks
                    chunk_size = 50000
                    df_chunk = pd.read_csv(file_path, nrows=chunk_size)
                    
                    # Métriques de qualité
                    quality_metrics = {
                        'total_rows_sample': len(df_chunk),
                        'missing_values': df_chunk.isnull().sum().sum(),
                        'missing_percentage': (df_chunk.isnull().sum().sum() / (len(df_chunk) * len(df_chunk.columns))) * 100,
                        'duplicate_rows': df_chunk.duplicated().sum(),
                        'duplicate_percentage': (df_chunk.duplicated().sum() / len(df_chunk)) * 100,
                        'data_types': df_chunk.dtypes.value_counts().to_dict()
                    }
                    
                    validation_report['files_validated'].append(csv_file)
                    validation_report['quality_metrics'][csv_file] = quality_metrics
                    
                    # Détection des problèmes
                    issues = []
                    if quality_metrics['missing_percentage'] > 20:
                        issues.append("Taux de valeurs manquantes élevé (>20%)")
                    if quality_metrics['duplicate_percentage'] > 10:
                        issues.append("Taux de doublons élevé (>10%)")
                    
                    if issues:
                        validation_report['issues_found'].extend([f"{csv_file}: {issue}" for issue in issues])
                    
                    # Recommandations
                    recommendations = []
                    if quality_metrics['missing_percentage'] > 10:
                        recommendations.append(f"Considérer l'imputation des valeurs manquantes pour {csv_file}")
                    if quality_metrics['duplicate_percentage'] > 5:
                        recommendations.append(f"Nettoyer les doublons pour {csv_file}")
                    
                    validation_report['recommendations'].extend(recommendations)
                    
                    logger.info(f"✅ {csv_file} validé - {quality_metrics['missing_percentage']:.1f}% manquants")
                    
                except Exception as e:
                    error_msg = f"Erreur validation {csv_file}: {e}"
                    logger.error(error_msg)
                    validation_report['issues_found'].append(error_msg)
                    continue
            
            # Sauvegarde du rapport de validation
            validation_path = f'{self.kaggle_dir}/quality_validation_{self.metadata["session_id"]}.json'
            with open(validation_path, 'w', encoding='utf-8') as f:
                json.dump(validation_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Rapport de validation sauvegardé: {validation_path}")
            
            return validation_report
            
        except Exception as e:
            error_msg = f"Erreur validation qualité: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return {}
    
    def fusionner_avec_api_nba(self) -> bool:
        """Fusionne les données Kaggle avec les données de l'API NBA"""
        logger.info("Fusion des données Kaggle avec l'API NBA...")
        
        try:
            # Vérification des données disponibles
            kaggle_files = [f for f in os.listdir(self.kaggle_dir) if f.endswith('.csv')]
            api_files = [f for f in os.listdir(self.raw_dir) if f.endswith('.csv')]
            
            if not kaggle_files:
                logger.error("Aucun fichier Kaggle disponible pour la fusion")
                return False
            
            if not api_files:
                logger.error("Aucun fichier API disponible pour la fusion")
                return False
            
            logger.info(f"📁 Fusion de {len(kaggle_files)} fichiers Kaggle avec {len(api_files)} fichiers API")
            
            # Création du dossier de fusion
            fusion_dir = f'{self.processed_dir}/fusion_{self.metadata["session_id"]}'
            os.makedirs(fusion_dir, exist_ok=True)
            
            # Traitement des fichiers de fusion
            fusion_results = {}
            
            for kaggle_file in kaggle_files:
                try:
                    kaggle_path = os.path.join(self.kaggle_dir, kaggle_file)
                    logger.info(f"Traitement de {kaggle_file}...")
                    
                    # Lecture du fichier Kaggle
                    df_kaggle = pd.read_csv(kaggle_path, nrows=10000)  # Limite pour la démo
                    
                    # Recherche de correspondances avec l'API
                    api_matches = self._trouver_correspondances_api(df_kaggle, kaggle_file)
                    
                    if api_matches:
                        # Fusion des données
                        df_fusion = self._fusionner_donnees(df_kaggle, api_matches, kaggle_file)
                        
                        # Sauvegarde du fichier fusionné
                        fusion_path = os.path.join(fusion_dir, f"fusion_{kaggle_file}")
                        df_fusion.to_csv(fusion_path, index=False)
                        
                        fusion_results[kaggle_file] = {
                            'fusion_path': fusion_path,
                            'rows_original': len(df_kaggle),
                            'rows_fusion': len(df_fusion),
                            'api_matches': len(api_matches)
                        }
                        
                        logger.info(f"✅ {kaggle_file} fusionné - {len(df_fusion)} lignes")
                    else:
                        logger.info(f"ℹ️ Aucune correspondance API trouvée pour {kaggle_file}")
                        
                except Exception as e:
                    error_msg = f"Erreur fusion {kaggle_file}: {e}"
                    logger.error(error_msg)
                    continue
            
            # Sauvegarde des résultats de fusion
            fusion_summary_path = os.path.join(fusion_dir, 'fusion_summary.json')
            with open(fusion_summary_path, 'w', encoding='utf-8') as f:
                json.dump(fusion_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Fusion terminée - {len(fusion_results)} fichiers traités")
            
            return True
            
        except Exception as e:
            error_msg = f"Erreur fusion données: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return False
    
    def _trouver_correspondances_api(self, df_kaggle: pd.DataFrame, kaggle_file: str) -> List[str]:
        """Trouve les correspondances entre les données Kaggle et l'API"""
        correspondances = []
        
        try:
            # Recherche des fichiers API correspondants
            if 'player' in kaggle_file.lower():
                api_files = [f for f in os.listdir(self.raw_dir) if 'player' in f.lower()]
            elif 'team' in kaggle_file.lower():
                api_files = [f for f in os.listdir(self.raw_dir) if 'team' in f.lower()]
            elif 'game' in kaggle_file.lower():
                api_files = [f for f in os.listdir(self.raw_dir) if 'game' in f.lower()]
            else:
                api_files = [f for f in os.listdir(self.raw_dir)]
            
            correspondances = api_files[:3]  # Limite à 3 correspondances
            
        except Exception as e:
            logger.warning(f"Erreur recherche correspondances: {e}")
        
        return correspondances
    
    def _fusionner_donnees(self, df_kaggle: pd.DataFrame, api_files: List[str], kaggle_file: str) -> pd.DataFrame:
        """Fusionne les données Kaggle avec les données API"""
        df_fusion = df_kaggle.copy()
        
        try:
            # Ajout d'une colonne source
            df_fusion['source'] = 'kaggle'
            df_fusion['fusion_timestamp'] = datetime.now().isoformat()
            
            # Ajout des métadonnées de fusion
            df_fusion['api_files_matched'] = str(api_files)
            df_fusion['fusion_session'] = self.metadata['session_id']
            
            # Tentative de correspondance des colonnes
            for api_file in api_files:
                try:
                    api_path = os.path.join(self.raw_dir, api_file)
                    df_api = pd.read_csv(api_path, nrows=1000)  # Échantillon API
                    
                    # Recherche de colonnes communes
                    common_columns = set(df_kaggle.columns) & set(df_api.columns)
                    
                    if common_columns:
                        logger.info(f"  📊 Colonnes communes trouvées: {list(common_columns)}")
                        
                        # Ajout d'informations de correspondance
                        df_fusion[f'api_{api_file}_columns_matched'] = str(list(common_columns))
                        
                except Exception as e:
                    logger.warning(f"  ⚠️ Erreur lecture {api_file}: {e}")
                    continue
            
        except Exception as e:
            logger.warning(f"Erreur fusion: {e}")
        
        return df_fusion
    
    def organiser_fichiers(self) -> bool:
        """Organise et structure les fichiers de données"""
        logger.info("Organisation des fichiers de données...")
        
        try:
            # Structure d'organisation
            organization_structure = {
                'kaggle': {
                    'raw': 'Données brutes Kaggle',
                    'processed': 'Données traitées Kaggle',
                    'analysis': 'Analyses et rapports'
                },
                'api': {
                    'raw': 'Données brutes API NBA',
                    'processed': 'Données traitées API NBA'
                },
                'fusion': {
                    'combined': 'Données fusionnées',
                    'validation': 'Validation et qualité'
                }
            }
            
            # Création des dossiers d'organisation
            for category, subdirs in organization_structure.items():
                for subdir, description in subdirs.items():
                    dir_path = f'{self.data_dir}/{category}/{subdir}'
                    os.makedirs(dir_path, exist_ok=True)
                    
                    # Création d'un fichier README pour chaque dossier
                    readme_path = os.path.join(dir_path, 'README.md')
                    if not os.path.exists(readme_path):
                        with open(readme_path, 'w', encoding='utf-8') as f:
                            f.write(f"# {description}\n\n")
                            f.write(f"Dossier: {category}/{subdir}\n\n")
                            f.write(f"Description: {description}\n")
                            f.write(f"Créé le: {datetime.now().isoformat()}\n")
            
            # Déplacement des fichiers existants
            self._deplacer_fichiers_existants()
            
            logger.info("✅ Organisation des fichiers terminée")
            return True
            
        except Exception as e:
            error_msg = f"Erreur organisation fichiers: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            return False
    
    def _deplacer_fichiers_existants(self):
        """Déplace les fichiers existants vers la nouvelle structure"""
        try:
            # Déplacement des fichiers Kaggle
            if os.path.exists(self.kaggle_dir):
                kaggle_files = [f for f in os.listdir(self.kaggle_dir) if f.endswith('.csv')]
                for file in kaggle_files:
                    src = os.path.join(self.kaggle_dir, file)
                    dst = os.path.join(f'{self.data_dir}/kaggle/raw', file)
                    if not os.path.exists(dst):
                        os.rename(src, dst)
            
            # Déplacement des fichiers API
            if os.path.exists(self.raw_dir):
                api_files = [f for f in os.listdir(self.raw_dir) if f.endswith('.csv')]
                for file in api_files:
                    src = os.path.join(self.raw_dir, file)
                    dst = os.path.join(f'{self.data_dir}/api/raw', file)
                    if not os.path.exists(dst):
                        os.rename(src, dst)
                        
        except Exception as e:
            logger.warning(f"Erreur déplacement fichiers: {e}")
    
    def sauvegarder_metadata(self):
        """Sauvegarde les métadonnées de l'intégration"""
        self.metadata['end_time'] = datetime.now().isoformat()
        self.metadata['duration'] = (
            datetime.fromisoformat(self.metadata['end_time']) - 
            datetime.fromisoformat(self.metadata['start_time'])
        ).total_seconds()
        
        metadata_path = f'{self.kaggle_dir}/integration_metadata_{self.metadata["session_id"]}.json'
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Métadonnées d'intégration sauvegardées: {metadata_path}")
        
        return metadata_path
    
    def run_full_integration(self) -> Dict:
        """Exécute l'intégration complète du dataset Kaggle"""
        logger.info("🚀 Démarrage de l'intégration complète du dataset Kaggle")
        
        try:
            # 1. Téléchargement du dataset
            download_success = self.telecharger_dataset_kaggle()
            if not download_success:
                logger.warning("Téléchargement non réussi, continuation avec les fichiers existants")
            
            # 2. Extraction si nécessaire
            if download_success:
                extract_success = self.extraire_dataset()
                if not extract_success:
                    logger.error("Échec de l'extraction du dataset")
                    return {}
            
            # 3. Analyse de la structure
            structure_analysis = self.analyser_structure_dataset()
            
            # 4. Validation de la qualité
            quality_validation = self.valider_qualite_donnees()
            
            # 5. Fusion avec l'API NBA
            fusion_success = self.fusionner_avec_api_nba()
            
            # 6. Organisation des fichiers
            organization_success = self.organiser_fichiers()
            
            # 7. Sauvegarde des métadonnées
            metadata_path = self.sauvegarder_metadata()
            
            # Résumé de l'intégration
            summary = {
                'session_id': self.metadata['session_id'],
                'download_success': download_success,
                'structure_analysis': bool(structure_analysis),
                'quality_validation': bool(quality_validation),
                'fusion_success': fusion_success,
                'organization_success': organization_success,
                'files_processed': len(structure_analysis.get('files_found', [])),
                'errors_count': len(self.metadata['errors']),
                'metadata_file': metadata_path
            }
            
            logger.info("✅ Intégration Kaggle terminée avec succès")
            logger.info(f"📊 Résumé: {summary}")
            
            return summary
            
        except Exception as e:
            error_msg = f"Erreur critique lors de l'intégration: {e}"
            logger.error(error_msg)
            self.metadata['errors'].append(error_msg)
            self.sauvegarder_metadata()
            raise


