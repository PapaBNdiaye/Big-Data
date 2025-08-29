# NBA DataLake - Organisation du Projet

## 📁 Structure du Projet

```
tp_group/
├── .gitignore                 # Fichiers à ignorer par Git
├── config.py                  # Configuration centralisée
├── requirements.txt           # Dépendances Python
├── README.md                  # Documentation principale
├── src/                       # Code source
│   ├── main.py               # Point d'entrée principal
│   └── ingestion/            # Modules de collecte de données
│       ├── nba_data_collector.py
│       └── kaggle_integrator.py
├── data/                      # Données du projet (ignorées par Git)
│   ├── raw/                  # Données brutes
│   │   ├── api_nba/         # Données NBA API
│   │   └── kaggle/          # Dataset Kaggle
│   ├── processed/            # Données traitées
│   ├── insight/              # Analyses et visualisations
│   ├── persistence/          # Stockage et base de données
│   └── metadata/             # Métadonnées et index
├── docs/                     # Documentation
│   └── ORGANISATION_PROJET.md
└── venv/                     # Environnement virtuel (ignoré par Git)
```

## Principes d'Organisation

### **1. Séparation des Responsabilités**
- **`src/`** : Code source et logique métier
- **`data/`** : Données et métadonnées
- **`docs/`** : Documentation et guides
- **`config.py`** : Configuration centralisée

### **2. Gestion Git Intelligente**
- **`.gitignore`** : Exclut les données volumineuses et sensibles
- **Code source** : Versionné et partagé
- **Données** : Locales uniquement, pas de versioning
- **Configuration** : Modèles fournis, valeurs sensibles via variables d'environnement

### **3. Architecture DataLake**
- **Ingestion** : Collecte depuis API NBA et Kaggle
- **Persistence** : Stockage structuré des données
- **Insight** : Analyse et visualisation
- **Métadonnées** : Traçabilité et index des données

## Configuration

### **Fichier `config.py`**
- **Chemins** : Définition centralisée des dossiers
- **API NBA** : Paramètres de collecte et limites
- **Kaggle** : Configuration du dataset
- **Base de données** : Paramètres de connexion
- **Logs** : Configuration du système de logging

### **Variables d'Environnement**
```bash
# Base de données
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD=your_password

# API Keys (si nécessaire)
NBA_API_KEY=your_key
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_key
```

## Gestion des Données

### **Données Ignorées par Git**
- **`data/raw/`** : Données brutes (CSV, JSON, SQLite)
- **`data/processed/`** : Données traitées
- **`data/insight/`** : Rapports et analyses
- **`*.log`** : Fichiers de logs
- **`venv/`** : Environnement virtuel

### **Données Versionnées**
- **Code source** : Classes et fonctions
- **Configuration** : Paramètres et structure
- **Documentation** : Guides et explications
- **Métadonnées** : Index et descriptions

## Workflow de Développement

### **1. Configuration Initiale**
```bash
# Cloner le projet
git clone <repository>
cd tp_group

# Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Créer la structure des dossiers
python config.py
```

### **2. Collecte de Données**
```bash
# Lancer le menu principal
python src/main.py

# Option 1 : Collecte NBA API
# Option 2 : Intégration Kaggle
```

### **3. Développement**
- **Nouveaux modules** : Ajouter dans `src/`
- **Configuration** : Modifier `config.py`
- **Documentation** : Mettre à jour `docs/`

## 📝 Bonnes Pratiques

### **Code**
- **Commentaires en français** : Pour la compréhension
- **Pas d'emojis** : Style professionnel
- **Gestion d'erreurs** : Logging et exceptions
- **Tests** : Validation des fonctionnalités

### **Données**
- **Métadonnées** : Traçabilité complète
- **Validation** : Vérification de la qualité
- **Backup** : Sauvegarde des données importantes
- **Nettoyage** : Suppression des doublons

### **Git**
- **Commits réguliers** : Progression claire
- **Messages descriptifs** : Explication des changements
- **Branches** : Développement de fonctionnalités
- **Pull requests** : Revue de code

## 🔍 Maintenance

### **Nettoyage Régulier**
- **Cache Python** : Supprimer `__pycache__/`
- **Logs anciens** : Rotation automatique
- **Données temporaires** : Nettoyage périodique
- **Dépendances** : Mise à jour des packages

### **Monitoring**
- **Taille des données** : Surveillance de l'espace
- **Performance** : Temps de collecte et traitement
- **Erreurs** : Analyse des logs
- **Qualité** : Validation des données

## Ressources

- **README.md** : Vue d'ensemble du projet
- **`docs/`** : Documentation détaillée
- **`config.py`** : Configuration et paramètres
- **Logs** : Historique des opérations
- **Métadonnées** : Index et descriptions des données
