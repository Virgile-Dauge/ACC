@echo off
echo Arrêt de l'application ACC...

REM Se placer dans le dossier docker
cd /d "%~dp0"

docker-compose down

if %errorlevel% equ 0 (
    echo [OK] Application arrêtée avec succès.
) else (
    echo [ERREUR] Problème lors de l'arrêt de l'application.
)

pause