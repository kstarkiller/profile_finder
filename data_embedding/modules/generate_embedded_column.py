import pandas as pd
import sys
sys.path.append('data_embedding/modules')
from embed_text import embedding_text

def generate_embeddings(df: pd.DataFrame, embedding_column: str, embedded_column: str, model: str) -> pd.DataFrame:
    """
    Generate in a column the embeddings of a specified column of the dataframe using the Azure OpenAI API.

    :param df: DataFrame (e.g. df = pd.DataFrame({"text": ["This is a text to embed.", "This is another text to embed."]}))
    :param embedding_column: str (e.g. "Embedding")
    :param embedded_column: str (e.g. "text")
    :param model: str (e.g. "text-embedding")
    :return: DataFrame (e.g. df = pd.DataFrame({"text": ["This is a text to embed.", "This is another text to embed."], "Embedding": [[0.1, 0.2, 0.3, ..., 0.9], [0.2, 0.3, 0.4, ..., 0.8]]}))
    """
    # Validate inputs
    if df is None:
        raise ValueError("DataFrame cannot be None.")
    if not isinstance(embedding_column, str) or not embedding_column:
        raise ValueError("Embedding column must be a non-empty string.")
    if not isinstance(embedded_column, str) or not embedded_column:
        raise ValueError("Embedded column must be a non-empty string.")
    if not isinstance(model, str) or not model:
        raise ValueError("Model must be a non-empty string.")
    if embedded_column not in df.columns:
        raise KeyError(f"DataFrame does not contain the column '{embedded_column}'.")

    # Check if DataFrame is empty
    if df.empty:
        if embedded_column not in df.columns or embedding_column not in df.columns:
            raise KeyError(f"DataFrame does not contain the columns '{embedded_column}' and/or '{embedding_column}'.")
        return df[[embedded_column, embedding_column]]

    # Define a helper function for embedding text
    def safe_embedding_text(x: str, model: str):
        if pd.isnull(x):
            return None
        return embedding_text(str(x), model)

    # Apply the embedding function to the specified column
    df[embedding_column] = df[embedded_column].apply(lambda x: safe_embedding_text(x, model))

    # Return the DataFrame with the specified columns
    return df[[embedded_column, embedding_column]]