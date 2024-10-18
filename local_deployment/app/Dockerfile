# Utiliser une image officielle de Python comme image de base
FROM python:3.11.9-slim

# Installer les dépendances nécessaires pour PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le répertoire de travail
COPY requirements.txt /app/

# Installer les dépendances nécessaires
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application dans le répertoire de travail
COPY . /app

# Créer un utilisateur non-root et passer à cet utilisateur
RUN useradd -m appuser
USER appuser

# Rendre le port 8501 disponible pour le monde extérieur
EXPOSE 8501

# Définir les variables d'environnement à partir des arguments de construction
ENV DB_USER ${DB_USER}
ENV DB_PASSWORD ${DB_PASSWORD}
ENV DB_NAME ${DB_NAME}
ENV HOST ${DB_HOST}
ENV PORT ${PORT}

# Lancer app.py lorsque le conteneur démarre
CMD ["streamlit", "run", "main.py"]