import os
from openai import AzureOpenAI

# Description: Embed a text using the Azure OpenAI API.
def embedding_text(text, model):  # model = "azure deployment name"
    """
    Embed a text using the Azure OpenAI API.

    :param text: str (e.g. "This is a text to embed.")
    :param model: str (e.g. "text-embedding")
    :return: list (e.g. [0.1, 0.2, 0.3, ..., 0.9])
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