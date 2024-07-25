import os
import pandas as pd
from openai import AzureOpenAI

# Paths according to the OS
if os.name == 'posix':
    combined_result_path = "app/processing_data/datas/combined_result.csv"
    embedded_data_path = "app/processing_data/datas/embedded_datas.csv"
else:
    combined_result_path = r"C:\Users\k.simon\Projet\avv-matcher\processing_data\datas\combined_result.csv"
    embedded_data_path = r"C:\Users\k.simon\Projet\avv-matcher\processing_data\datas\embedded_datas.csv"

def embedding_text(text, model):  # model = "azure deployment name"
    """
    Embed a text using the Azure OpenAI API.

    :param text: str
    :param model: str
    :return: list
    """

    AZURE_OPENAI_API_KEY=os.environ.get("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT=os.environ.get("AZURE_OPENAI_ENDPOINT")

        # Vérification du type de texte (TU)
    if not isinstance(text, str):
        raise TypeError("The text must be a string.")
    
    # Check if the credentials are correctly loaded
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY or not text:
        raise ValueError("AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_API_KEY environment variables must be set and a text have to be given.")
    else :
        
        client = AzureOpenAI(
        # Initialize the AzureOpenAI client 
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2024-02-01",
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        )
    

    return client.embeddings.create(input=[text], model=model).data[0].embedding


def generate_embeddings(df, embedding_column, embedded_column, model):
    """
    Generate in a column the embeddings of a specified column of the dataframe using the Azure OpenAI API.

    :param df: DataFrame
    :param embedding_column: str
    :param embedded_column: str
    :param model: str
    :return: DataFrame
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
