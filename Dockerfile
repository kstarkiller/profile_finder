# Utilisez une image Python officielle comme image parente
FROM python:3.11.9-slim

# Définissez le répertoire de travail
WORKDIR /app

# Copiez le contenu du répertoire actuel dans le conteneur à /app
COPY . /app

# Installez les paquets nécessaires spécifiés dans requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Installez l'outil CLI d'Azure
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Créez un utilisateur non-root et passez à cet utilisateur
RUN useradd -m appuser
USER appuser

# Rendez le port 8080 disponible pour le monde extérieur à ce conteneur
EXPOSE 8080

# Définissez les arguments de construction
ARG AZURE_OPENAI_API_KEY
ARG AZURE_OPENAI_ENDPOINT
ARG AZURE_SEARCH_API_KEY
ARG AZURE_SEARCH_ENDPOINT

# Définissez les variables d'environnement à partir des arguments de construction
ENV AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
ENV AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
ENV AZURE_SEARCH_API_KEY=${AZURE_SEARCH_API_KEY}
ENV AZURE_SEARCH_ENDPOINT=${AZURE_SEARCH_ENDPOINT}

# Exécutez app.py lorsque le conteneur se lance
CMD ["streamlit", "run", "main.py", "--server.port=8080"]