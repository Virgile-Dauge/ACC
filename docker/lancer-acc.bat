@echo off
echo ========================================
echo    ACC - Analyse Contrats et Consommations
echo ========================================
echo.

REM Vérifier si Docker est installé
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Docker n'est pas installé ou n'est pas dans le PATH.
    echo Veuillez installer Docker Desktop depuis https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

REM Vérifier si Docker est en cours d'exécution
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Docker n'est pas en cours d'exécution.
    echo Veuillez démarrer Docker Desktop.
    pause
    exit /b 1
)

echo [INFO] Démarrage de l'application ACC...
echo.

REM Se placer dans le dossier docker
cd /d "%~dp0"

REM Vérifier le paramètre dossier
if "%~1"=="" (
    REM Utiliser dossier par défaut si aucun paramètre
    if not exist "..\data" mkdir "..\data"
    set DATA_PATH=%cd%\..\data
    echo [INFO] Aucun dossier spécifié. Utilisation du dossier par défaut: %DATA_PATH%
    echo [INFO] Usage: lancer-acc.bat "C:\chemin\vers\mes\donnees"
) else (
    if not exist "%~1" (
        echo [ERREUR] Le dossier '%~1' n'existe pas.
        pause
        exit /b 1
    )
    set DATA_PATH=%~1
    echo [INFO] Utilisation du dossier: %DATA_PATH%
)

set HOME_DATA_PATH=%TEMP%\acc-home
if not exist "%HOME_DATA_PATH%" mkdir "%HOME_DATA_PATH%"

REM Arrêter proprement toute instance existante
echo [INFO] Nettoyage des conteneurs existants...
docker-compose down --remove-orphans >nul 2>&1

REM Démarrer l'application
docker-compose up -d --build

if %errorlevel% equ 0 (
    echo.
    echo [OK] Application démarrée avec succès !
    echo.
    echo Ouverture du navigateur dans 5 secondes...
    timeout /t 5 /nobreak >nul
    start http://localhost:8000
    echo.
    echo Pour arrêter l'application, exécutez : arreter-acc.bat
) else (
    echo.
    echo [ERREUR] Impossible de démarrer l'application.
    echo Vérifiez les logs avec : docker-compose logs
)

pause