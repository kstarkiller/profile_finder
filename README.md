# Profile Finder

## Description du projet

Profile Finder est un Chatbot qui aide les utilisateurs à trouver des membres d'équipe en fonction de leur localisation, disponibilité, compétences et certifications.  
Le projet utilise un modèle NLP pour structurer les requêtes des utilisateurs, un modèle d'embedding pour vectoriser la base de données des membres et les requêtes de l'utilisateur et enfin un modèle LLM pour fournir des réponses pertinentes.  
Les réponses du LLM sont augmentées (RAG) grâce à des données pertinentes des membres. Ces données sont trouvées et ajoutées au contexte de la requête grâce à une recherche par similarité sémantique entre la base de données des membres et la requête de l'utilisateur, tous deux vectorisés grâce au même modèle d'embedding.

Ce Chatbot peut être facilement utilisé en local grâce à votre clé d'un service IA tel que OpenAI, Perplexity, EdenAI, Phind, etc.
Mais il peut tout aussi bien être déployé entièrement sur Microsoft Azure et n'utiliser que des ressources Azure :
 - Azure OpenAI Studio et ses modèles IA (LLM et Embedding).
 - Azure AI Search pour la recherche par similarité sémantique.
 - Azure Container Registry pour le dépot de l'image Docker.
 - Azure App Service pour le déploiement et l'hébergement de l'application.

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre machine :

- [Python 3.11.9](https://www.python.org/downloads/release/python-3119/)
- [Ollama](https://ollama.com/download)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Docker](https://www.docker.com/get-started)
- [Git](https://git-scm.com/)

## Installation

1. Clonez le dépôt :

    ```bash
    git clone <URL_DU_DEPOT>
    cd profile-finder
    ```

2. Installez les dépendances pour le déploiement local :

    ```bash
    cd local_deployment
    pip install -r requirements.txt
    ```

3. Installez les dépendances pour le déploiement Azure :

    ```bash
    cd ../azure_deployment
    pip install -r requirements.txt
    ```

4. Pull les modèles depuis Ollama

    ```bash
    ollama run llama3.1
    ollama pull nomic-embed-text
    ```

## Variables d'environnement

Assurez-vous de définir les variables d'environnement suivantes sur votre machine :

```bash
export AZURE_OPENAI_API_KEY=<votre_azure_openai_api_key>
export AZURE_OPENAI_ENDPOINT=<votre_azure_openai_endpoint>
export AZURE_SEARCH_API_KEY=<votre_azure_search_api_key>
export AZURE_SEARCH_ENDPOINT=<votre_azure_search_endpoint>
export AZURE_SP_ID=<votre_azure_sp_id>
export AZURE_SP_SECRET=<votre_azure_sp_secret>
export AZURE_TENANT=<votre_azure_tenant>
export RAG_LOCAL_API_KEY=<votre_rag_local_api_key>
export RAG_LOCAL_USERNAME=<votre_username_pour_se_connecter_à_lapplication>
export RAG_LOCAL_PASSWORD=<votre_password_pour_se_connecter_à_lapplication>
export DB_USER=<votre_utilisateur_postgresql>
export DB_PASSWORD=<votre_mot_de_passe_postgresql>
```

## Commandes Docker
Ce n'est pas nécessaire mais vous pouvez également créer votre propre image Docker comme suit :

```bash
docker build --build-arg AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
             --build-arg AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
             --build-arg AZURE_SEARCH_API_KEY=$AZURE_SEARCH_API_KEY \
             --build-arg AZURE_SEARCH_ENDPOINT=$AZURE_SEARCH_ENDPOINT \
             -t your_image_name .

docker run -d -p 8080:8080 --name your_container_name your_image_name
```

## Exécution des tests
Pour exécuter les tests unitaires localement :

```bash
# Exécution des tests de l'application en local
cd profile_finder/local_deployment/rag_api
python -m unittest discover -s test_unitaires

# Exécution des tests de l'application déployée sur Azure
cd profile_finder/azure_deployment
python -m unittest discover -s tests
```

## [LOCAL] Lancement de l'application
```bash
cd profile_finder/local_deployment/rag_api
python rag_api.py

cd ../app
streamlit run main.py
```

## CI/CD GitLab
Le projet utilise GitLab CI/CD pour automatiser les tests et le déploiement. Le fichier de configuration se trouve à la racine ".gitlab-ci.yml".
Les étapes sont :
1. La vérification de potentiels secrets
2. Les tests unitaires
3. Le build de l'image Docker
4. Le déploiement sur Azure

## Structure du projet
```
profile-finder/
├── azure_deployment/
│   ├── data_embedding/
│   │   ├── az_embedding.py
│   │   └── modules/
│   │       ├── embed_text.py
│   │       └── generate_embedded_column.py
│   ├── data_indexing/
│   │   ├── az_indexing.py
│   │   └── modules/
│   │       ├── clear_index.py
│   │       ├── create_validate_documents.py
│   │       └── index_documents.py
│   ├── data_processing/
│   │   ├── create_fixtures.py
│   │   ├── get_skills.py
│   │   ├── pre_processing.py
│   │   └── datas/
│   │       ├── sources/
│   │       │   ├── descriptions_uniques.txt
│   │       │   ├── acronyms.txt
│   │       │   ├── profils_uniques.txt
│   │       │   └── professions_uniques.txt
│   │       ├── fixtures/
│   │       │   ├── fixtures_certs.csv
│   │       │   ├── fixtures_coaff.csv
│   │       │   └── fixtures_psarm.csv
│   │       ├── combined/
│   │       │   └── combined_result.csv
│   │       └── embeddeds/
│   │           └── embedded_datas.csv
│   ├── llm_module/
│   │   ├── az_processing_request.py
│   │   ├── az_search.py
│   │   └── model_precision_improvements.py
│   ├── pages/
│   │   └── chatbot.py
│   ├── tests/
│   │   ├── test_az_indexing_clear_index.py
│   │   ├── test_az_indexing_index_documents.py
│   │   ├── test_az_search_find_profile_azure.py
│   │   ├── test_embeddings_embedding_text.py
│   │   ├── test_embeddings_generate_embeddings.py
│   │   ├── test_normalizing_normalize_text.py
│   │   └── test_processing_request_process_input.py
│   ├── main.py
│   ├── styles.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── local_deployment/
│   ├── app/
│   │   ├── .streamlit/
│   │   ├── pages/
│   │   │   └── chatbot.py
│   │   ├── main.py
│   │   ├── processing_request.py
│   │   ├── response_generator.py
│   │   └── styles.py
│   └── rag_api/
│       ├── llm_module/
│       │   └── generate_response.py
│       ├── log_module/
│       │   └── custom_logging.py
│       ├── rag_module/
│       │   ├── embedding.py
│       │   └── load_documents.py
│       ├── test_unitaires/
│       │   ├── test_authenticate.py
│       │   ├── test_embedding.py
│       │   ├── test_load_documents.py
│       │   ├── test_ollama.py
│       │   └── test_perplexity.py
│       └── rag_api.py
├── .gitignore
├── .gitlab-ci.yml
└── README.md
```