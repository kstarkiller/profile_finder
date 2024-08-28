import numpy as np

# Description: This file contains the functions to create and validate documents for indexing.
def create_documents(df, embedded_column="Embedding"):
    """
    Create a list of documents from a DataFrame.

    :param df: DataFrame containing the data
    :param embedded_column: str column name containing the embeddings
    :return: list of documents
    """

    documents = []
    for index, row in df.iterrows():
        embedding = row[embedded_column]
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
    return documents

def validate_document(doc):
    if len(doc["content_vector"]) != 3072:
        raise ValueError(f"Document {doc['id']} has incorrect vector dimension: {len(doc['content_vector'])}")
    return doc