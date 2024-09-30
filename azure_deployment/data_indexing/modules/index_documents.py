import time
from azure.core.exceptions import HttpResponseError


# Description: This function indexes a list of documents in batches to an Azure Cognitive Search index.
def index_documents(search_client, documents, batch_size=100, max_retries=3):
    """
    Index a list of documents in batches to an Azure Cognitive Search index.

    :param search_client: azure.search.documents.SearchClient instance (e. g. search_client)
    :param documents: list of dict (e. g. [{"id": "1", "text": "Hello world"}, ...])
    :param batch_size: int, optional (e. g. 100)
    :param max_retries: int, optional (e. g. 3)
    :return: None
    """

    original_batch_size = batch_size
    i = 0
    while i < len(documents):
        batch = documents[i : i + batch_size]
        retries = 0
        while retries < max_retries:
            try:
                results = search_client.upload_documents(documents=batch)
                print(
                    f"Batch {i//original_batch_size + 1}: {len(results)} documents indexed"
                )
                i += batch_size  # Move to the next batch
                batch_size = original_batch_size  # Reset the batch size
                break
            except HttpResponseError as e:
                if e.status_code == 413:  # Request Entity Too Large
                    print(f"Batch too large, reducing size and retrying...")
                    batch_size = max(1, batch_size // 2)
                    batch = documents[i : i + batch_size]
                retries += 1
            except Exception as e:
                print(f"Error indexing batch: {str(e)}")
                retries += 1
                time.sleep(2**retries)  # Exponential backoff
        if retries == max_retries:
            raise Exception(f"Failed to index batch after {max_retries} retries")
