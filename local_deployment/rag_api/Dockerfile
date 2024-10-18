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

# Démarrer Ollama en arrière-plan et attendre qu'il soit prêt
RUN echo '#!/bin/bash\nollama serve &\nsleep 10\nollama pull nomic-embed-text:latest\nollama pull llama3.1:8b\nexec "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Copier le reste du code de l'application dans le répertoire de travail
COPY . /app

# Exposer le port sur lequel l'application va tourner
EXPOSE 8080

# Définir les arguments
ARG DB_USER
ARG DB_PASSWORD
ARG DB_NAME
ARG RAG_LOCAL_USER
ARG RAG_LOCAL_PASSWORD
ARG MINAI_API_KEY

# Définir les variables d'environnement
ENV DB_USER=$DB_USER
ENV DB_PASSWORD=$DB_PASSWORD
ENV DB_NAME=$DB_NAME
ENV RAG_LOCAL_USER=$RAG_LOCAL_USER
ENV RAG_LOCAL_PASSWORD=$RAG_LOCAL_PASSWORD
ENV MINAI_API=$MINAI_API_KEY

# Définir le point d'entrée pour lancer l'application
ENTRYPOINT ["/entrypoint.sh"]
# Définir la commande par défaut pour lancer l'application
CMD ["uvicorn", "rag_api:app", "--host", "0.0.0.0", "--port", "8080"]