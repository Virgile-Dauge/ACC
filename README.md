# ACC - Autoconsommation Collective

Application Marimo pour le traitement et l'analyse des données R15 d'Autoconsommation Collective et des journaux de ventes.

## À propos de l'Autoconsommation Collective

L'autoconsommation collective permet à un ou plusieurs **producteurs** et un ou plusieurs **consommateurs**, proches géographiquement, de se regrouper au sein d'une personne morale pour organiser la consommation de l'électricité produite, le plus souvent d'origine photovoltaïque.

### Définition légale
> *Selon l'[article L 315-2 du Code de l'Énergie](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000043213495), les points de soutirage et d'injection doivent être situés en aval d'un même poste de transformation d'électricité de moyenne en basse tension.*

### Acteurs concernés
Le terme "collective" ne signifie pas uniquement "collectivité". Cette solution s'applique à :
- **Collectivités territoriales**
- **Entreprises**
- **Particuliers**

*Source : [EDF Collectivités](https://www.edf.fr/collectivites/le-mag/le-mag-collectivites/strategie-energetique-territoriale/autoconsommation-collective-quelle-application-pour-les-collectivites)*

### Grandeurs métier calculées

Dans le cadre des opérations d'ACC, Enedis calcule et transmet de nouvelles grandeurs pour chaque Point de Référence Mesure (PRM) participant :

#### Pour les producteurs :
- **PROD** : Production totale injectée sur le Réseau Public de Distribution
- **AUTOPROD** : Quantité affectée aux consommateurs de l'opération ACC
- **SURPLUS** : Production résiduelle après affectations aux consommateurs

#### Pour les consommateurs :
- **CONS** : Consommation totale soutirée sur le RPD
- **AUTOCONS** : Quantité issue des producteurs ACC affectée au consommateur
- **COMPLEMENT** : Électricité fournie par le fournisseur en complément de la production ACC

## Prérequis

- Python 3.12 ou supérieur
- Poetry pour la gestion des dépendances

## Installation

### Option 1 : Installation simple avec Docker (Recommandé)

1. **Prérequis** : Installer [Docker Desktop](https://www.docker.com/products/docker-desktop/)

2. **Lancer l'application avec vos données** :
   - **Windows** : `docker/lancer-acc.bat "C:\chemin\vers\vos\donnees"`
   - **Linux/Mac** : `./docker/lancer-acc.sh /chemin/vers/vos/donnees`
   
   Ou sans paramètre pour utiliser un dossier par défaut :
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

- **Chargement des données Enedis** : Sélection du dossier contenant les fichiers ZIP R15
- **Traitement automatique** : Conversion des colonnes EA (énergies actives) en format numérique
- **Gestion temporelle** : Conversion de Date_Releve en format datetime (UTC)
- **Support des grandeurs ACC** : PROD, AUTOPROD, SURPLUS, CONS, AUTOCONS, COMPLEMENT

### 2. Analyse du journal des ventes

- **Import Excel** : Chargement de fichiers Excel (.xlsx) des journaux de ventes
- **Agrégation hiérarchique** :
  - Par **CONTRAT** (opération d'autoconsommation collective)
  - Par **PÉRIODE** (temporalité de facturation)
  - Par **NOM_ARTICLE** (type de grandeur énergétique)
- **Calculs automatiques** : Agrégation des colonnes numériques (somme)
- **Préservation des données** : Conservation de PDS_CONTRAT sans agrégation

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

### Types de fichiers supportés
- **Fichiers R15** : Données ZIP fournies par Enedis contenant les relevés ACC
- **Journaux de ventes** : Fichiers Excel (.xlsx) avec les données de facturation

### Accès aux données
L'application accède aux fichiers via le dossier spécifié en paramètre du script de lancement, ou utilise un dossier par défaut si aucun chemin n'est fourni.

Organisez vos fichiers dans le dossier de votre choix et spécifiez le chemin lors du lancement.

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