import pandas as pd
import numpy as np
import faiss

# Load data
df = pd.read_csv(r"processing_data\datas\embedded_data.csv")

# Create a matrix of embeddings
df["embeddings"] = df["embeddings"].apply(lambda x: np.array(eval(x)))
embeddings = np.array(df["embeddings"].tolist())

print(
    f"""
      Number of vectors: {embeddings.shape[0]}
      Number of dimensions: {embeddings.shape[1]}
      """
)

# Create the FAISS index and add the embeddings
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

# Save the index
faiss.write_index(index, r"embedding_data\index\faker_coaff.faiss")
print("Index saved successfully.")
