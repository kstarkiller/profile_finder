
# import pandas as pd
from indexing_data.embeddings import embedding_text
from processing_data.normalizing import normalize_text
import os
import requests
from requests.adapters import HTTPAdapter
import ssl
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

model = "aiprofilesmatching-text-embedding-3-large"

# # Paths according to the used OS
# if os.name == 'posix':
#     file_path = "processing_data/datas/embedded_datas.csv"
# else:
#     file_path = r"processing_data\datas\embedded_datas.csv"

# df = pd.read_csv(file_path)

search_service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
search_service_api_key =  os.environ.get("AZURE_SEARCH_API_KEY")
index_name = "aiprofilesmatching-index"

# Classe personnalisée pour désactiver la vérification SSL
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)

# Application globale de l'adaptateur SSL personnalisé à la session requests
session = requests.Session()
adapter = SSLAdapter()
session.mount("https://", adapter)

# Check if the credentials are correctly loaded
if not search_service_endpoint or not search_service_api_key:
    raise ValueError("Both AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY environment variables must be set.")

# Créez un client de recherche
credential = AzureKeyCredential(search_service_api_key)
search_client = SearchClient(endpoint=search_service_endpoint, index_name=index_name, credential=credential)


class CustomSearchClient(SearchClient):
    def __init__(self, endpoint, index_name, credential, **kwargs):
        super().__init__(endpoint, index_name, credential, **kwargs)
        self._client._client._pipeline._transport.session = session

# Assurez-vous que les variables d'environnement sont définies
search_service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
search_service_api_key = os.environ.get("AZURE_SEARCH_API_KEY")
index_name = "aiprofilesmatching-index"

if not search_service_endpoint or not search_service_api_key:
    raise ValueError("Both AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY environment variables must be set.")

# Créez un client de recherche avec désactivation SSL
credential = AzureKeyCredential(search_service_api_key)
search_client = CustomSearchClient(endpoint=search_service_endpoint, index_name=index_name, credential=credential)

def find_profiles_azure(user_input, model):
    try:
        # Normaliser l'entrée utilisateur
        user_input = normalize_text(user_input)

        # Générer l'embedding de la requête
        query_embedded = embedding_text(user_input, model)

        # Créez une requête vectorielle
        vector_query = VectorizedQuery(
            vector=query_embedded,
            k_nearest_neighbors=10,
            fields="content_vector",
            kind="vector"
        )

        # Effectuez la recherche
        results = search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=["id", "content"],
            top=10
        )

        profiles = []
        for result in results:
            profile_text = result["content"]
            profiles.append(profile_text)

        return profiles

    except Exception as e:
        print(f"An error occurred in find_profiles_azure: {e}")
        return []
