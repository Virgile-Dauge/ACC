import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import pandas as pd
    import numpy as np
    from pathlib import Path
    from typing import Optional
    import datetime

    from electriflux.simple_reader import process_flux, iterative_process_flux


@app.cell(hide_code=True)
def introduction():
    mo.md(
        r"""
    # 📊 Analyse des Données d'Autoconsommation Collective (ACC)

    Bienvenue dans l'outil d'analyse des données ACC ! Cette application vous permet d'analyser les données de facturation et de flux électriques pour régulariser l'autoconsommation collective.

    ## 🎯 Objectifs de l'analyse

    - **Traitement des données R15** : Analyse des flux d'énergie, auto et alloconso
    - **Analyse du journal des ventes** : Suivi des tarifs et périodes de facturation  
    - **Identification des changements tarifaires** : Détection automatique des variations de prix
    - **Période de régularisation** : Focus sur une période spécifique d'analyse

    ## 📋 Workflow de l'analyse

    1. **Configuration** : Import des bibliothèques et fonctions utilitaires
    2. **Données R15** : Chargement et traitement des fichiers de flux électriques
    3. **Journal des ventes** : Import et analyse des données de facturation
    4. **Analyse des prix** : Identification des périodes tarifaires et changements

    Suivez les étapes ci-dessous pour réaliser votre analyse complète.
    """
    )
    return


@app.cell(hide_code=True)
def configuration_section():
    mo.md(
        r"""
    ## ⚙️ Configuration et Imports

    Cette section configure l'environnement d'analyse avec tous les outils nécessaires :

    ### 📚 Bibliothèques importées
    - **Marimo** : Framework interactif pour les notebooks Python
    - **Pandas & Numpy** : Manipulation et analyse de données  
    - **Pandera** : Validation des schémas de données
    - **Electriflux** : Traitement spécialisé des fichiers de flux électriques

    ### 🔧 Fonctions utilitaires
    - Modèles de validation Pandera pour garantir la qualité des données
    - Algorithme d'identification automatique des périodes de prix
    - Gestion robuste des erreurs et types de données

    La configuration est maintenant prête pour le traitement de vos données ACC.
    """
    )
    return


@app.function(hide_code=True)
def identify_price_periods(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifie les périodes de prix distinctes pour chaque combinaison CONTRAT-CODE_ARTICLE.

    Cette fonction analyse les changements de prix unitaire HT (PUHT) dans le temps pour
    chaque combinaison contrat-article et crée des périodes tarifaires cohérentes. Elle
    utilise des opérations vectorisées pandas pour une performance optimale.

    Algorithme :
    1. Tri chronologique des données par CONTRAT, CODE_ARTICLE, DATEFACT
    2. Groupement par combinaison CONTRAT-CODE_ARTICLE
    3. Détection des changements de prix avec pandas.shift(1)
    4. Identification des points de rupture tarifaire
    5. Calcul des dates de début/fin et durées pour chaque période

    Args:
        df (pd.DataFrame): DataFrame contenant les colonnes :
            - CONTRAT (str) : Identifiant unique du contrat
            - CODE_ARTICLE (str) : Code de l'article facturé
            - PUHT (float) : Prix unitaire hors taxe
            - DATEFACT (pd.Timestamp) : Date de facturation

    Returns:
        pd.DataFrame: DataFrame contenant les périodes de prix avec :
            - CONTRAT (str) : Identifiant du contrat
            - CODE_ARTICLE (str) : Code de l'article
            - PUHT (float) : Prix unitaire de la période
            - date_debut (pd.Timestamp) : Date de début de la période
            - date_fin (pd.Timestamp) : Date de fin de la période
            - duree_jours (int) : Durée de la période en jours (≥ 1)

    Examples:
        >>> # Données d'entrée avec changement de prix
        >>> data = pd.DataFrame({
        ...     'CONTRAT': ['C001', 'C001', 'C001'],
        ...     'CODE_ARTICLE': ['ABONNEMENT', 'ABONNEMENT', 'ABONNEMENT'], 
        ...     'PUHT': [12.0, 12.0, 15.0],
        ...     'DATEFACT': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01'])
        ... })
        >>> periods = identify_price_periods(data)
        >>> len(periods)
        2
        >>> periods.iloc[0]['duree_jours']  # Première période
        59
        >>> periods.iloc[1]['PUHT']  # Nouveau prix
        15.0

        >>> # Données vides
        >>> empty_df = pd.DataFrame(columns=['CONTRAT', 'CODE_ARTICLE', 'PUHT', 'DATEFACT'])
        >>> result = identify_price_periods(empty_df)
        >>> result.empty
        True

    Note:
        - Les périodes sont calculées de manière inclusive (date_fin incluse)
        - Pour la dernière période d'un groupe, date_fin = dernière DATEFACT du groupe
        - Les données sont automatiquement triées par ordre chronologique
        - La fonction gère les DataFrames vides en retournant une structure vide valide
    """
    if df.empty:
        # Retourner un DataFrame vide avec la structure attendue
        return pd.DataFrame(columns=['CONTRAT', 'CODE_ARTICLE', 'PUHT', 'date_debut', 'date_fin', 'duree_jours'])

    # Trier par contrat, article et date pour avoir une séquence temporelle cohérente
    df_sorted = df.sort_values(['CONTRAT', 'CODE_ARTICLE', 'DATEFACT']).copy()

    # Grouper par contrat et article
    grouped = df_sorted.groupby(['CONTRAT', 'CODE_ARTICLE'])

    periods_list = []

    for (contrat, article), group in grouped:
        # Détecter les changements de prix avec shift() - opération vectorisée
        price_changes = group['PUHT'] != group['PUHT'].shift(1)
        # Le premier élément est toujours un "changement"
        price_changes.iloc[0] = True

        # Identifier les indices où il y a changement de prix
        change_indices = group[price_changes].index

        # Créer les périodes de prix
        for i, start_idx in enumerate(change_indices):
            # Date de début de la période
            date_debut = group.loc[start_idx, 'DATEFACT']
            # Prix de la période
            puht = group.loc[start_idx, 'PUHT']

            # Date de fin : dernière date du groupe ou début de la période suivante - 1 jour
            if i < len(change_indices) - 1:
                # Il y a une période suivante
                next_start_idx = change_indices[i + 1]
                date_fin = group.loc[next_start_idx, 'DATEFACT'] - pd.Timedelta(days=1)
            else:
                # Dernière période : prendre la dernière date du groupe
                date_fin = group['DATEFACT'].iloc[-1]

            # Calculer la durée en jours
            duree_jours = (date_fin - date_debut).days + 1

            periods_list.append({
                'CONTRAT': contrat,
                'CODE_ARTICLE': article, 
                'PUHT': puht,
                'date_debut': date_debut,
                'date_fin': date_fin,
                'duree_jours': duree_jours
            })

    # Créer le DataFrame résultat
    result_df = pd.DataFrame(periods_list)

    if result_df.empty:
        # Retourner un DataFrame vide avec la structure attendue
        return pd.DataFrame(columns=['CONTRAT', 'CODE_ARTICLE', 'PUHT', 'date_debut', 'date_fin', 'duree_jours'])

    return result_df


@app.cell(hide_code=True)
def donnees_r15_section():
    mo.md(
        r"""
    ## 📁 Chargement des Données R15

    Les données R15 contiennent les mesures de flux électriques pour l'autoconsommation collective. Ces fichiers ZIP contiennent les relevés détaillés de production et consommation.

    ### 🔍 Que contiennent les données R15 ?
    - **Mesures énergétiques** : Énergie active (EA) et réactive par période
    - **Horodatage** : Date et heure des relevés
    - **Identification ACC** : Flag d'autoconsommation collective
    - **Données de comptage** : Relevés détaillés par point de mesure

    ### ⚡ Traitement automatique
    - Conversion des colonnes EA en format numérique
    - Normalisation des dates en UTC  
    - Validation de la cohérence des données

    **👇 Sélectionnez le dossier contenant vos fichiers ZIP R15 :**
    """
    )
    return


@app.cell(hide_code=True)
def _():
    folder_picker = mo.ui.file_browser(
        initial_path=Path('~/data/ACC').expanduser(),
        selection_mode="directory", 
        label="Sélectionnez le dossier contenant les zip R15 à traiter"
    )
    return (folder_picker,)


@app.cell(hide_code=True)
def _(folder_picker):
    folder_picker
    return


@app.cell
def _(folder_picker):
    mo.stop(not folder_picker.value, mo.md("⚠️ **Veuillez sélectionner un dossier contenant les fichiers R15 à traiter**"))

    r15 = process_flux('R15_ACC', folder_picker.value[0].path)

    # Convertir toutes les colonnes commençant par 'EA' en numérique
    ea_columns = [col for col in r15.columns if col.startswith('EA')]
    for col in ea_columns:
        r15[col] = pd.to_numeric(r15[col], errors='coerce')

    # Convertir Date_Releve en format date
    if 'Date_Releve' in r15.columns:
        r15['Date_Releve'] = pd.to_datetime(r15['Date_Releve'], errors='coerce', utc=True)

    return (r15,)


@app.cell(hide_code=True)
def donnees_r15_display():
    mo.md(
        r"""
    ### 📊 Aperçu des Données R15 Chargées

    Les données R15 ont été chargées avec succès ! Le tableau ci-dessous présente un échantillon des données traitées :

    **Points clés :**
    - Toutes les colonnes énergétiques (EA) ont été converties en format numérique
    - Les dates sont normalisées en UTC pour éviter les problèmes de timezone
    - Les données sont prêtes pour l'analyse des flux d'autoconsommation

    **Navigation :** Utilisez les contrôles du tableau pour explorer les différentes colonnes et périodes.
    """
    )
    return


@app.cell
def _(r15):
    r15
    return


@app.cell(hide_code=True)
def debut_acc_info():
    mo.md(
        r"""
    ### 📅 Identification du Début de l'Autoconsommation Collective

    Le système identifie automatiquement la date de début de l'autoconsommation collective en analysant les données R15.

    **Comment ça fonctionne :**
    - Recherche de la première occurrence du flag `Autoconsommation_Collective = '0'`
    - Cette date marque le commencement officiel de l'ACC
    - Toutes les analyses ultérieures utiliseront cette date comme référence

    **Date de début ACC identifiée :**
    """
    )
    return


@app.cell
def _(r15):
    debut_acc = r15[r15['Autoconsommation_Collective'] == '0']['Date_Releve'].min()
    debut_acc
    return (debut_acc,)


@app.cell(hide_code=True)
def periode_regularisation_section():
    mo.md(
        r"""
    ## 🗺️ Sélection de la Période de Régularisation

    La période de régularisation définit l'intervalle temporel pour votre analyse. Cette sélection détermine :

    ### 📊 Impact sur l'analyse
    - **Filtrage des données R15** : Seules les données entre le début ACC et cette date seront analysées
    - **Scope du journal des ventes** : Les facturations hors période seront exclues
    - **Calculs tarifaires** : Les analyses de prix se concentreront sur cette période

    ### 🎯 Recommandations
    - Choisissez le dernier jour du mois pour une analyse mensuelle complète
    - Alignez avec vos cycles de facturation habituels
    - Considérez les périodes de changements tarifaires connus

    **👇 Sélectionnez votre mois de régularisation :**
    """
    )
    return


@app.cell(hide_code=True)
def _():
    # Date par défaut : premier jour du mois courant
    current_date = datetime.date.today()
    default_date = current_date.replace(day=1)

    date_regularisation_picker = mo.ui.date(
        value=default_date,
        label="Sélectionnez le mois de régularisation",
        start=datetime.date(2022, 1, 1),  # Date minimum
        stop=current_date  # Date maximum (aujourd'hui)
    )

    return (date_regularisation_picker,)


@app.cell(hide_code=True)
def _(date_regularisation_picker):
    date_regularisation_picker
    return


@app.cell
def _(date_regularisation_picker, debut_acc, r15):

    # Convertir la date de régularisation en datetime avec timezone UTC (cohérent avec les autres dates)
    date_regularisation = pd.to_datetime(date_regularisation_picker.value, utc=True)

    # Filtrer les données R15
    r15_filtered = r15[
        (r15['Date_Releve'] >= debut_acc) & 
        (r15['Date_Releve'] <= date_regularisation)
    ].copy()

    # Afficher un résumé du filtrage
    print(f"Période filtrée : de {debut_acc.date()} à {date_regularisation.date()}")
    print(f"Nombre de lignes après filtrage : {len(r15_filtered)} (sur {len(r15)} lignes totales)")

    return (date_regularisation,)


@app.cell(hide_code=True)
def journal_ventes_section():
    mo.md(
        r"""
    ## 🧾 Chargement du Journal des Ventes Détaillés

    Le journal des ventes contient l'historique complet des facturations pour vos contrats ACC. Ces données sont essentielles pour :

    ### 💰 Contenu du journal des ventes
    - **Informations contractuelles** : Identifiants contrats et clients
    - **Détail des articles** : Types de prestations facturées (abonnement, consommation...)
    - **Tarification** : Prix unitaires HT (PUHT) par période
    - **Chronologie** : Dates de facturation pour l'analyse temporelle

    ### 🔄 Filtrage automatique
    Les données seront automatiquement filtrées sur la période sélectionnée (début ACC → date de régularisation).

    **👇 Sélectionnez votre fichier Excel du journal des ventes :**
    """
    )
    return


@app.cell(hide_code=True)
def _():
    journal_picker = mo.ui.file_browser(
        initial_path=Path('~/data/ACC/').expanduser(),
        selection_mode="file",
        restrict_navigation=False,
        label="Sélectionnez le fichier Journal des ventes détaillés (.xlsx)",
        filetypes=[".xlsx", ".xls"]
    )
    return (journal_picker,)


@app.cell(hide_code=True)
def _(journal_picker):
    journal_picker
    return


@app.cell
def _(date_regularisation, debut_acc, journal_picker):
    mo.stop(not journal_picker.value, mo.md("⚠️ **Veuillez sélectionner le fichier Journal des ventes détaillés**"))

    # Charger le fichier Excel sélectionné
    journal_ventes = pd.read_excel(journal_picker.value[0].path)

    # Convertir DATEFACT en format date avec UTC (même approche que R15)
    if 'DATEFACT' in journal_ventes.columns:
        journal_ventes['DATEFACT'] = pd.to_datetime(journal_ventes['DATEFACT'], errors='coerce', utc=True)

    # Validation simple des données
    validation_messages = []

    # Vérifier les colonnes essentielles
    required_cols = ['CONTRAT', 'CODE_ARTICLE', 'PUHT', 'DATEFACT']
    missing_cols = [col for col in required_cols if col not in journal_ventes.columns]
    if missing_cols:
        validation_messages.append(f"⚠️ Colonnes manquantes : {missing_cols}")

    # Vérifier les types et convertir
    try:
        journal_ventes['PUHT'] = pd.to_numeric(journal_ventes['PUHT'], errors='coerce')
        invalid_puht = journal_ventes['PUHT'].isnull().sum()
        if invalid_puht > 0:
            validation_messages.append(f"⚠️ {invalid_puht} valeurs PUHT invalides converties en NaN")
    except Exception:
        validation_messages.append("⚠️ Problème de conversion PUHT")

    # Message final de validation
    if not validation_messages:
        validation_message = "✅ **Validation réussie** : Données prêtes pour l'analyse"
    else:
        validation_message = "🔄 **Validation avec avertissements** :\n" + "\n".join(validation_messages)

    journal_ventes_validated = journal_ventes

    # Filtrer les données du journal entre debut_acc et date_regularisation
    journal_ventes_filtered = journal_ventes_validated[
        (journal_ventes_validated['DATEFACT'] >= debut_acc) & 
        (journal_ventes_validated['DATEFACT'] <= date_regularisation)
    ].copy()

    mo.md(f"""✅ **Fichier chargé:** {journal_picker.value[0].name}

    {validation_message}

    **Période filtrée:** de {debut_acc.date()} à {date_regularisation.date()}

    **Nombre de lignes:** {len(journal_ventes_filtered)} (sur {len(journal_ventes_validated)} lignes totales)""")
    journal_ventes = journal_ventes_filtered
    # Ajout col PRM
    return (journal_ventes,)


@app.cell(hide_code=True)
def journal_ventes_display():
    mo.md(
        r"""
    ### 📋 Aperçu du Journal des Ventes

    Données du journal des ventes chargées et filtrées sur votre période d'analyse.

    **Validation des données :**

    - Dates de facturation converties en UTC
    - Filtrage appliqué sur la période de régularisation  
    - Structure des données vérifiée

    **Colonnes importantes :**

    - **CONTRAT** : Identifiant unique du contrat
    - **CODE_ARTICLE** : Type de prestation (ABONNEMENT, CONSO_ENERGIE...)
    - **PUHT** : Prix unitaire hors taxe (utilisé pour détecter les changements)
    - **DATEFACT** : Date de facturation
    """
    )
    return


@app.cell
def _(journal_ventes):
    journal_ventes
    return


@app.cell(hide_code=True)
def groupement_donnees_section():
    mo.md(
        r"""
    ## 📊 Groupement et Agrégation des Données

    Cette étape consolide les données de facturation pour simplifier l'analyse. Le groupement s'effectue par :

    ### 🔄 Logique de groupement
    - **CONTRAT** : Regroupement par contrat client
    - **PÉRIODE** : Consolidation par période de facturation  
    - **CODE_ARTICLE** : Agrégation par type de prestation
    - **PUHT** : Maintien du prix unitaire pour l'analyse tarifaire

    ### 📈 Règles d'agrégation
    - **Colonnes numériques** : Somme des montants facturés
    - **PDS_CONTRAT** : Conservation de la première valeur (référence stable)
    - **Suppression des doublons** : Élimination des lignes redondantes

    Cette agrégation facilite l'identification des changements de prix et l'analyse des périodes tarifaires.
    """
    )
    return


@app.cell
def _(journal_ventes):
    mo.stop(journal_ventes is None, mo.md("⚠️ **En attente du chargement du journal des ventes**"))

    # Grouper et sommer par CONTRAT, PÉRIODE et NOM_ARTICLE
    # Colonnes de groupby
    groupby_cols = ['CONTRAT', 'PÉRIODE', 'CODE_ARTICLE', 'PUHT']

    # Colonnes numériques à sommer (exclure PDS_CONTRAT et les colonnes de groupby)
    numeric_cols = [col for col in journal_ventes.columns 
                    if journal_ventes[col].dtype in ['int64', 'float64'] 
                    and col not in ['PDS_CONTRAT'] + groupby_cols]

    # Créer le dictionnaire d'agrégation
    agg_dict = {col: 'sum' for col in numeric_cols}
    # Pour PDS_CONTRAT, prendre la première valeur (devrait être la même pour un contrat)
    if 'PDS_CONTRAT' in journal_ventes.columns:
        agg_dict['PDS_CONTRAT'] = 'first'

    journal_grouped = journal_ventes.groupby(groupby_cols).agg(agg_dict).reset_index()

    mo.md(f"✅ **Données groupées:** {len(journal_grouped)} lignes (depuis {len(journal_ventes)} lignes originales)")

    return (journal_grouped,)


@app.cell(hide_code=True)
def journal_grouped_display():
    mo.md(
        r"""
    ### 📊 Données Groupées et Consolidées

    Le journal des ventes a été agrégé avec succès ! Cette vue consolidée présente :

    **Avantages du groupement :**
    - 🎯 **Vue synthétique** : Une ligne par combinaison contrat/période/article
    - 💰 **Montants agrégés** : Somme des facturations par groupe
    - 🔍 **Simplification** : Réduction du nombre de lignes pour faciliter l'analyse
    - ⚡ **Performance** : Traitement plus rapide pour les analyses suivantes

    Ces données groupées serviront de base pour l'identification des périodes de prix et l'analyse des changements tarifaires.
    """
    )
    return


@app.cell
def _(journal_grouped):
    journal_grouped
    return


@app.cell(hide_code=True)
def analyse_prix_section():
    mo.md(
        r"""
    ## 🔍 Analyse des Périodes de Prix

    Cette section identifie automatiquement les différentes périodes tarifaires dans vos données de facturation.

    ### 🧮 Algorithme d'identification
    L'algorithme analyse chaque combinaison CONTRAT-CODE_ARTICLE pour :

    - **Détecter les changements** : Variations du prix unitaire HT (PUHT) dans le temps
    - **Créer des périodes** : Segments temporels avec tarification stable
    - **Calculer les durées** : Nombre de jours par période tarifaire
    - **Valider la cohérence** : Vérification des données avec Pandera

    ### 📊 Métriques générées
    - Nombre total de périodes identifiées
    - Articles avec changements de prix
    - Durée moyenne des périodes tarifaires
    - Répartition par contrat et type d'article

    L'analyse s'effectue sur la période filtrée (début ACC → date de régularisation).
    """
    )
    return


@app.cell
def _(journal_ventes):
    mo.stop(journal_ventes is None, mo.md("⚠️ **En attente du chargement du journal des ventes**"))

    # Préparer les données avec les colonnes requises par le modèle Pandera
    journal_for_periods = journal_ventes[['CONTRAT', 'CODE_ARTICLE', 'PUHT', 'DATEFACT']].copy()

    # Identifier les périodes de prix distinctes
    price_periods = identify_price_periods(journal_for_periods)

    # Statistiques résumées
    total_contrats = price_periods['CONTRAT'].nunique() if not price_periods.empty else 0
    total_articles = price_periods['CODE_ARTICLE'].nunique() if not price_periods.empty else 0
    total_periods = len(price_periods)

    # Analyse des changements de prix par contrat
    if not price_periods.empty:
        changes_by_contract = (price_periods.groupby(['CONTRAT', 'CODE_ARTICLE'])
                              .size()
                              .reset_index(name='nb_periodes_prix'))
        # Articles avec plus d'une période de prix (donc des changements)
        articles_with_changes = changes_by_contract[changes_by_contract['nb_periodes_prix'] > 1]
        nb_articles_changes = len(articles_with_changes)
    else:
        changes_by_contract = pd.DataFrame()
        articles_with_changes = pd.DataFrame() 
        nb_articles_changes = 0

    mo.md(f"""## 📊 Analyse des Périodes de Prix

    **Résumé global:**

    - **{total_contrats}** contrats analysés
    - **{total_articles}** articles différents  
    - **{total_periods}** périodes de prix identifiées
    - **{nb_articles_changes}** articles avec changements de prix

    Les périodes de prix ont été identifiées en détectant les changements de PUHT dans la séquence chronologique pour chaque combinaison CONTRAT-CODE_ARTICLE.
    """)

    return articles_with_changes, price_periods


@app.cell(hide_code=True)
def periodes_prix_display():
    mo.md(
        r"""
    ### 🗺️ Périodes de Prix Identifiées

    Tableau détaillé de toutes les périodes tarifaires détectées dans vos données.

    **Structure des résultats :**
    - **CONTRAT** : Identifiant du contrat concerné
    - **CODE_ARTICLE** : Type de prestation tarifée
    - **PUHT** : Prix unitaire stable durant la période
    - **date_debut** : Date de début de la période (inclusive)
    - **date_fin** : Date de fin de la période (inclusive)  
    - **duree_jours** : Durée totale en jours

    **Interprétation :**
    - Chaque ligne représente une période de prix stable
    - Les dates sont continues entre les périodes d'un même article
    - Un changement de PUHT génère une nouvelle période
    """
    )
    return


@app.cell
def _(price_periods):
    price_periods
    return


@app.cell(hide_code=True)
def changements_prix_section():
    mo.md(
        r"""
    ## 🔄 Identification des Changements Tarifaires

    Vue synthétique des articles ayant subi des modifications de prix durant la période analysée.

    ### 📈 Détection automatique
    Le système identifie les articles avec :
    - **Périodes multiples** : Plus d'une période de prix = changement détecté
    - **Stabilité tarifaire** : Une seule période = prix constant
    - **Fréquence des changements** : Nombre de périodes par article

    Cette analyse vous permet de cibler rapidement les postes tarifaires ayant évolué et nécessitant une attention particulière pour la régularisation.
    """
    )
    return


@app.cell
def _(articles_with_changes):
    # Afficher les articles avec changements de prix
    if not articles_with_changes.empty:
        mo.md("### 🔄 Articles avec Changements de Prix")
        articles_with_changes.sort_values('nb_periodes_prix', ascending=False)
    else:
        mo.md("### ✅ Aucun Changement de Prix Détecté")
    return


@app.cell(hide_code=True)
def variations_prix_section():
    mo.md(
        r"""
    ## 📊 Analyse Détaillée des Variations de Prix

    Calcul précis des écarts tarifaires pour quantifier l'impact des changements de prix.

    ### 📐 Métriques calculées
    - **Prix minimum/maximum** : Fourchette tarifaire par article
    - **Variation absolue** : Différence en euros entre prix min et max
    - **Variation relative** : Pourcentage d'évolution tarifaire
    - **Durée totale** : Nombre de jours couverts par l'analyse

    ### 🎯 Indicateurs clés
    - Articles avec les plus fortes variations
    - Impact potentiel sur la facturation
    - Tendances d'évolution tarifaire

    Ces informations sont cruciales pour évaluer l'impact financier des changements tarifaires sur vos contrats d'autoconsommation collective.
    """
    )
    return


@app.cell
def _(price_periods):
    # Analyse détaillée des changements de prix
    if not price_periods.empty:
        # Prix min/max par article
        price_analysis = (price_periods.groupby(['CONTRAT', 'CODE_ARTICLE'])
                         .agg({
                             'PUHT': ['min', 'max', 'count'],
                             'duree_jours': 'sum'
                         })
                         .round(4))

        # Aplatir les colonnes multi-niveaux
        price_analysis.columns = ['_'.join(col) for col in price_analysis.columns]
        price_analysis = price_analysis.reset_index()

        # Calculer la variation de prix
        price_analysis['variation_prix'] = price_analysis['PUHT_max'] - price_analysis['PUHT_min']
        price_analysis['variation_percent'] = (price_analysis['variation_prix'] / price_analysis['PUHT_min'] * 100).round(2)

        # Filtrer les articles avec variation de prix significative
        significant_changes = price_analysis[price_analysis['variation_prix'] > 0].sort_values('variation_percent', ascending=False)

        mo.md("### 📈 Analyse des Variations de Prix")
        significant_changes
    else:
        mo.md("### ℹ️ Aucune donnée disponible pour l'analyse des variations")
    return


@app.cell(hide_code=True)
def conclusion():
    mo.md(
        r"""
    ## 🎉 Analyse Terminée

    Félicitations ! Votre analyse des données d'autoconsommation collective est maintenant complète.

    ### 📋 Récapitulatif de l'analyse réalisée

    1. ✅ **Données R15 traitées** : Flux électriques analysés sur la période
    2. ✅ **Journal des ventes consolidé** : Facturations groupées et validées  
    3. ✅ **Périodes de prix identifiées** : Changements tarifaires détectés
    4. ✅ **Variations quantifiées** : Impact des évolutions tarifaires calculé

    ### 🚀 Prochaines étapes recommandées

    - **Validation métier** : Vérifiez la cohérence des changements détectés avec vos contrats
    - **Impact financier** : Évaluez les conséquences des variations sur la facturation
    - **Régularisation** : Utilisez ces analyses pour ajuster les facturations si nécessaire
    - **Suivi périodique** : Répétez l'analyse pour monitorer les évolutions tarifaires

    ### 💡 Points d'attention

    N'hésitez pas à explorer les différents tableaux générés pour affiner votre compréhension des données et identifier d'éventuelles anomalies ou opportunités d'optimisation tarifaire.

    **Vos données sont maintenant prêtes pour la régularisation ACC !**
    """
    )
    return


if __name__ == "__main__":
    app.run()
