import sys
import os
import requests
from requests.adapters import HTTPAdapter
import ssl
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.pipeline.transport import RequestsTransport

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data_embedding.modules.embed_text import embedding_text
from data_processing.normalizing import normalize_text

model = "aiprofilesmatching-text-embedding-3-large"


# Custom class to disable SSL verification
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)


# Apply the SSL adapter to the HTTP client
session = requests.Session()
session.mount("https://", SSLAdapter())


# Custom transport class to set the session
class CustomTransport(RequestsTransport):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session


# Custom client class with SSL verification disabled
class CustomSearchClient(SearchClient):
    def __init__(self, endpoint, index_name, credential, **kwargs):
        super().__init__(endpoint, index_name, credential, **kwargs)
        self._client._client._pipeline._transport = CustomTransport()


# Define the Azure Cognitive Search client and index name from environment variables
search_service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
search_service_api_key = os.environ.get("AZURE_SEARCH_API_KEY")
index_name = "aiprofilesmatching-index"

if not search_service_endpoint or not search_service_api_key:
    raise ValueError(
        "Both AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY environment variables must be set."
    )

# Create a search client with SSL disabled
credential = AzureKeyCredential(search_service_api_key)
search_client = CustomSearchClient(
    endpoint=search_service_endpoint,
    index_name=index_name,
    credential=credential,
    session=session,
)


def find_profiles_azure(user_input: list, model: str) -> list:
    """
    Find profiles using Azure Cognitive Search.

    :param user_input: list of dict containing the user input and context (if any) as a string (e.g. [{"query": "Who's Scrum Master ?", "context": "Scrum"}])
    :param model: str (e. g. "aiprofilesmatching-text-embedding-3-large")
    :return: list of str (e. g. ["Karen is a Software engineer with 5 years of experience.", ...])
    """
    try:
        # Check if the user input is empty or too long
        if user_input[-1]["query"] == "" or len(user_input[-1]["query"]) == 0:
            return []
        elif len(user_input[-1]["query"]) >= 10000:
            return ["Input too long. Please enter a shorter input."]

        # Normalize the user input
        user_input[-1]["context"] = normalize_text(user_input[-1]["context"])

        # Generate the embedding of the user input
        query_embedded = embedding_text(user_input[-1]["query"], model)

        # Create a vectorized query
        vector_query = VectorizedQuery(
            vector=query_embedded,
            k_nearest_neighbors=20,
            fields="content_vector",
            kind="vector",
        )

        # Execute the search
        results = search_client.search(
            # search_text=user_input[-1]["query"],
            vector_queries=[vector_query],
            select=["id", "content"],
        )

        profiles = []
        for result in results:
            if isinstance(result, dict) and "content" in result:
                profile_text = result["content"]
                profiles.append(profile_text)
            else:
                print(f"Unexpected result format: {result}")

        print(f"Number of profiles found: {len(profiles)}")

        return profiles

    except Exception as e:
        print(f"An error occurred in find_profiles_azure: {e}")
        return []
