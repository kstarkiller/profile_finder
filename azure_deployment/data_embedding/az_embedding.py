import os
import pandas as pd

from modules.embed_text import embedding_text
from modules.generate_embedded_column import generate_embeddings

model = "aiprofilesmatching-text-embedding-3-large"

# Paths according to the OS
if os.name == "posix":
    combined_result_path = "data_processing/datas/combined/combined_result.csv"
    embedded_data_path = "data_processing/datas/embedded/embedded_datas.csv"
else:
    combined_result_path = r"C:\Users\k.simon\Projet\avv-matcher\azure_deployment\processing_data\datas\combined\combined_result.csv"
    embedded_data_path = r"C:\Users\k.simon\Projet\avv-matcher\azure_deployment\processing_data\datas\embedded\embedded_datas.csv"

# Load the data
df = pd.read_csv(combined_result_path)

# Embed the data
generate_embeddings(df, "Embedding", "Combined", model)

# Save the embedded data
df.to_csv(embedded_data_path, index=False)
