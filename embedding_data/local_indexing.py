import pandas as pd
import numpy as np
import faiss
import os

# Paths according to the OS
if os.name == 'posix':
    embedded_data_path = "/home/kevin/simplon/briefs/avv-matcher/processing_data/datas/embedded_datas.csv"
    complete_index_path = "/home/kevin/simplon/briefs/avv-matcher/embedding_data/index/complete_index.faiss"
else:
    embedded_data_path = r"C:\Users\simon\Projet\avv-matcher\processing_data\datas\embedded_datas.csv"
    complete_index_path = r"C:\Users\simon\Projet\avv-matcher\embedding_data\index\complete_index.faiss"

# Load data
df = pd.read_csv(embedded_data_path)

# Create a matrix of embeddings
df["embedding"] = df["embedding"].apply(lambda x: np.array(eval(x))) # type: ignore
embeddings = np.array(df["embedding"].tolist())

# Create the FAISS index and add the embeddings
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings) # type: ignore

# Save the index
faiss.write_index(index, complete_index_path)
