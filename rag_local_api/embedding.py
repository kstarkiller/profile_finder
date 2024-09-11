import chromadb
import ollama
import os

from load_documents import load_documents

# Path to the collection
if os.name == 'posix':
    collection_path = r"/home/kevin/simplon/briefs/avv-matcher/rag_local_api/collection/"
else:
    collection_path = r"C:\\Users\\k.simon\\Projet\\avv-matcher\\rag_local_api\\collection\\"

# Create a new client
client = chromadb.PersistentClient(path=collection_path)

# Embedding the documents
def embed_documents(file_path, model="llama3.1:8b"):
    '''
    Embeds the documents using the llama3.1 8B model.

    Args:
        documents (list): A list of documents to embed.

    Returns:
        chromadb.Collection: A collection of the embedded documents.
    '''
    # Create a new collection
    collection = client.get_or_create_collection(name="docs")

    documents = load_documents(file_path)

    # Vérification du type de documents
    if not isinstance(documents, list):
        raise ValueError("La fonction load_documents doit retourner une liste de chaînes de caractères.")

    # store each document in a vector database
    for i, d in enumerate(documents):
        # Convertir le document en chaîne de caractères si nécessaire
        if isinstance(d, list):
            d = ' '.join(map(str, d))
        elif not isinstance(d, str):
            d = str(d)

        response = ollama.embeddings(model=model, prompt=d)
        embedding = response["embedding"]
        collection.add(
            ids=[str(i)],
            embeddings=[embedding],
            documents=[d]
        )

    return collection

# Embedding the question
def retrieve_documents(question:str, model="llama3.1:8b"):
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
    
    # print(embedded_question)
    
    # Get the collection
    collection = client.get_or_create_collection(name="docs")

    # Query the collection for the most similar documents
    results = collection.query(
        query_embeddings=[embedded_question["embedding"]],
        )
    data = results['documents']

    return data

# data = embed_documents(r"/home/kevin/simplon/briefs/avv-matcher/rag_local_api/sources", "all-minilm:33m")
# print(data)

# data = retrieve_documents("Combien de personnes à Paris ?", "all-minilm:33m")
# print(data)