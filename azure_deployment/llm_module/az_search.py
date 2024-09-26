import os
import requests
from requests.adapters import HTTPAdapter
import ssl
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.pipeline.transport import RequestsTransport

from data_embedding.modules.embed_text import embedding_text
from data_processing.normalizing import normalize_text

model = "aiprofilesmatching-text-embedding-3-large"


# Classe personnalisée pour désactiver la vérification SSL
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)


# Application globale de l'adaptateur SSL personnalisé à la session requests
session = requests.Session()
adapter = SSLAdapter()
session.mount("https://", adapter)


# Custom transport class to set the session
class CustomTransport(RequestsTransport):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session


# Classe personnalisée du client avec désactivation de la vérification SSL
class CustomSearchClient(SearchClient):
    def __init__(self, endpoint, index_name, credential, **kwargs):
        super().__init__(endpoint, index_name, credential, **kwargs)
        self._client._client._pipeline._transport = CustomTransport()


# Assurez-vous que les variables d'environnement sont définies
search_service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
search_service_api_key = os.environ.get("AZURE_SEARCH_API_KEY")
index_name = "aiprofilesmatching-index"

if not search_service_endpoint or not search_service_api_key:
    raise ValueError(
        "Both AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY environment variables must be set."
    )

# Créez un client de recherche avec désactivation SSL
credential = AzureKeyCredential(search_service_api_key)
search_client = CustomSearchClient(
    endpoint=search_service_endpoint, index_name=index_name, credential=credential
)


def find_profiles_azure(user_input, model):
    """
    Find profiles using Azure Cognitive Search.

    :param user_input: str (e. g. "Who's Karen ?")
    :param model: str (e. g. "aiprofilesmatching-text-embedding-3-large")
    :return: list of str (e. g. ["Karen is a Software engineer with 5 years of experience.", ...])
    """

    try:
        # Vérifier que l'entrée utilisateur est vide ou si il est trop long
        if user_input == "":
            return []
        elif len(user_input[-1]["query"]) >= 1000:
            return ["Input too long. Please enter a shorter input."]

        # Normaliser l'entrée utilisateur
        user_input = normalize_text(user_input[-1]["context"])

        # Générer l'embedding de la requête
        query_embedded = embedding_text(user_input, model)

        # Créez une requête vectorielle
        vector_query = VectorizedQuery(
            vector=query_embedded,
            k_nearest_neighbors=30,
            fields="content_vector",
            kind="vector",
        )

        # Effectuez la recherche
        results = search_client.search(
            search_text=user_input,
            vector_queries=[vector_query],
            select=["id", "content"],
        )

        profiles = []
        for result in results:
            profile_text = result["content"]
            profiles.append(profile_text)

        print(f"Number of profiles found: {len(profiles)}")

        return profiles

    except Exception as e:
        print(f"An error occurred in find_profiles_azure: {e}")
        return []
