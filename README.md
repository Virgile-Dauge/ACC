# Analyse des Données d'Autoconsommation Collective (ACC)

## 📋 Vue d'ensemble

Cette application Marimo permet d'analyser les données d'autoconsommation collective en traitant les fichiers R15 et le journal des ventes pour identifier les périodes de prix et optimiser la facturation électrique.

### Qu'est-ce que l'Autoconsommation Collective (ACC) ?

L'autoconsommation collective est un dispositif légal français qui permet à plusieurs consommateurs de partager l'électricité produite par une ou plusieurs installations de production d'énergie renouvelable. Les participants peuvent être :
- Des particuliers (résidences)
- Des entreprises  
- Des collectivités publiques

Situés dans un périmètre géographique défini, ils partagent l'électricité produite localement, réduisant ainsi leur dépendance au réseau électrique national et leurs coûts énergétiques.

## 🎯 Objectifs du Projet

Cette application analyse les données ACC pour :

1. **Traitement des données R15** : Analyse des flux électriques avec conversion automatique des colonnes d'énergie active (EA) et gestion des dates
2. **Analyse du journal des ventes** : Groupement et agrégation des données commerciales par contrat, période et article
3. **Identification des périodes de prix** : Détection automatique des changements tarifaires dans le temps
4. **Optimisation de la régularisation** : Filtrage des données sur une période sélectable pour les calculs de régularisation

## 🏗️ Architecture de l'Application

L'application utilise le framework **Marimo** avec une architecture cellulaire où chaque `@app.cell` représente une unité d'exécution isolée :

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Configuration │    │  Sélection des   │    │   Traitement    │
│   & Validation  │ -> │     Fichiers     │ -> │   des Données   │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                |
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    Analyse &    │    │   Identification │    │   Affichage     │
│   Visualisation │ <- │  des Périodes    │ <- │   & Filtrage    │
│                 │    │    de Prix       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📊 Formats de Données

### Fichiers R15_ACC

Les fichiers R15 contiennent les données de flux électriques avec :

- **Date_Releve** : Date et heure du relevé (format datetime UTC)
- **EA\*** : Colonnes d'énergie active (automatiquement converties en numérique)
- **Autoconsommation_Collective** : Indicateur ACC ('0' = début de l'ACC)

**Exemple de structure :**
```
Date_Releve                | EA_Index1 | EA_Index2 | Autoconsommation_Collective
2023-01-01 00:00:00+00:00 | 1250.5    | 890.2     | 1
2023-01-01 01:00:00+00:00 | 1251.8    | 891.1     | 0
```

### Journal des Ventes

Fichier Excel (.xlsx) contenant les données commerciales :

**Colonnes requises :**
- **CONTRAT** : Identifiant du contrat
- **CODE_ARTICLE** : Code de l'article facturé
- **PUHT** : Prix unitaire HT (utilisé pour détecter les changements)
- **DATEFACT** : Date de facturation
- **PÉRIODE** : Période de facturation
- **PDS_CONTRAT** : Puissance souscrite du contrat

**Exemple de données :**
```
CONTRAT | CODE_ARTICLE | PUHT   | DATEFACT   | PÉRIODE | PDS_CONTRAT
C12345  | ABONNEMENT  | 12.50  | 2023-01-15 | 01/2023 | 6
C12345  | ABONNEMENT  | 13.20  | 2023-02-15 | 02/2023 | 6
```

## 🔍 Algorithme d'Identification des Périodes de Prix

La fonction `identify_price_periods` utilise un algorithme optimisé basé sur les opérations vectorisées pandas :

### Principe de Fonctionnement

1. **Tri chronologique** : Les données sont triées par CONTRAT, CODE_ARTICLE et DATEFACT
2. **Détection des changements** : Utilisation de `shift(1)` pour comparer chaque prix avec le précédent
3. **Création des périodes** : Identification des dates de début/fin pour chaque période de prix stable
4. **Calcul de durée** : Calcul automatique de la durée en jours pour chaque période

### Exemple de Traitement

**Données d'entrée :**
```
CONTRAT | CODE_ARTICLE | PUHT  | DATEFACT
C001    | ABONNEMENT  | 12.00 | 2023-01-01
C001    | ABONNEMENT  | 12.00 | 2023-02-01  
C001    | ABONNEMENT  | 15.00 | 2023-03-01
C001    | ABONNEMENT  | 15.00 | 2023-04-01
```

**Périodes identifiées :**
```
CONTRAT | CODE_ARTICLE | PUHT  | date_debut | date_fin   | duree_jours
C001    | ABONNEMENT  | 12.00 | 2023-01-01 | 2023-02-28 | 59
C001    | ABONNEMENT  | 15.00 | 2023-03-01 | 2023-04-01 | 32
```

## 🛠️ Installation et Configuration

### Prérequis

- Python 3.8+
- Poetry (gestionnaire de dépendances)

### Installation

1. **Cloner le projet :**
```bash
git clone <url-du-repo>
cd ACC
```

2. **Installer les dépendances :**
```bash
poetry install
```

3. **Activer l'environnement virtuel :**
```bash
poetry shell
```

### Dépendances Principales

- **marimo** : Framework de notebooks interactifs
- **electriflux** : Bibliothèque de traitement des données de flux électriques
- **pandas** : Manipulation et analyse de données
- **pandera** : Validation et contrôle de qualité des données
- **numpy** : Calculs numériques

## 📖 Guide d'Utilisation

### 1. Lancement de l'Application

```bash
# Mode exécution
poetry run marimo run acc.py

# Mode édition (pour modifier le notebook)
poetry run marimo edit acc.py
```

### 2. Utilisation Étape par Étape

#### **Étape 1 : Sélection du Dossier R15**
- Utilisez le navigateur de fichiers pour sélectionner le dossier contenant les fichiers ZIP R15
- Chemin par défaut : `~/data/ACC`
- Les fichiers ZIP seront automatiquement traités par `electriflux`

#### **Étape 2 : Choix de la Date de Régularisation**
- Sélectionnez le mois de régularisation souhaité
- Par défaut : premier jour du mois courant
- Cette date détermine la période d'analyse (du début ACC à cette date)

#### **Étape 3 : Chargement du Journal des Ventes**
- Sélectionnez le fichier Excel (.xlsx) du journal des ventes détaillés
- Le fichier doit contenir les colonnes requises (CONTRAT, CODE_ARTICLE, PUHT, DATEFACT)

#### **Étape 4 : Analyse Automatique**
L'application génère automatiquement :
- **Données R15 filtrées** : Flux électriques sur la période sélectionnée
- **Données groupées** : Agrégation par CONTRAT → PÉRIODE → CODE_ARTICLE
- **Périodes de prix** : Identification des changements tarifaires
- **Analyses statistiques** : Variations de prix et articles impactés

### 3. Interprétation des Résultats

#### **Données R15**
- Visualisation des flux électriques avec conversion automatique des types
- Identification automatique du début de l'autoconsommation collective
- Filtrage sur la période de régularisation sélectionnée

#### **Journal des Ventes Groupé**
- Agrégation intelligente :
  - **Colonnes numériques** : Sommées (quantités, montants)
  - **PDS_CONTRAT** : Première valeur (cohérence contractuelle)
- Réduction du nombre de lignes pour simplifier l'analyse

#### **Analyse des Périodes de Prix**
- **Résumé global** : Nombre de contrats, articles et périodes
- **Articles avec changements** : Liste des articles ayant subi des variations tarifaires
- **Analyse détaillée** : Variations min/max et pourcentages de changement

## 🔧 Validation des Données

L'application utilise **Pandera** pour valider les données :

### JournalVentesModel
- Valide la structure des données du journal des ventes
- Conversion automatique des types (`coerce = True`)
- Permet les colonnes supplémentaires (`strict = False`)

### PricePeriodModel  
- Valide les périodes de prix générées
- Contrôle strict de la structure (`strict = True`)
- Validation que `duree_jours >= 1`

## 🚀 Fonctionnalités Avancées

### Gestion des Erreurs
- **Arrêt conditionnel** : Utilisation de `mo.stop()` pour éviter l'exécution sans données
- **Messages informatifs** : Affichage des statuts de chargement et erreurs
- **Validation robuste** : Gestion des fichiers manquants ou mal formatés

### Performance
- **Opérations vectorisées** : Utilisation des fonctions pandas optimisées
- **Traitement par chunks** : Gestion efficace des gros volumes de données
- **Cache intelligent** : Réutilisation des données entre cellules

### Interface Utilisateur
- **Navigation intuitive** : Chemins initiaux configurés pour faciliter la sélection
- **Feedback visuel** : Indicateurs de progression et messages de statut
- **Affichage adaptatif** : Masquage du code pour une interface épurée

## 🔄 Workflow Type

1. **Préparation** : Placer les fichiers R15 (ZIP) et le journal des ventes (Excel) dans `~/data/ACC`
2. **Configuration** : Lancer l'application et sélectionner les fichiers/dossiers
3. **Paramétrage** : Choisir la date de régularisation appropriée
4. **Traitement** : L'application traite automatiquement les données
5. **Analyse** : Examiner les résultats et identifier les optimisations possibles
6. **Export** : Utiliser les données traitées pour les processus de facturation

## 📝 Notes Techniques

- **Timezone** : Toutes les dates sont converties en UTC pour la cohérence
- **Types numériques** : Conversion automatique des colonnes EA avec gestion des erreurs
- **Mémoire** : Optimisation par copie sélective des DataFrames
- **Compatibilité** : Support des formats Excel (.xlsx, .xls)

Cette documentation couvre l'ensemble des fonctionnalités de l'application ACC. Pour toute question technique ou suggestion d'amélioration, consultez le code source ou contactez l'équipe de développement.