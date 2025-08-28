#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menu principal du DataLake NBA
Interface centralisée pour toutes les fonctionnalités du projet
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.nba_data_collector import NBADataCollector
import pandas as pd
import json
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NBADataLakeMenu:
    """Menu principal du DataLake NBA"""
    
    def __init__(self):
        self.collector = None
        self.data_dir = 'data'
        
    def afficher_menu_principal(self):
        """Affiche le menu principal"""
        print("\n" + "="*60)
        print("NBA DATALAKE - MENU PRINCIPAL")
        print("="*60)
        print("1. Collecte de données via API NBA")
        print("2. Intégration dataset Kaggle")
        print("3. Gestion de la base de données")
        print("4. Dashboard et visualisations")
        print("5. Analyse et insights")
        print("6. Configuration et paramètres")
        print("7. État du système")
        print("0. Quitter")
        print("="*60)
    
    def afficher_menu_collecte(self):
        """Menu de collecte de données"""
        while True:
            print("\n" + "="*50)
            print("COLLECTE DE DONNÉES NBA")
            print("="*50)
            print("1. Collecte complète (toutes les données)")
            print("2. Collecte joueurs uniquement")
            print("3. Collecte équipes uniquement")
            print("4. Collecte leaders actuels")
            print("5. Collecte incrémentale")
            print("6. Historique des collectes")
            print("0. Retour au menu principal")
            print("="*50)
            
            choix = input("Votre choix : ").strip()
            
            if choix == "1":
                self.collecte_complete()
            elif choix == "2":
                self.collecte_joueurs()
            elif choix == "3":
                self.collecte_equipes()
            elif choix == "4":
                self.collecte_leaders()
            elif choix == "5":
                self.collecte_incrementale()
            elif choix == "6":
                self.historique_collectes()
            elif choix == "0":
                break
            else:
                print("Choix invalide. Veuillez réessayer.")
    
    def afficher_menu_kaggle(self):
        """Menu d'intégration du dataset Kaggle"""
        while True:
            print("\n" + "="*50)
            print("INTÉGRATION DATASET KAGGLE")
            print("="*50)
            print("1. Télécharger dataset Kaggle")
            print("2. Mettre à jour dataset existant")
            print("3. Analyser structure du dataset")
            print("4. Fusionner avec données API")
            print("5. Validation des données")
            print("6. Organisation des fichiers")
            print("0. Retour au menu principal")
            print("="*50)
            
            choix = input("Votre choix : ").strip()
            
            if choix == "1":
                self.telecharger_kaggle()
            elif choix == "2":
                self.mettre_a_jour_kaggle()
            elif choix == "3":
                self.analyser_structure_kaggle()
            elif choix == "4":
                self.fusionner_donnees()
            elif choix == "5":
                self.valider_donnees()
            elif choix == "6":
                self.organiser_fichiers()
            elif choix == "0":
                break
            else:
                print("❌ Choix invalide. Veuillez réessayer.")
    
    def afficher_menu_database(self):
        """Menu de gestion de la base de données"""
        while True:
            print("\n" + "="*50)
            print("GESTION BASE DE DONNÉES")
            print("="*50)
            print("1. Créer base de données")
            print("2. Importer données")
            print("3. Requêtes et analyses")
            print("4. Statistiques base")
            print("5. Nettoyage données")
            print("6. Sauvegarde/Restauration")
            print("0. Retour au menu principal")
            print("="*50)
            
            choix = input("Votre choix : ").strip()
            
            if choix == "1":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "2":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "3":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "4":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "5":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "6":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "0":
                break
            else:
                print("❌ Choix invalide. Veuillez réessayer.")
    
    def afficher_menu_dashboard(self):
        """Menu du dashboard et visualisations"""
        while True:
            print("\n" + "="*50)
            print("DASHBOARD ET VISUALISATIONS")
            print("="*50)
            print("1. Lancer dashboard")
            print("2. Créer visualisations")
            print("3. Rapports automatisés")
            print("4. KPIs et métriques")
            print("5. Interface mobile")
            print("0. Retour au menu principal")
            print("="*50)
            
            choix = input("Votre choix : ").strip()
            
            if choix == "1":
                self.lancer_dashboard()
            elif choix == "2":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "3":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "4":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "5":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "0":
                break
            else:
                print("❌ Choix invalide. Veuillez réessayer.")
    
    def afficher_menu_analyse(self):
        """Menu d'analyse et insights"""
        while True:
            print("\n" + "="*50)
            print("ANALYSE ET INSIGHTS")
            print("="*50)
            print("1. Analyse exploratoire")
            print("2. Machine Learning")
            print("3. Prédictions")
            print("4. Découverte de patterns")
            print("5. Rapports d'analyse")
            print("0. Retour au menu principal")
            print("="*50)
            
            choix = input("Votre choix : ").strip()
            
            if choix == "1":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "2":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "3":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "4":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "5":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "0":
                break
            else:
                print("❌ Choix invalide. Veuillez réessayer.")
    
    def afficher_menu_config(self):
        """Menu de configuration"""
        while True:
            print("\n" + "="*50)
            print("CONFIGURATION ET PARAMÈTRES")
            print("="*50)
            print("1. Configuration API")
            print("2. Chemins des dossiers")
            print("3. Paramètres base de données")
            print("4. Planification des tâches")
            print("5. Limites de collecte")
            print("6. Paramètres par défaut")
            print("0. Retour au menu principal")
            print("="*50)
            
            choix = input("Votre choix : ").strip()
            
            if choix == "1":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "2":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "3":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "4":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "5":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "6":
                print("🔄 Fonctionnalité en cours de développement...")
            elif choix == "0":
                break
            else:
                print("❌ Choix invalide. Veuillez réessayer.")
    
    def collecte_complete(self):
        """Lance la collecte complète des données"""
        print("\nLancement de la collecte complète...")
        try:
            self.collector = NBADataCollector()
            summary = self.collector.run_full_collection()
            print(f"\n✅ Collecte terminée avec succès !")
            print(f"Résumé : {summary}")
        except Exception as e:
            print(f"Erreur lors de la collecte : {e}")
    
    def collecte_joueurs(self):
        """Collecte uniquement les données des joueurs"""
        print("\n👥 Collecte des données des joueurs...")
        try:
            self.collector = NBADataCollector()
            players_df = self.collector.collect_players_static()
            print(f"✅ {len(players_df)} joueurs collectés")
        except Exception as e:
            print(f"❌ Erreur : {e}")
    
    def collecte_equipes(self):
        """Collecte uniquement les données des équipes"""
        print("\n🏆 Collecte des données des équipes...")
        try:
            self.collector = NBADataCollector()
            teams_df = self.collector.collect_teams_static()
            print(f"✅ {len(teams_df)} équipes collectées")
        except Exception as e:
            print(f"❌ Erreur : {e}")
    
    def collecte_leaders(self):
        """Collecte uniquement les leaders actuels"""
        print("\nCollecte des leaders actuels...")
        try:
            self.collector = NBADataCollector()
            leaders = self.collector.collect_current_leaders()
            print(f"✅ {len(leaders)} catégories de leaders collectées")
        except Exception as e:
            print(f"❌ Erreur : {e}")
    
    def collecte_incrementale(self):
        """Collecte incrémentale des données"""
        print("Collecte incrémentale...")
        print("Fonctionnalité en cours de développement...")
    
    def historique_collectes(self):
        """Affiche l'historique des collectes"""
        print("\nHistorique des collectes :")
        metadata_dir = f"{self.data_dir}/metadata"
        if os.path.exists(metadata_dir):
            files = [f for f in os.listdir(metadata_dir) if f.endswith('.json')]
            if files:
                for file in sorted(files, reverse=True):
                    file_path = os.path.join(metadata_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        session_id = metadata.get('session_id', 'N/A')
                        duration = metadata.get('duration', 0)
                        errors = len(metadata.get('errors', []))
                        print(f"  {session_id} - {duration:.1f}s - {errors} erreurs")
                    except:
                        print(f"  {file} - Erreur de lecture")
            else:
                print("  Aucune collecte trouvée")
        else:
            print("  Aucun historique disponible")
    
    def telecharger_kaggle(self):
        """Télécharge le dataset Kaggle"""
        print("\nTéléchargement du dataset Kaggle...")
        try:
            from ingestion.kaggle_integrator import KaggleIntegrator
            integrator = KaggleIntegrator()
            success = integrator.telecharger_dataset_kaggle()
            if success:
                print("✅ Dataset Kaggle téléchargé avec succès")
            else:
                print("Téléchargement manuel requis - instructions créées")
        except Exception as e:
            print(f"❌ Erreur : {e}")
    
    def mettre_a_jour_kaggle(self):
        """Met à jour le dataset Kaggle existant"""
        print("\n🔄 Mise à jour du dataset Kaggle...")
        try:
            from ingestion.kaggle_integrator import KaggleIntegrator
            integrator = KaggleIntegrator()
            success = integrator.telecharger_dataset_kaggle(force_download=True)
            if success:
                print("✅ Dataset Kaggle mis à jour")
            else:
                print("ℹ️ Mise à jour manuelle requise")
        except Exception as e:
            print(f"❌ Erreur : {e}")
    
    def analyser_structure_kaggle(self):
        """Analyse la structure du dataset Kaggle"""
        print("\n📊 Analyse de la structure du dataset Kaggle...")
        try:
            from ingestion.kaggle_integrator import KaggleIntegrator
            integrator = KaggleIntegrator()
            analysis = integrator.analyser_structure_dataset()
            if analysis:
                print(f"✅ Analyse terminée - {len(analysis.get('files_found', []))} fichiers analysés")
                print(f"📋 Rapport sauvegardé dans data/kaggle/")
            else:
                print("ℹ️ Aucun fichier à analyser")
        except Exception as e:
            print(f"❌ Erreur : {e}")
    
    def fusionner_donnees(self):
        """Fusionne les données Kaggle avec l'API NBA"""
        print("\n🔗 Fusion des données Kaggle et API NBA...")
        try:
            from ingestion.kaggle_integrator import KaggleIntegrator
            integrator = KaggleIntegrator()
            success = integrator.fusionner_avec_api_nba()
            if success:
                print("✅ Fusion des données terminée")
                print(f"📋 Résultats sauvegardés dans data/processed/")
            else:
                print("ℹ️ Aucune fusion possible")
        except Exception as e:
            print(f"❌ Erreur : {e}")
    
    def valider_donnees(self):
        """Valide la qualité des données"""
        print("\n📋 Validation des données...")
        try:
            from ingestion.kaggle_integrator import KaggleIntegrator
            integrator = KaggleIntegrator()
            validation = integrator.valider_qualite_donnees()
            if validation:
                print(f"✅ Validation terminée - {len(validation.get('files_validated', []))} fichiers validés")
                print(f"📋 Rapport sauvegardé dans data/kaggle/")
            else:
                print("ℹ️ Aucun fichier à valider")
        except Exception as e:
            print(f"❌ Erreur : {e}")
    
    def organiser_fichiers(self):
        """Organise les fichiers de données"""
        print("\n🗂️ Organisation des fichiers...")
        try:
            from ingestion.kaggle_integrator import KaggleIntegrator
            integrator = KaggleIntegrator()
            success = integrator.organiser_fichiers()
            if success:
                print("✅ Organisation des fichiers terminée")
                print(f"📁 Nouvelle structure créée dans data/")
            else:
                print("ℹ️ Organisation non possible")
        except Exception as e:
            print(f"❌ Erreur : {e}")
    
    def lancer_dashboard(self):
        """Lance le dashboard interactif"""
        print("\n🚀 Lancement du dashboard...")
        print("🔄 Fonctionnalité en cours de développement...")
        print("📋 Prochainement : Interface Dash avec Plotly")
    
    def etat_systeme(self):
        """Affiche l'état actuel du système"""
        print("\n📋 ÉTAT DU SYSTÈME NBA DATALAKE")
        print("="*50)
        
        # Vérification des dossiers
        print("📁 Structure des dossiers :")
        for folder in ['data', 'data/raw', 'data/processed', 'data/metadata']:
            if os.path.exists(folder):
                files = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
                print(f"  ✅ {folder} : {files} fichiers")
            else:
                print(f"  ❌ {folder} : Absent")
        
        # Vérification des données collectées
        print("\n📊 Données disponibles :")
        if os.path.exists('data/raw'):
            raw_files = [f for f in os.listdir('data/raw') if f.endswith('.csv')]
            if raw_files:
                for file in raw_files:
                    file_path = os.path.join('data/raw', file)
                    size = os.path.getsize(file_path) / 1024  # KB
                    print(f"  📄 {file} : {size:.1f} KB")
            else:
                print("  Aucun fichier de données trouvé")
        
        # Vérification de l'API
        print("\n🔌 État de l'API NBA :")
        try:
            from nba_api.stats.static import players
            all_players = players.get_players()
            print(f"  ✅ API NBA : {len(all_players)} joueurs accessibles")
        except Exception as e:
            print(f"  ❌ API NBA : Erreur - {e}")
    
    def executer(self):
        """Exécute le menu principal"""
        while True:
            self.afficher_menu_principal()
            choix = input("\nVotre choix : ").strip()
            
            if choix == "1":
                self.afficher_menu_collecte()
            elif choix == "2":
                self.afficher_menu_kaggle()
            elif choix == "3":
                self.afficher_menu_database()
            elif choix == "4":
                self.afficher_menu_dashboard()
            elif choix == "5":
                self.afficher_menu_analyse()
            elif choix == "6":
                self.afficher_menu_config()
            elif choix == "7":
                self.etat_systeme()
            elif choix == "0":
                print("\n👋 Au revoir ! Merci d'avoir utilisé le NBA DataLake.")
                break
            else:
                print("❌ Choix invalide. Veuillez réessayer.")
            
            input("\nAppuyez sur Entrée pour continuer...")

def main():
    """Fonction principale"""
    print("🏀 NBA DATALAKE - DÉMARRAGE")
    print("="*50)
    
    menu = NBADataLakeMenu()
    menu.executer()

if __name__ == "__main__":
    main()
