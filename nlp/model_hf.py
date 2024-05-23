import os
# from langchain_community.document_loaders import TextLoader
# from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import HuggingFaceEndpoint
from config import HUGGINGFACEHUB_API_TOKEN



def init_mistral_model(api_token, repo_id="mistralai/Mistral-7B-Instruct-v0.2", temperature=0.1, max_length=512):
    if "HUGGINGFACEHUB_API_TOKEN" not in os.environ:
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_token

    try:
        model = HuggingFaceEndpoint(repo_id=repo_id, temperature=temperature, model_kwargs={"max_length": max_length})
        print("Modèle initialisé avec succès.")
        return model
    except Exception as e:
        print("Erreur lors de l'initialisation du modèle :", e)
        return None