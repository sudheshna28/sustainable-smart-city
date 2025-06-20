import os
import glob
from sentence_transformers import SentenceTransformer
import faiss
import pickle

# Step 1: Load all text files
def load_village_docs(folder_path):
    files = glob.glob(os.path.join(folder_path, "*.txt"))
    docs = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
            docs.append({"filename": os.path.basename(file), "text": text})
    return docs

# Step 2: Split into chunks
def split_into_chunks(text, chunk_size=500):
    words = text.split()
    chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

# Step 3: Create embeddings using a CPU-compatible model
def create_embeddings(docs):
    model = SentenceTransformer("all-MiniLM-L6-v2")  # Fast and CPU-friendly
    texts = []
    metadata = []
    
    for doc in docs:
        chunks = split_into_chunks(doc["text"])
        for chunk in chunks:
            texts.append(chunk)
            metadata.append(doc["filename"])
    
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings, texts, metadata

# Step 4: Save embeddings in FAISS index
def save_faiss_index(embeddings, texts, metadata, index_path="faiss_index"):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    os.makedirs(index_path, exist_ok=True)
    
    faiss.write_index(index, os.path.join(index_path, "village.index"))
    with open(os.path.join(index_path, "texts.pkl"), "wb") as f:
        pickle.dump(texts, f)
    with open(os.path.join(index_path, "metadata.pkl"), "wb") as f:
        pickle.dump(metadata, f)
    
    print("✅ FAISS index and metadata saved!")

# Main
if __name__ == "__main__":
    folder = r"C:\Users\DELL\Desktop\sustainble\sustainable-smart-city\Samitha\villages"  # Update this to your folder path
    print("📂 Loading village files...")
    docs = load_village_docs(folder)

    print("🔍 Creating embeddings...")
    embeddings, texts, metadata = create_embeddings(docs)

    import numpy as np
    embeddings = np.array(embeddings).astype("float32")  # FAISS requires float32

    print("💾 Saving index...")
    save_faiss_index(embeddings, texts, metadata)
