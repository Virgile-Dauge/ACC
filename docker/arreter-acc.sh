#!/bin/bash

echo "Arrêt de l'application ACC..."

# Se placer dans le dossier docker
cd "$(dirname "$0")"

if docker-compose down; then
    echo "[OK] Application arrêtée avec succès."
else
    echo "[ERREUR] Problème lors de l'arrêt de l'application."
    exit 1
fi