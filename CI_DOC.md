# Documentation Docker Compose et CI/CD pour le Projet AI Profile Finder

## Table des matières

- [Configuration Docker Compose](#configuration-docker-compose)
  - [Services](#services)
  - [Réseaux et Volumes](#réseaux-et-volumes)
  - [Utilisation](#utilisation)
- [Pipeline CI/CD](#pipeline-cicd)
  - [Structure du Pipeline](#structure-du-pipeline)
  - [Étapes détaillées](#étapes-détaillées)
- [Variables d'Environnement](#variables-denvironnement)

## Configuration Docker Compose

### Services

#### 1. PostgreSQL (postgres)

- **Image**: postgres:latest
- **Conteneur**: pf_postgres
- **Configuration**:
  - Variables d'environnement pour les identifiants
  - Port exposé : 5332 (hôte) -> 5432 (conteneur)
  - Healthcheck intégré
  - Volume persistant pour les données
- **Utilisation**: Base de données principale pour les données structurées

#### 2. MLflow (mlflow)

- **Image**: ghcr.io/mlflow/mlflow
- **Conteneur**: mlflow
- **Configuration**:
  - Port exposé : 5000
  - Dépend de PostgreSQL
  - Healthcheck intégré
- **Utilisation**: Gestion du cycle de vie des modèles ML

#### 3. MongoDB (mongo)

- **Image**: mongo:latest
- **Conteneur**: pf_mongo
- **Configuration**:
  - Variables d'environnement pour les identifiants
  - Port exposé : 27017
  - Healthcheck intégré
  - Volume persistant pour les données
- **Utilisation**: Base de données NoSQL pour données non/semi-structurées

#### 4. API BDD (bdd_api)

- **Image**: Construite localement
- **Conteneur**: pf_bdd_api
- **Configuration**:
  - Port exposé : 5050
  - Dépend de PostgreSQL et MongoDB
  - Limites de ressources définies
- **Utilisation**: API pour interagir avec PostgreSQL et MongoDB

#### 5. API RAG (rag_api)

- **Image**: Construite localement
- **Conteneur**: pf_api
- **Configuration**:
  - Port exposé : 8080
  - Dépend de PostgreSQL et MongoDB
  - Volume pour les modèles Ollama
  - Limites de ressources définies
- **Utilisation**: API principale pour le traitement RAG

#### 6. Frontend RAG (rag_front)

- **Image**: Construite localement
- **Conteneur**: pf_front
- **Configuration**:
  - Port exposé : 8501
  - Dépend de PostgreSQL et MongoDB
- **Utilisation**: Interface utilisateur de l'application

### Réseaux et Volumes

- **Réseau**: pf_network (bridge)
- **Volumes**:
  - postgres_data
  - ollama_models
  - mongo_data
  - mlflow-data

### Utilisation

```bash
# Démarrer les services
docker-compose up -d

# Arrêter et supprimer les conteneurs
docker-compose down

# Reconstruire et redémarrer
docker-compose up -d --build
```

## Pipeline CI/CD

### Structure du Pipeline

1. Test
2. Sécurité
3. Build
4. Déploiement

### Étapes détaillées

#### 1. Test

- Test de l'API RAG
- Test de l'API BDD

#### 2. Sécurité

- Audit des dépendances Python avec pip-audit

#### 3. Build

- Construction des images Docker
- Push vers Azure Container Registry

#### 4. Déploiement

- Déploiement sur Azure Web App

## Variables d'Environnement

### Pour Docker Compose

À définir dans un fichier `.env` ou dans l'environnement :

- DB_USER
- DB_PASSWORD
- DB_NAME
- MONGO_USER
- MONGO_PWD
- MONGO_DB
- MINAI_API_KEY
- SECRET_KEY

### Pour CI/CD

À définir dans les paramètres CI/CD de GitLab :

- DB_USER
- DB_PASSWORD
- DB_NAME
- MONGO_USER
- MONGO_PWD
- MONGO_DB
- SECRET_KEY
- AZURE_SP_ID
- AZURE_SP_SECRET
- AZURE_TENANT
- MINAI_API_KEY
