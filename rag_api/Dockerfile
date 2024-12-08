# Utiliser une image officielle de Python comme image de base
FROM python:3.11.9-slim

# Installer les dépendances nécessaires pour PostgreSQL et Ollama
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le répertoire de travail
COPY requirements.txt /app/

# Installer les dépendances nécessaires
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Télécharger le modèle spaCy
RUN python -m spacy download fr_core_news_lg

# Démarrer Ollama en arrière-plan et attendre qu'il soit prêt
RUN echo '#!/bin/bash\nollama serve &\nsleep 10\nollama pull nomic-embed-text:v1.5\nexec "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Copier le reste du code de l'application dans le répertoire de travail
COPY . /app

# Exposer le port sur lequel l'application va tourner
EXPOSE 8080

# Définir les variables d'environnement
ENV MINAI_API=${MINAI_API_KEY}
ENV DB_API_HOST=${DB_API_HOST}
ENV DB_API_PORT=${DB_API_PORT}
ENV DB_API_USER=${DB_API_USER}
ENV DB_API_PASSWORD=${DB_API_PASSWORD}
ENV DB_API_NAME=${DB_API_NAME}
ENV MONGO_HOST=${MONGO_HOST}
ENV MONGO_PORT=${MONGO_PORT}
ENV MONGO_USER=${MONGO_USER}
ENV MONGO_PWD=${MONGO_PWD}
ENV MONGO_DB=${MONGO_DB}
ENV MF_HOST=${MF_HOST}
ENV MF_PORT=${MF_PORT}
ENV SECRET_KEY=${SECRET_KEY}

# Définir le point d'entrée pour lancer l'application
ENTRYPOINT ["/entrypoint.sh"]
# Définir la commande par défaut pour lancer l'application
CMD ["uvicorn", "rag_api:app", "--host", "0.0.0.0", "--port", "8080"]