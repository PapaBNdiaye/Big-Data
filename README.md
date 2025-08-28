# NBA DataLake - Architecture et Analytics IA

## Vue d'ensemble du projet

Ce projet implémente une solution d'architecture DataLake complète pour l'analyse des données NBA, combinant des sources de données multiples et des capacités d'intelligence artificielle.

## Architecture technique

### Couche 1 : Ingestion
- **Dataset Kaggle NBA** : Données historiques structurées (30 équipes, 4800+ joueurs, 65k+ matchs)
- **API NBA officielle** : Données temps réel et mises à jour
- **Pipeline ETL** : Extraction, transformation et chargement automatisé

### Couche 2 : Persistance
- **Base de données relationnelle** : Stockage des données structurées
- **Système de métadonnées** : Gestion des informations de traçabilité
- **Indexation automatique** : Optimisation des requêtes analytiques

### Couche 3 : Insight et Analytics
- **Dashboard interactif** : Visualisations et analyses en temps réel
- **Rapports automatisés** : Génération d'insights significatifs
- **Intelligence artificielle** : Prédictions et découverte de patterns

## Méthodologie

### Approche de développement
1. **Analyse des besoins** : Identification des sources de données et cas d'usage
2. **Conception architecturale** : Définition des couches et composants
3. **Implémentation itérative** : Développement par phases avec tests continus
4. **Validation des résultats** : Comparaison avec études existantes

### Sources de données
- **Kaggle Dataset** : Données historiques NBA depuis 1946-47
- **API NBA officielle** : Statistiques temps réel et mises à jour
- **Données complémentaires** : Articles, analyses, métadonnées

### Limitations et gestion des erreurs

#### API NBA officielle
**Limitations connues :**
- **Rate limiting** : L'API limite le nombre de requêtes par minute
- **Timeouts fréquents** : Erreurs `HTTPSConnectionPool: Read timed out` communes
- **Serveurs surchargés** : Particulièrement pendant les heures de pointe
- **Protection anti-bot** : Détection des collectes massives

**Gestion des erreurs :**
- **Timeout configuré** : 30 secondes par requête
- **Délai entre requêtes** : 0.3 secondes pour éviter la surcharge
- **Collecte par lots** : Limitation à 300 joueurs actifs par session
- **Retry automatique** : Gestion des erreurs temporaires

**Recommandations :**
- Collecter pendant les heures creuses (nuit US)
- Utiliser des pauses entre les sessions de collecte
- Surveiller les logs pour identifier les patterns d'erreur
- Considérer la collecte incrémentale pour les mises à jour

#### Dataset Kaggle
- **Taille** : ~4.4 GB de données historiques
- **Mise à jour** : Manuel via Kaggle CLI
- **Fiabilité** : Excellente, pas de limitations de rate

### Technologies utilisées
- **Backend** : Python, FastAPI, SQLAlchemy
- **Base de données** : PostgreSQL
- **Frontend** : Dash, Plotly
- **IA/ML** : Scikit-learn, TensorFlow (selon besoins)

## Installation et utilisation

### Prérequis
- Python 3.8+
- PostgreSQL
- Git

### Installation
```bash
# Cloner le repository
git clone <repository-url>
cd tp_group

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration
1. Créer un fichier `.env` avec les variables d'environnement
2. Configurer la base de données PostgreSQL
3. Lancer les services d'ingestion et de dashboard

## Structure du projet

```
tp_group/
├── data/                 # Données organisées selon l'architecture DataLake
│   ├── ingestion/        # Couche d'ingestion des données
│   │   ├── api_nba/      # Données API NBA officielle (0.27 MB)
│   │   ├── kaggle/       # Dataset Kaggle basketball (4.4 GB)
│   │   ├── scraping/     # Web scraping (préparé)
│   │   └── external/     # Autres sources externes
│   ├── persistence/      # Couche de stockage et gestion
│   │   ├── raw/          # Données brutes non transformées
│   │   ├── processed/    # Données nettoyées et transformées
│   │   ├── validated/    # Données validées et qualifiées
│   │   └── archived/     # Données archivées par date
│   ├── insight/          # Couche d'analyse et visualisation
│   │   ├── analytics/    # Analyses et métriques
│   │   ├── ml_models/    # Modèles de machine learning
│   │   ├── reports/      # Rapports et visualisations
│   │   └── dashboards/   # Dashboards interactifs
│   ├── metadata_globale.json    # Métadonnées du projet
│   ├── index_donnees.json       # Inventaire des données
│   └── ORGANISATION_RESUMEE.md  # Résumé de l'organisation
├── docs/                 # Documentation et études
├── src/                  # Code source
│   ├── ingestion/        # Modules de collecte de données
│   ├── persistence/      # Modules de stockage et gestion
│   ├── insight/          # Modules d'analyse et ML
│   └── utils/            # Utilitaires communs
├── tests/                # Tests automatisés
├── requirements.txt      # Dépendances Python
└── README.md            # Ce fichier
```

## Organisation des données

### Architecture DataLake implémentée
Le projet suit une architecture DataLake en 3 couches principales :

#### 📥 Couche INGESTION
- **API NBA** : Données officielles temps réel (joueurs, équipes, statistiques)
- **Dataset Kaggle** : Données historiques complètes (1946-2023)
- **Sources externes** : Préparées pour futures intégrations

#### 💾 Couche PERSISTENCE  
- **Raw** : Données brutes non transformées
- **Processed** : Données nettoyées et transformées
- **Validated** : Données qualifiées et validées
- **Archived** : Historique et archivage par date

#### 🔍 Couche INSIGHT
- **Analytics** : Métriques et analyses
- **ML Models** : Modèles prédictifs et IA
- **Reports** : Rapports automatisés
- **Dashboards** : Visualisations interactives

### Données disponibles
- **API NBA** : 5 fichiers CSV (0.27 MB) - données actuelles
- **Kaggle** : 17 fichiers CSV + SQLite (4.4 GB) - données historiques
- **Traçabilité** : Métadonnées complètes et index des données

## Cas d'usage

### Analyse des performances
- Comparaison des statistiques joueurs
- Évolution des performances saisonnières
- Analyse des matchs et résultats

### Prédictions et insights
- Prédiction des résultats de matchs
- Identification des patterns de jeu
- Analyse des tendances historiques

### Reporting automatisé
- Rapports de performance hebdomadaires
- Analyses comparatives d'équipes
- Suivi des records et statistiques

## État actuel du projet

### ✅ Réalisé
- **Architecture DataLake** : Structure complète implémentée
- **Organisation des données** : Nettoyage et organisation terminés
- **Sources de données** : API NBA et Kaggle intégrées
- **Documentation** : Métadonnées et index créés
- **Menu principal** : Interface de gestion développée

### 🚧 En cours
- **Intégration des données** : Fusion API NBA + Kaggle
- **Couche persistence** : Base de données et stockage
- **Dashboard** : Interface de visualisation

### 📋 À venir
- **Analytics avancées** : Métriques et KPIs
- **Machine Learning** : Modèles prédictifs
- **Rapports automatisés** : Génération d'insights

## Configuration et monitoring

### Fichier de configuration
Le projet utilise `config.py` pour centraliser la configuration :
```python
NBA_API_CONFIG = {
    "timeout": 30,           # Timeout des requêtes API
    "delay": 0.3,            # Délai entre requêtes
    "max_players": 300,      # Limite de joueurs par session
    "start_year": 2000,      # Année de début des données
    "seasons": list(range(2000, 2026))  # Saisons à collecter
}
```

### Monitoring des collectes
- **Logs détaillés** : `data/ingestion.log`
- **Métadonnées des sessions** : `data/metadata/session_*.json`
- **Index des données** : `data/index_donnees.json`
- **Gestion des erreurs** : Timeouts et retry automatiques

### Bonnes pratiques
- **Collecte par lots** : Éviter la surcharge de l'API
- **Pauses entre sessions** : Respecter les limitations de rate
- **Surveillance des logs** : Identifier les patterns d'erreur
- **Backup des données** : Sauvegarde avant nouvelles collectes

## Contribution

Ce projet suit les bonnes pratiques de développement :
- Code documenté en français
- Tests automatisés
- Architecture modulaire et extensible
- Documentation technique complète
- Organisation DataLake conforme aux standards

## Licence

Projet académique - Tous droits réservés
