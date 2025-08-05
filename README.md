# ACC - Analyse des Contrats et Consommations

Application Marimo pour le traitement et l'analyse des données R15 ACC et des journaux de ventes.

## Prérequis

- Python 3.12 ou supérieur
- Poetry pour la gestion des dépendances

## Installation

1. Cloner le repository
2. Installer les dépendances avec Poetry :
   ```bash
   poetry install
   ```

## Utilisation

### Lancer l'application

```bash
poetry run marimo run acc.py
```

### Mode édition (pour modifier le notebook)

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
├── acc.py          # Notebook Marimo principal
├── pyproject.toml  # Configuration Poetry et dépendances
├── poetry.lock     # Versions figées des dépendances
├── CLAUDE.md       # Documentation pour Claude Code
└── README.md       # Ce fichier
```

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