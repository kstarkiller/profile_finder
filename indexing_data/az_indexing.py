from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.core.exceptions import HttpResponseError
import time
import numpy as np
import pandas as pd
import os

# Paths according to the OS
if os.name == 'posix':
    embedded_data_path = "app/processing_data/datas/embedded_datas.csv"  
else:
    embedded_data_path = r"C:\Users\k.simon\Projet\avv-matcher\processing_data\datas\embedded_datas.csv"

search_service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
search_service_api_key =  os.environ.get("AZURE_SEARCH_API_KEY")  

# Check if the credentials are correctly loaded
if not search_service_endpoint or not search_service_api_key:
    raise ValueError("Both AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY environment variables must be set.")

credential = AzureKeyCredential(search_service_api_key)
search_client = SearchClient(endpoint=search_service_endpoint, index_name="aiprofilesmatching-index", credential=credential)

df = pd.read_csv(embedded_data_path)

documents = []
for index, row in df.iterrows():
    embedding = row["embedding"]
    if isinstance(embedding, np.ndarray):
        embedding = embedding.tolist()
    elif isinstance(embedding, str):
        embedding = [float(x) for x in embedding.strip('[]').split(',')]
    
    document = {
        "id": str(index),
        "content": row["Combined"],
        "content_vector": embedding
    }
    documents.append(document)

def validate_document(doc):
    if len(doc["content_vector"]) != 3072:
        raise ValueError(f"Document {doc['id']} has incorrect vector dimension: {len(doc['content_vector'])}")
    return doc

def index_documents(search_client, documents, batch_size=100, max_retries=3):
    original_batch_size = batch_size
    i = 0
    while i < len(documents):
        batch = documents[i:i+batch_size]
        retries = 0
        while retries < max_retries:
            try:
                results = search_client.upload_documents(documents=batch)
                print(f"Batch {i//original_batch_size + 1}: {len(results)} documents indexed")
                i += batch_size  # Avance à la prochaine batch
                batch_size = original_batch_size  # Réinitialise la taille du batch
                break
            except HttpResponseError as e:
                if e.status_code == 413:  # Request Entity Too Large
                    print(f"Batch too large, reducing size and retrying...")
                    batch_size = max(1, batch_size // 2)
                    batch = documents[i:i+batch_size]
                retries += 1
            except Exception as e:
                print(f"Error indexing batch: {str(e)}")
                retries += 1
                time.sleep(2 ** retries)  # Exponential backoff
        if retries == max_retries:
            print(f"Failed to index batch after {max_retries} retries")
            raise Exception(f"Failed to index batch after {max_retries} retries")

def clear_index(search_client, batch_size=100):
    try:
        while True:
            # Récupérer tous les IDs des documents dans l'index
            results = search_client.search("*", select="id", top=1000)
            all_ids = [doc['id'] for doc in results]
            if not all_ids:
                break  # Sortir de la boucle si aucun document n'est trouvé

            # Supprimer les documents par lots
            for i in range(0, len(all_ids), batch_size):
                batch_ids = all_ids[i:i+batch_size]
                search_client.delete_documents(documents=[{"id": id} for id in batch_ids])
                print(f"Batch {i//batch_size + 1}: {len(batch_ids)} documents deleted")

        print("Index cleared successfully")
    except Exception as e:
        print(f"An error occurred while clearing the index: {str(e)}")
