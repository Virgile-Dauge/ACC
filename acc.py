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
    return Path, mo, process_flux


@app.cell(hide_code=True)
def _(Path, mo):
    folder_picker = mo.ui.file_browser(
        initial_path=Path('~/data/').expanduser(),
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
    
    return r15


@app.cell(hide_code=True)
def _(mo):
    journal_picker = mo.ui.file_browser(
        initial_path="~/",
        selection_mode="file",
        restrict_navigation=False,
        label="Sélectionnez le fichier Journal des ventes détaillés (.xlsx)",
        filetypes=[".xlsx", ".xls"]
    )
    return journal_picker


@app.cell(hide_code=True)
def _(journal_picker):
    journal_picker
    return


@app.cell
def _(journal_picker, mo, pd):
    mo.stop(not journal_picker.value, mo.md("⚠️ **Veuillez sélectionner le fichier Journal des ventes détaillés**"))
    
    # Charger le fichier Excel sélectionné
    journal_ventes = pd.read_excel(journal_picker.value[0].path)
    
    mo.md(f"✅ **Fichier chargé:** {journal_picker.value[0].name}")
    
    return journal_ventes


@app.cell
def _(journal_ventes, mo):
    mo.stop(journal_ventes is None, mo.md("⚠️ **En attente du chargement du journal des ventes**"))
    
    # Grouper et sommer par CONTRAT, PÉRIODE et NOM_ARTICLE
    # Colonnes de groupby
    groupby_cols = ['CONTRAT', 'PÉRIODE', 'NOM_ARTICLE']
    
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
    
    return journal_grouped


if __name__ == "__main__":
    app.run()
