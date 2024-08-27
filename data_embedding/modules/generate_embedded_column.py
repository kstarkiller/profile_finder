import pandas as pd

from modules.embed_text import embedding_text

# Description: Generate in a column the embeddings of a specified text column of the dataframe using the Azure OpenAI API.
def generate_embeddings(df, embedding_column, embedded_column, model):
    """
    Generate in a column the embeddings of a specified column of the dataframe using the Azure OpenAI API.

    :param df: DataFrame (e.g. df = pd.DataFrame({"text": ["This is a text to embed.", "This is another text to embed."]}))
    :param embedding_column: str (e.g. "Embedding")
    :param embedded_column: str (e.g. "Combined")
    :param model: str (e.g. "text-embedding")
    :return: DataFrame (e.g. df = pd.DataFrame({"Combined": ["This is a text to embed.", "This is another text to embed."], "Embedding": [[0.1, 0.2, 0.3, ..., 0.9], [0.2, 0.3, 0.4, ..., 0.8]]}))
    """
    
    def safe_embedding_text(x, model):
        # Convertir en chaîne de caractères si ce n'est pas déjà le cas (chgt aprés TU)
        if pd.isnull(x):  # Gérer les valeurs nulles et NaN
            return None
        if not isinstance(x, str):
            x = str(x)
        return embedding_text(x, model)
    
    df[embedding_column] = df[embedded_column].apply(lambda x: safe_embedding_text(x, model))
    
    # Return a dataframe with only embedded and embedding columns
    return df[[embedded_column, embedding_column]]