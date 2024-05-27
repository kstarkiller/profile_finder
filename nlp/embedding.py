from haystack import Document
from haystack_integrations.components.embedders.ollama.document_embedder import OllamaDocumentEmbedder
from haystack_integrations.components.embedders.ollama.text_embedder import OllamaTextEmbedder

# Fonction pour embedder les documents
def embed_documents(documents):
    """
    Embed les documents à l'aide de Haystack.

    Args:
        documents (list): Une liste de documents.

    Returns:
        list: Une liste de tuples contenant le nom du fichier et son embedding.
    """
    document_embedder = OllamaDocumentEmbedder()
    embed_documents = [document_embedder.run([Document(content=doc)]) for doc in documents]

    # # Stocker les documents embeddés
    # with open(r'C:\Users\k.simon\Desktop\test_loads\embeded_documents.txt', 'w') as f:
    #     for doc in embed_documents:
    #         f.write(f"{doc}\n")

    return embed_documents

# Fonction pour embedder la question
def embed_question(question):
    """
    Embed la question à l'aide de Haystack.

    Args:
        question (str): La question posée.

    Returns:
        str: L'embedding de la question.
    """
    question_embedder = OllamaTextEmbedder()
    question_embedding = question_embedder.run(text=question)
    return question_embedding