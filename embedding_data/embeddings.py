import os
from openai import AzureOpenAI
import pandas as pd

# Paths according to the OS
if os.name == 'posix':
    combined_result_path = "/home/kevin/simplon/briefs/avv-matcher/processing_data/datas/combined_result.csv"
    embedded_data_path = "/home/kevin/simplon/briefs/avv-matcher/processing_data/datas/embedded_datas.csv"
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

    # Initialize the AzureOpenAI client
    client = AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-01",
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"), # type: ignore
    )

    return client.embeddings.create(input=[text], model=model).data[0].embedding


def generate_embeddings(df, embedding_column, embedded_column, model):
    """
    Generate in a column the embeddings of a specified column of the dataframe using the Azure OpenAI API.

    :param client: AzureOpenAI object
    :param df: DataFrame
    :param embedding_column: str
    :param embedded_column: str
    :param model: str
    :return: DataFrame
    """

    df[embedding_column] = df[embedded_column].apply(lambda x: embedding_text(x, model))
    return df

df = pd.read_csv(combined_result_path)

df = generate_embeddings(df, "embedding", "Combined", "aiprofilesmatching-text-embedding-3-large")

# Save the dataframe
df.to_csv(embedded_data_path, index=False)