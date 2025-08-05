# ACC - Analyse des Contrats et Consommations

Application Marimo pour le traitement et l'analyse des données R15 ACC et des journaux de ventes.

## Prérequis

- Python 3.12 ou supérieur
- Poetry pour la gestion des dépendances

## Installation

### Option 1 : Installation simple avec Docker (Recommandé)

1. **Prérequis** : Installer [Docker Desktop](https://www.docker.com/products/docker-desktop/)

2. **Lancer l'application** :
   - **Windows** : Double-cliquer sur `docker/lancer-acc.bat`
   - **Linux/Mac** : Exécuter `./docker/lancer-acc.sh`

3. **Accéder à l'application** : Ouvrir http://localhost:8000 dans votre navigateur

4. **Arrêter l'application** :
   - **Windows** : Double-cliquer sur `docker/arreter-acc.bat`
   - **Linux/Mac** : Exécuter `./docker/arreter-acc.sh`

### Option 2 : Installation pour développeurs (Poetry)

1. Cloner le repository
2. Installer les dépendances avec Poetry :
   ```bash
   poetry install
   ```

## Utilisation

### Avec Docker (utilisateurs)

L'application est accessible via votre navigateur à l'adresse http://localhost:8000 après avoir lancé le script approprié.

### Avec Poetry (développeurs)

#### Lancer l'application

```bash
poetry run marimo run acc.py
```

#### Mode édition (pour modifier le notebook)

```bash
poetry run marimo edit acc.py
```

## Fonctionnalités

### 1. Traitement des données R15 ACC

- Sélection du dossier contenant les fichiers ZIP R15
- Conversion automatique des colonnes commençant par "EA" en format numérique
- Conversion de la colonne Date_Releve en format datetime (UTC)

### 2. Analyse du journal des ventes

- Chargement de fichiers Excel (.xlsx)
- Groupement hiérarchique des données :
  - Par CONTRAT
  - Par PÉRIODE
  - Par NOM_ARTICLE
- Agrégation des colonnes numériques (somme)
- Conservation de PDS_CONTRAT sans agrégation

## Structure du projet

```
ACC/
├── acc.py              # Notebook Marimo principal
├── pyproject.toml      # Configuration Poetry et dépendances
├── poetry.lock         # Versions figées des dépendances
├── docker/             # Dossier contenant tous les fichiers Docker
│   ├── Dockerfile      # Image Docker de l'application
│   ├── docker-compose.yml  # Configuration Docker Compose
│   ├── lancer-acc.bat  # Script de lancement Windows
│   ├── lancer-acc.sh   # Script de lancement Linux/Mac
│   ├── arreter-acc.bat # Script d'arrêt Windows
│   ├── arreter-acc.sh  # Script d'arrêt Linux/Mac
│   └── .env.example    # Exemple de configuration
├── CLAUDE.md           # Documentation pour Claude Code
├── README.md           # Ce fichier
└── data/               # Dossier pour les données (créé automatiquement)
```

## Organisation des données

L'application peut accéder aux fichiers dans deux emplacements :
- `/data` : Dossier local du projet (créé automatiquement)
- `~/data` : Dossier data de votre répertoire utilisateur

Placez vos fichiers R15 et journaux de ventes dans l'un de ces dossiers pour y accéder depuis l'application.

## Dépendances principales

- **marimo** : Framework de notebook interactif
- **pandas** : Manipulation des données
- **numpy** : Calculs numériques
- **electriflux** : Traitement des flux R15
- **altair** : Visualisations
- **openpyxl** : Lecture des fichiers Excel
- **pyarrow** : Format de données performant

## Développement

### Ajouter une dépendance

```bash
poetry add <nom-du-package>
```

### Activer l'environnement virtuel

```bash
poetry shell
```

## Licence

Ce projet est sous licence GPL-3.0. Voir le fichier LICENSE pour plus de détails.