# Déploiement Docker pour ACC

Ce dossier contient tous les fichiers nécessaires au déploiement de l'application ACC avec Docker.

## Contenu

- `Dockerfile` : Image Docker de l'application
- `docker-compose.yml` : Configuration des services et volumes
- `lancer-acc.bat` / `lancer-acc.sh` : Scripts de démarrage
- `arreter-acc.bat` / `arreter-acc.sh` : Scripts d'arrêt
- `.dockerignore` : Fichiers à exclure du build Docker
- `.env.example` : Exemple de configuration d'environnement

## Utilisation simple

### Avec vos données (recommandé)

**Windows :**
```cmd
lancer-acc.bat "C:\Users\utilisateur\mes-donnees"
```

**Linux/Mac :**
```bash
./lancer-acc.sh /home/utilisateur/mes-donnees
```

### Sans paramètre (dossier par défaut)

**Windows :**
```cmd
lancer-acc.bat
```

**Linux/Mac :**
```bash
./lancer-acc.sh
```

### Arrêter l'application

**Windows :** Double-cliquer sur `arreter-acc.bat`  
**Linux/Mac :** `./arreter-acc.sh`

## Configuration avancée

### Variables d'environnement

Copier `.env.example` vers `.env` et ajuster selon vos besoins :

```bash
# Chemin des données locales
DATA_PATH=../data

# Chemin des données utilisateur
HOME_DATA_PATH=~/data

# Port de l'application (si 8000 est occupé)
# ACC_PORT=8001
```

### Commandes Docker utiles

```bash
# Voir les logs
docker-compose logs -f

# Reconstruire l'image
docker-compose build --no-cache

# Nettoyer les conteneurs
docker-compose down -v
```

## Dépannage

### "Docker n'est pas installé"
Installer Docker Desktop depuis https://www.docker.com/products/docker-desktop/

### "Le port 8000 est déjà utilisé"
1. Créer un fichier `.env` dans ce dossier
2. Ajouter : `ACC_PORT=8001`
3. Modifier aussi le port dans docker-compose.yml

### "Impossible d'accéder aux fichiers"
Vérifier que les dossiers de données existent et sont accessibles :
- `ACC/data/` pour les données du projet
- `~/data/` pour vos données personnelles