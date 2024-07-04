import pandas as pd
import numpy as np
import faiss

# Load data
df = pd.read_csv(r"processing_data\datas\embedded_data.csv")

# Create a matrix of embeddings
df["embedding"] = df["embedding"].apply(lambda x: np.array(eval(x))) # type: ignore
embeddings = np.array(df["embedding"].tolist())

# Create the FAISS index and add the embeddings
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings) # type: ignore

# Save the index
faiss.write_index(index, r"embedding_data\index\complete_index.faiss")
