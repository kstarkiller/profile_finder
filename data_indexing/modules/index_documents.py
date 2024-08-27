import time
from azure.core.exceptions import HttpResponseError

# Description: This function indexes a list of documents in batches to an Azure Cognitive Search index.
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
            # print(f"Failed to index batch after {max_retries} retries")
            raise Exception(f"Failed to index batch after {max_retries} retries")