# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Marimo notebook application for processing R15 ACC data files. The application provides a file browser interface to select and process zip files containing R15 data using the `electriflux` library.

## Key Dependencies

- **marimo**: Interactive notebook framework for Python
- **electriflux**: Custom library for processing flux data (specifically the `simple_reader` module)
- **pandas**: Data manipulation
- **numpy**: Numerical operations

## Application Structure

The application consists of a single Marimo notebook (`acc.py`) with the following workflow:
1. Import required libraries and modules
2. Present a file browser UI for directory selection
3. Process R15_ACC data from the selected directory
4. Display the processed results

## Development Commands

### Install Dependencies
```bash
poetry install
```

### Running the Application
```bash
poetry run python acc.py
```
or
```bash
poetry run marimo run acc.py
```

### Editing the Notebook
```bash
poetry run marimo edit acc.py
```

### Adding New Dependencies
```bash
poetry add <package-name>
```

### Activating the Virtual Environment
```bash
poetry shell
```

## Architecture Notes

- The application uses Marimo's cell-based architecture where each `@app.cell` decorator defines an isolated execution unit
- Data flow between cells is managed through return statements
- The `electriflux.simple_reader` module provides the core data processing functionality via `process_flux()` and `iterative_process_flux()` functions
- File selection is handled through Marimo's built-in `file_browser` UI component

## Data Processing Pipeline

1. **R15 Data Processing**:
   - Loads R15_ACC data from selected directory
   - Automatically converts columns starting with 'EA' to numeric format
   - Converts Date_Releve column to datetime format (UTC)
   - Uses `mo.stop()` to prevent execution errors before directory selection

2. **Journal des ventes Processing**:
   - Separate file picker for Excel files (.xlsx)
   - Groups data by CONTRAT → PÉRIODE → NOM_ARTICLE hierarchy
   - Aggregates numeric columns (sum) except PDS_CONTRAT (first value)
   - Handles missing file scenarios with appropriate error messages