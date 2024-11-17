# Documentation Docker Compose pour le Projet AI Profiles Finder

## Introduction

Cette documentation détaille la configuration Docker Compose pour le projet AI Profiles Finder. Elle décrit chaque service, ses dépendances, ses configurations et son rôle dans l'architecture globale de l'application.

## Services

### 1. PostgreSQL (postgres)

**Image**: postgres:latest  
**Conteneur**: pf_postgres

**Configuration**:
- Utilise les variables d'environnement pour le nom d'utilisateur, le mot de passe et le nom de la base de données.
- Expose le port 5432 sur le port 5332 de l'hôte.
- Utilise un healthcheck pour s'assurer que la base de données est prête.
- Stocke les données dans un volume persistant.

**Utilisation**:
Base de données principale pour stocker les données structurées du projet.

### 2. MLflow (mlflow)

**Image**: ghcr.io/mlflow/mlflow  
**Conteneur**: mlflow

**Configuration**:
- Expose le port 5000.
- Installe les dépendances nécessaires et configure MLflow pour utiliser PostgreSQL comme backend.
- Dépend du service PostgreSQL.
- Utilise un healthcheck pour vérifier que le serveur MLflow est opérationnel.

**Utilisation**:
Plateforme pour la gestion du cycle de vie des modèles de machine learning.

### 3. MongoDB (mongo)

**Image**: mongo:latest  
**Conteneur**: pf_mongo

**Configuration**:
- Utilise les variables d'environnement pour le nom d'utilisateur, le mot de passe et le nom de la base de données.
- Expose le port 27017.
- Utilise un healthcheck pour vérifier que MongoDB est opérationnel.
- Stocke les données dans un volume persistant.

**Utilisation**:
Base de données NoSQL pour stocker des données non structurées ou semi-structurées.

### 4. API BDD (bdd_api)

**Image**: Construite à partir du contexte ./bdd_api  
**Conteneur**: pf_bdd_api

**Configuration**:
- Utilise les variables d'environnement pour la connexion à PostgreSQL.
- Expose le port 5050.
- Dépend des services PostgreSQL et MongoDB.
- Limite les ressources CPU et mémoire.

**Utilisation**:
API pour interagir avec les bases de données PostgreSQL et MongoDB.

### 5. API RAG (rag_api)

**Image**: Construite à partir du contexte ./rag_api  
**Conteneur**: pf_api

**Configuration**:
- Utilise de nombreuses variables d'environnement pour la configuration.
- Expose le port 8080.
- Dépend des services PostgreSQL et MongoDB.
- Utilise un volume pour stocker les modèles Ollama.
- Limite les ressources CPU et mémoire.

**Utilisation**:
API principale pour le traitement RAG (Retrieval-Augmented Generation).

### 6. Frontend RAG (rag_front)

**Image**: Construite à partir du contexte ./app  
**Conteneur**: pf_front

**Configuration**:
- Utilise des variables d'environnement pour se connecter aux API BDD et RAG.
- Expose le port 8501.
- Dépend des services PostgreSQL et MongoDB.

**Utilisation**:
Interface utilisateur pour interagir avec l'application.

## Réseaux

Un réseau bridge nommé `pf_network` est utilisé pour connecter tous les services.

## Volumes

Plusieurs volumes persistants sont définis :
- postgres_data : Pour les données PostgreSQL
- ollama_models : Pour les modèles Ollama
- mongo_data : Pour les données MongoDB
- mlflow-data : Pour les données MLflow

## Utilisation

Pour démarrer l'ensemble des services :

```bash
docker-compose up -d
```

Pour arrêter et supprimer tous les conteneurs :

```bash
docker-compose down
```

Pour reconstruire les images et redémarrer les services :

```bash
docker-compose up -d --build
```

## Variables d'Environnement Requises

Les variables suivantes doivent être définies dans un fichier `.env` ou dans l'environnement :

- DB_USER
- DB_PASSWORD
- DB_NAME
- MONGO_USER
- MONGO_PWD
- MONGO_DB
- MINAI_API_KEY
- SECRET_KEY

________________________________________________
________________________________________________