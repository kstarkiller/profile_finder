import ollama
import chromadb

from load_documents import load_documents

# Embedding the documents
def embed_documents(file_path, model="llama3.1:8b"):
    '''
    Embeds the documents using the llama3.1 8B model.

    Args:
        documents (list): A list of documents to embed.

    Returns:
        chromadb.Collection: A collection of the embedded documents.
    '''
    client = chromadb.Client()
    collection = client.create_collection(name="docs")

    documents = load_documents(file_path)

    # store each document in a vector embedding database
    for i, d in enumerate(documents):
        response = ollama.embeddings(model=model, prompt=d)
        embedding = response["embedding"]
        collection.add(
            ids=[str(i)],
            embeddings=[embedding],
            documents=[d]
        )
    
    # Save the chromadb collection to sources
    collection.save(r"C:\Users\k.simon\Projet\avv-matcher\rag_local_api\sources\collection.json")

    return collection

# Embedding the question
def retrieve_documents(question:str, collection_path, model="llama3.1:8b"):
    '''
    Embeds the question using the llama3.1 model and queries the collection for the most similar document.

    Args:
        question (str): The question to embed.
        collection (chromadb.Collection): The collection of embedded documents.

    Returns:
        str: The most similar document to the question.
    '''
    embedded_question = ollama.embeddings(
        prompt=question,
        model=model
        )
    
    # Load the collection from sources/collection.json
    collection = chromadb.Collection.load(collection_path)

    # Query the collection for the most similar documents
    results = collection.query(
        query_embeddings=[embedded_question["embedding"]],
        n_results=10
        )
    data = results['documents'][0][0]

    return data

embed_documents(r"C:\Users\k.simon\Projet\avv-matcher\rag_local_api\sources", "llama3.1:8b")