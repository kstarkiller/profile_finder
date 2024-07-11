from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.core.exceptions import HttpResponseError
import time
import numpy as np
import pandas as pd
import os

# Paths according to the OS
if os.name == 'posix':
    embedded_data_path = "/home/kevin/simplon/briefs/avv-matcher/processing_data/datas/embedded_datas.csv"
else:
    embedded_data_path = r"C:\Users\k.simon\Projet\avv-matcher\processing_data\datas\embedded_datas.csv"

search_service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
search_service_api_key =  os.environ.get("AZURE_SEARCH_API_KEY")

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
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        retries = 0
        while retries < max_retries:
            try:
                results = search_client.upload_documents(documents=batch)
                print(f"Batch {i//batch_size + 1}: {len(results)} documents indexed")
                break
            except HttpResponseError as e:
                if e.status_code == 413:  # Request Entity Too Large
                    print(f"Batch too large, reducing size and retrying...")
                    batch_size = batch_size // 2
                    if batch_size < 1:
                        raise Exception("Batch size cannot be reduced further")
                    batch = documents[i:i+batch_size]
                    retries += 1
                else:
                    raise
            except Exception as e:
                print(f"Error indexing batch: {str(e)}")
                retries += 1
                time.sleep(2 ** retries)  # Exponential backoff
        
        if retries == max_retries:
            print(f"Failed to index batch after {max_retries} retries")

documents = [validate_document(doc) for doc in documents]
index_documents(search_client, documents)
