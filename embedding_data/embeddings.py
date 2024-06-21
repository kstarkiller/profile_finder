import os
import sys
from openai import AzureOpenAI

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from processing_data.processing import data_processing

def embedding_text(text, model):  # model = "azure deployment name"
    """
    Embed a text using the Azure OpenAI API.

    :param text: str
    :param model: str
    :return: list
    """

    # Initialize the AzureOpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
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


# # Retrieve the Dataframe
# file_path = "processing_data/datas/faker_data.csv"
# df, total_tokens = data_processing(file_path, "cl100k_base")

# # Generate the embeddings
# model = "aiprofilesmatching-text-embedding-3-large"
# df = generate_embeddings(df, "embeddings", "combined", model)

# # Save the processed data
# df.to_csv("processing_data/datas/embedded_data.csv", index=False)

# print("Data processed and saved successfully.")
