FROM python:3.12-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN useradd -m -u 1000 marimo

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration Poetry
COPY pyproject.toml poetry.lock ./

# Installer Poetry et les dépendances
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Copier le reste de l'application
COPY --chown=marimo:marimo . .

# Créer les répertoires pour les données
RUN mkdir -p /data /home/data && \
    chown -R marimo:marimo /data /home/data

# Changer vers l'utilisateur non-root
USER marimo

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["marimo", "run", "acc.py", "--host", "0.0.0.0", "--port", "8000", "--no-token"]