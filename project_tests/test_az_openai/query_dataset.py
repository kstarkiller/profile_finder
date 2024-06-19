import os
import openpyxl
from langchain_openai import OpenAIEmbeddings

# Configuration for Azure OpenAI
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT = "aiprofilesmatching-text-embedding-3-large"

embedder = OpenAIEmbeddings(deployment=DEPLOYMENT, api_key=OPENAI_API_KEY)

# Function to read and embed text from a file
def embed_file(file_path):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active

    embeddings = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        text = ' '.join([str(cell) for cell in row])
        embedding = embedder.embed_query(text)
        embeddings.append(embedding)

    return embeddings

# Load files from a directory
directory = r"C:\Users\k.simon\Desktop\test_og"
file_paths = [os.path.join(directory, file_name) for file_name in os.listdir(directory) if file_name.endswith('.xlsx')]

# Embed all files
embedded_files = {file_path: embed_file(file_path) for file_path in file_paths}

# Print the embeddings for verification
for file_path, embedding in embedded_files.items():
    print(f"File: {file_path}\nEmbedding: {embedding[:5]}...")  # Print the first 5 elements of the embedding for brevity
