import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np

    from pathlib import Path

    from electriflux.simple_reader import process_flux, iterative_process_flux
    return mo, pd, process_flux


@app.cell(hide_code=True)
def _(mo):
    folder_picker = mo.ui.file_browser(
        selection_mode="directory", 
        label="Sélectionnez le dossier contenant les zip R15 à traiter"
    )
    return (folder_picker,)


@app.cell(hide_code=True)
def _(folder_picker):
    folder_picker
    return


@app.cell
def _(folder_picker, mo, pd, process_flux):
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


@app.cell
def _(r15):
    r15
    return


@app.cell
def _(r15):
    debut_acc = r15[r15['Autoconsommation_Collective'] == '0']['Date_Releve'].min()
    debut_acc
    return (debut_acc,)


@app.cell(hide_code=True)
def _(mo):
    # Sélecteur de date pour la régularisation (mois/année)
    import datetime

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
def _(date_regularisation_picker, debut_acc, pd, r15):
    # Filtrer les données R15 entre debut_acc et date_regularisation
    import datetime

    # Convertir la date de régularisation en datetime avec timezone UTC
    date_regularisation = pd.Timestamp(date_regularisation_picker.value).tz_localize('UTC')

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
def _(mo):
    journal_picker = mo.ui.file_browser(
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
def _(date_regularisation, debut_acc, journal_picker, mo, pd):
    mo.stop(not journal_picker.value, mo.md("⚠️ **Veuillez sélectionner le fichier Journal des ventes détaillés**"))

    # Charger le fichier Excel sélectionné
    journal_ventes = pd.read_excel(journal_picker.value[0].path)

    # Convertir Date_Releve en format date
    if 'DATEFACT' in journal_ventes.columns:
        journal_ventes['DATEFACT'] = pd.to_datetime(journal_ventes['DATEFACT'], errors='coerce', utc=True)

    # Filtrer les données du journal entre debut_acc et date_regularisation
    journal_ventes_filtered = journal_ventes[
        (journal_ventes['DATEFACT'] >= debut_acc) & 
        (journal_ventes['DATEFACT'] <= date_regularisation)
    ].copy()

    mo.md(f"""✅ **Fichier chargé:** {journal_picker.value[0].name}

    **Période filtrée:** de {debut_acc.date()} à {date_regularisation.date()}

    **Nombre de lignes:** {len(journal_ventes_filtered)} (sur {len(journal_ventes)} lignes totales)""")
    journal_ventes = journal_ventes_filtered
    # Ajout col PRM
    return (journal_ventes,)


@app.cell
def _(journal_ventes):
    journal_ventes
    return


@app.cell
def _(journal_ventes, mo):
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


@app.cell
def _(journal_grouped):
    journal_grouped
    return


if __name__ == "__main__":
    app.run()
