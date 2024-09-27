# Profile Finder

## Commands to build an run a Docker image
```bash
docker build --build-arg AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
             --build-arg AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
             --build-arg AZURE_SEARCH_API_KEY=$AZURE_SEARCH_API_KEY \
             --build-arg AZURE_SEARCH_ENDPOINT=$AZURE_SEARCH_ENDPOINT \
             -t your_image_name .

docker run -d -p 8080:8080 --name your_container_name your_image_name
```

## Structure du projet

Voici la structure du projet:
```
profil-finder/
├── azure_deployment/
│   ├── data_embedding/
│   │   ├── az_embedding.py
│   │   └── modules
│   │       ├── embed_text.py
│   │       └── generate_embedded_column.py
│   ├── data_indexing/
│   │   ├── az_indexing.py
│   │   └── modules
│   │       ├── clear_indext.py
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
│   │   └── model_precision_improvements.pyy
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