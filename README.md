# Profile Finder
**🔴 README UNDER CONTRUCTION 🔴** (Moving from gitlab to github)

## Description of the Project

Profile Finder is a chatbot designed to help users find team members based on their location, availability, skills, and certifications.
The project utilizes an NLP model to structure user queries, an embedding model to vectorize both the member database and user queries, and finally, an LLM model to provide relevant responses.
The LLM responses are augmented (RAG) with pertinent member data. This data is found and added to the query context through semantic similarity search between the member database and the user's query, both vectorized using the same embedding model.
This chatbot can be easily used locally with your key from an AI service such as OpenAI, Perplexity, EdenAI, Phind, etc.
However, it can also be fully deployed on Microsoft Azure using only Azure resources:

- Azure OpenAI Studio and its AI models (LLM and Embedding).
- Azure AI Search for semantic similarity search.
- Azure Container Registry for Docker image storage.
- Azure App Service for application deployment and hosting.

## Prerequisites

Before you begin, ensure you have the following installed on your machine

- [Python 3.11.9](https://www.python.org/downloads/release/python-3119/)
- [Ollama](https://ollama.com/download)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Docker](https://www.docker.com/get-started)
- [Git](https://git-scm.com/)

## Installation

1. Clone the repository:

    ```bash
    git clone <REPO_URL>
    cd profile-finder
    ```

2. Install dependencies for local deployment:

   ```bash
   cd local_deployment
   pip install -r requirements.txt
   ```

3. Install dependencies for Azure deployment::

   ```bash
   cd ../azure_deployment
   pip install -r requirements.txt
   ```

4. Pull models from Ollama:

   ```bash
   ollama run llama3.1
   ollama pull nomic-embed-text
   ```

## Environment Variables

Ensure you set the following environment variables on your machine:

```bash
export AZURE_OPENAI_API_KEY=<your_azure_openai_api_key>
export AZURE_OPENAI_ENDPOINT=<your_azure_openai_endpoint>
export AZURE_SEARCH_API_KEY=<your_azure_search_api_key>
export AZURE_SEARCH_ENDPOINT=<your_azure_search_endpoint>
export AZURE_SP_ID=<your_azure_sp_id>
export AZURE_SP_SECRET=<your_azure_sp_secret>
export AZURE_TENANT=<your_azure_tenant>
export RAG_LOCAL_API_KEY=<your_rag_local_api_key>
export RAG_LOCAL_USERNAME=<your_username_for_embedding>
export RAG_LOCAL_PASSWORD=<your_password_for_embedding>
export DB_USER=<your_postgresql_user>
export DB_PASSWORD=<your_postgresql_password>
```

## Docker Commands

It is not necessary, but you can also create your own Docker image as follows:

```bash
docker build --build-arg AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
             --build-arg AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
             --build-arg AZURE_SEARCH_API_KEY=$AZURE_SEARCH_API_KEY \
             --build-arg AZURE_SEARCH_ENDPOINT=$AZURE_SEARCH_ENDPOINT \
             -t your_image_name .

docker run -d -p 8080:8080 --name your_container_name your_image_name
```

## Running Tests

To run unit tests locally::

```bash
# Run local application tests
cd profile_finder/local_deployment/rag_api
python -m unittest discover -s test_unitaires

# Run Azure deployed application tests
cd profile_finder/azure_deployment
python -m unittest discover -s tests
```

## [LOCAL] Launching the Application

```bash
cd profile_finder/local_deployment/rag_api
python rag_api.py

cd ../app
streamlit run main.py
```

## CI/CD GitLab

The project uses GitLab CI/CD to automate testing and deployment. The configuration file is located at the root ".gitlab-ci.yml".
The steps are:

1. Checking for potential secrets
2. Running unit tests
3. Building the Docker image
4. Deploying on Azure

## Project Structure

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
