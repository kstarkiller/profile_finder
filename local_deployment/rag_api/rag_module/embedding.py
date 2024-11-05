import chromadb
import ollama
import os
import logging
from chromadb.config import Settings

from rag_module.load_documents import load_profile
from llm_module.model_precision_improvements import structure_query

logs_path = os.path.join(
    os.path.dirname(__file__), "..", "log_module", "logs", "logs_api.log"
)

# Logging module configuration
logging.basicConfig(
    filename=logs_path,  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)


def embed_documents(collection_path, model="nomic-embed-text:v1.5", batch_size=10):
    """
    Embeds the documents using an embedding model in batches.

    Args:
        file_path (str): The path to the file containing documents to embed.
        model (str): The model to use for embedding.
        batch_size (int): The number of documents to process in each batch.

    Returns:
        chromadb.Collection: A collection of the embedded documents.
    """
    try:
        # Connect to the client
        client = chromadb.PersistentClient(
            path=collection_path,
            settings=Settings(allow_reset=True),
        )
    except Exception as e:
        logging.error(f"Error connecting to the ChromaDB client: {e}")
        raise (f"Error connecting to the ChromaDB client: {e}")

    # Create a new collection or get existing one
    collection = client.get_or_create_collection(name="docs")

    # Load documents
    documents = load_profile()

    # Verify the type of documents
    if not isinstance(documents, list):
        logging.error("Documents must be a list of strings.")
        raise ValueError("The load_documents function must return a list of strings.")

    logging.info(f"Found {len(documents)} documents.")

    # Store documents in batches
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i : i + batch_size]
        batch_embeddings = []
        batch_ids = []
        batch_texts = []
        for j, d in enumerate(batch_docs):
            try:
                response = ollama.embeddings(model=model, prompt=d)
                embedding = response["embedding"]
                batch_embeddings.append(embedding)
                batch_ids.append(str(i + j))  # Unique ID for each document
                batch_texts.append(d)
                # logging.info(f"Document {i + j} embedded.")
            except Exception as e:
                logging.error(f"Error embedding document {i + j}: {e}")
                raise ValueError(f"Error embedding document {i + j}: {e}")

        # Add the batch to the collection
        collection.add(
            ids=batch_ids, embeddings=batch_embeddings, documents=batch_texts
        )
        logging.info(f"Batch {i // batch_size} added to the collection.")

    return collection


# Retrieve documents
def retrieve_documents(collection_path, question: str, model="nomic-embed-text:v1.5"):
    """
    Embeds the question using an embedding model and queries the collection for the most similar document.

    Args:
        question (str): The question to embed.
        model (str): The model to use for embedding.

    Returns:
        str: The most similar document to the question.
    """
    # Improve the question structure
    question = structure_query(question)

    # Create embedding client
    embedded_question = ollama.embeddings(prompt=question, model=model)

    # Connect to the ChromaDB client
    client = chromadb.PersistentClient(
        path=collection_path,
        settings=Settings(allow_reset=True),
    )

    # Get the collection
    collection = client.get_collection(name="docs")

    # Query the collection with the embedded question for the most similar documents
    results = collection.query(
        query_embeddings=[embedded_question["embedding"]], n_results=5
    )
    data = results["documents"]

    return data
