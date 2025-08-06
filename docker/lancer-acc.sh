#!/bin/bash

echo "========================================"
echo "   ACC - Autoconsommation Collective"
echo "========================================"
echo

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "[ERREUR] Docker n'est pas installé."
    echo "Veuillez installer Docker depuis https://www.docker.com/"
    exit 1
fi

# Vérifier si Docker est en cours d'exécution
if ! docker ps &> /dev/null; then
    echo "[ERREUR] Docker n'est pas en cours d'exécution."
    echo "Veuillez démarrer Docker."
    exit 1
fi

echo "[INFO] Démarrage de l'application ACC..."
echo

# Se placer dans le dossier docker
cd "$(dirname "$0")"

# Vérifier le paramètre dossier
if [ -n "$1" ]; then
    if [ ! -d "$1" ]; then
        echo "[ERREUR] Le dossier '$1' n'existe pas."
        exit 1
    fi
    export DATA_PATH="$(realpath "$1")"
    echo "[INFO] Utilisation du dossier: $DATA_PATH"
else
    # Utiliser dossier par défaut si aucun paramètre
    export DATA_PATH="$(pwd)/../data"
    mkdir -p "$DATA_PATH"
    echo "[INFO] Aucun dossier spécifié. Utilisation du dossier par défaut: $DATA_PATH"
    echo "[INFO] Usage: ./lancer-acc.sh /chemin/vers/mes/donnees"
fi

export HOME_DATA_PATH="/tmp/acc-home"
mkdir -p "$HOME_DATA_PATH"

# Arrêter proprement toute instance existante
echo "[INFO] Nettoyage des conteneurs existants..."
docker-compose down --remove-orphans 2>/dev/null || true

# Démarrer l'application
if docker-compose up -d --build; then
    echo
    echo "[OK] Application démarrée avec succès !"
    echo
    echo "Ouverture du navigateur dans 5 secondes..."
    sleep 5
    
    # Ouvrir le navigateur selon l'OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:8000
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open http://localhost:8000 2>/dev/null || echo "Ouvrez http://localhost:8000 dans votre navigateur"
    fi
    
    echo
    echo "Pour arrêter l'application, exécutez : ./arreter-acc.sh"
else
    echo
    echo "[ERREUR] Impossible de démarrer l'application."
    echo "Vérifiez les logs avec : docker-compose logs"
    exit 1
fi