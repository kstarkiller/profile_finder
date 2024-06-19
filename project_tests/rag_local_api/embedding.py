import ollama
import chromadb


# Embedding the documents
def embed_documents(documents):
    """
    Embeds the documents using the mxbai-embed-large model.

    Args:
        documents (list): A list of documents to embed.

    Returns:
        chromadb.Collection: A collection of the embedded documents.
    """
    client = chromadb.Client()
    collection = client.create_collection(name="docs")

    # store each document in a vector embedding database
    for i, d in enumerate(documents):
        response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
        embedding = response["embedding"]
        collection.add(ids=[str(i)], embeddings=[embedding], documents=[d])

    return collection


# Embedding the question
def retrieve_documents(question, collection):
    """
    Embeds the question using the mxbai-embed-large model and queries the collection for the most similar document.

    Args:
        question (str): The question to embed.
        collection (chromadb.Collection): The collection of embedded documents.

    Returns:
        str: The most similar document to the question.
    """
    embedded_question = ollama.embeddings(prompt=question, model="mxbai-embed-large")
    results = collection.query(
        query_embeddings=[embedded_question["embedding"]], n_results=1
    )
    data = results["documents"][0][0]

    return data
