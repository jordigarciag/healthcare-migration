# ═══════════════════════════════════════════════════════════════
# ÉTAPE 1 : Définir l'image de base
# ═══════════════════════════════════════════════════════════════
# Image de base Python 3.11 (version "slim" = légère, sans outils inutiles)
# Cette image contient Python 3.11 déjà installé sur un système Linux minimal
FROM python:3.11-slim

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 2 : Ajouter des métadonnées (documentation)
# ═══════════════════════════════════════════════════════════════
# LABEL = étiquettes pour identifier l'image (qui l'a créée, à quoi elle sert)
# Ces informations apparaissent quand on inspecte l'image : docker inspect <image>
LABEL maintainer="jordi.garcia@datasolutech.com"
LABEL description="Healthcare Data Migration to MongoDB"

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 3 : Configurer les variables d'environnement Python
# ═══════════════════════════════════════════════════════════════
# PYTHONUNBUFFERED=1 : Affiche les logs Python en temps réel (pas de mise en cache)
# → Important pour voir les messages print() immédiatement dans Docker
ENV PYTHONUNBUFFERED=1

# PYTHONDONTWRITEBYTECODE=1 : Empêche Python de créer des fichiers .pyc (bytecode compilé)
# → Réduit la taille de l'image et évite les fichiers cache inutiles
ENV PYTHONDONTWRITEBYTECODE=1

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 4 : Définir le répertoire de travail
# ═══════════════════════════════════════════════════════════════
# WORKDIR = dossier où toutes les commandes suivantes seront exécutées
# Si /app n'existe pas, Docker le crée automatiquement
WORKDIR /app

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 5 : Copier et installer les dépendances Python
# ═══════════════════════════════════════════════════════════════
# COPY = Copie un fichier depuis ton PC vers l'image Docker
# requirements.txt (ton PC) → . (= /app dans le conteneur)
COPY requirements.txt .

# RUN = Exécute des commandes lors de la construction de l'image
# --no-cache-dir : N'utilise pas le cache pip (réduit la taille de l'image)
# --upgrade pip : Met à jour pip vers la dernière version
# && : Combine plusieurs commandes en une seule couche Docker (optimisation)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 6 : Copier le code source de l'application
# ═══════════════════════════════════════════════════════════════
# Copie le dossier scripts/ depuis ton PC vers /app/scripts/ dans le conteneur
COPY scripts/ ./scripts/

# Copie le dossier data/ depuis ton PC vers /app/data/ dans le conteneur
COPY data/ ./data/

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 7 : Créer un utilisateur non-root (SÉCURITÉ)
# ═══════════════════════════════════════════════════════════════
# useradd -m -u 1000 appuser : Crée un utilisateur "appuser" avec l'ID 1000
# -m : Crée un dossier home pour cet utilisateur
# -u 1000 : Définit l'ID utilisateur (compatible avec la plupart des systèmes)
# chown -R : Change le propriétaire de tous les fichiers dans /app
# → Par défaut, les conteneurs s'exécutent en root (risque de sécurité)
# → Ici, on crée un utilisateur standard pour limiter les privilèges
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# USER = Bascule vers l'utilisateur "appuser" pour toutes les commandes suivantes
# À partir de maintenant, le conteneur ne s'exécute plus en root
USER appuser

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 8 : Définir la commande par défaut
# ═══════════════════════════════════════════════════════════════
# CMD = Commande exécutée au démarrage du conteneur
# ["python", "scripts/migration.py"] : Lance le script de migration
# Format JSON (recommandé) : Plus robuste que la forme "shell"
CMD ["python", "scripts/migration.py"]