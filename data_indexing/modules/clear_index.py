# Description: Module to clear all documents from an Azure Cognitive Search index
def clear_index(search_client, batch_size=100):
    """
    Clear all documents from an Azure Cognitive Search index.

    :param search_client: azure.search.documents.SearchClient instance (e. g. search_client)
    :param batch_size: int, optional (e. g. 100)
    :return: None
    """

    try:
        while True:
            # Récupérer tous les IDs des documents dans l'index
            results = search_client.search("*", select="id", top=1000)
            all_ids = [doc["id"] for doc in results]
            if not all_ids:
                break  # Sortir de la boucle si aucun document n'est trouvé

            # Supprimer les documents par lots
            for i in range(0, len(all_ids), batch_size):
                batch_ids = all_ids[i : i + batch_size]
                search_client.delete_documents(
                    documents=[{"id": id} for id in batch_ids]
                )
                print(f"Batch {i//batch_size + 1}: {len(batch_ids)} documents deleted")

        print("Index cleared successfully")
    except Exception as e:
        print(f"An error occurred while clearing the index: {str(e)}")
