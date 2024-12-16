FROM python:3.13-slim

# Installer les dépendances nécessaires, y compris ffmpeg et ffprobe
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port utilisé par Flask
EXPOSE 5000

# Commande pour lancer l'application Flask
CMD ["python", "main.py"]
