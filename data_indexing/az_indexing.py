from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import pandas as pd
import os

from modules.clear_index import clear_index
from modules.create_validate_documents import create_documents, validate_document
from modules.index_documents import index_documents

# Paths according to the OS
if os.name == 'posix':
    embedded_data_path = "data_processing/datas/embedded/embedded_datas.csv"
else:
    embedded_data_path = r"C:\Users\k.simon\Projet\avv-matcher\data_processing\datas\embedded\embedded_datas.csv"

search_service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
search_service_api_key =  os.environ.get("AZURE_SEARCH_API_KEY")  

# Check if the credentials are correctly loaded
if not search_service_endpoint or not search_service_api_key:
    raise ValueError("Both AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY environment variables must be set.")

credential = AzureKeyCredential(search_service_api_key)
search_client = SearchClient(endpoint=search_service_endpoint, index_name="aiprofilesmatching-index", credential=credential)

df = pd.read_csv(embedded_data_path)

clear_index(search_client)
create_documents(df)
documents = [validate_document(doc) for doc in create_documents(df)]
index_documents(search_client, documents)