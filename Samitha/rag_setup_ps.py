import os
import glob
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np

# Step 1: Load all text files
def load_problems_docs(folder_path):
    """Load all .txt files from the specified folder"""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist!")
    
    files = glob.glob(os.path.join(folder_path, "*.txt"))
    
    if not files:
        raise ValueError(f"No .txt files found in '{folder_path}'!")
    
    docs = []
    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:  # Only add non-empty files
                    docs.append({"filename": os.path.basename(file), "text": text})
                else:
                    print(f"⚠️  Skipping empty file: {file}")
        except Exception as e:
            print(f"⚠️  Error reading {file}: {e}")
    
    if not docs:
        raise ValueError("No valid documents found!")
    
    print(f"📚 Loaded {len(docs)} documents")
    return docs

# Step 2: Split into chunks
def split_into_chunks(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks"""
    words = text.split()
    
    if len(words) <= chunk_size:
        return [text]
    
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Break if we've reached the end
        if i + chunk_size >= len(words):
            break
    
    return chunks

# Step 3: Create embeddings using a CPU-compatible model
def create_embeddings(docs):
    """Create embeddings for all document chunks"""
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        raise
    
    texts = []
    metadata = []
    
    for doc in docs:
        chunks = split_into_chunks(doc["text"])
        print(f"📄 Processing {doc['filename']}: {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadata.append({
                "filename": doc["filename"],
                "chunk_id": i,
                "total_chunks": len(chunks)
            })
    
    print(f"🔢 Total chunks to embed: {len(texts)}")
    
    if not texts:
        raise ValueError("No text chunks to embed!")
    
    try:
        embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
        print("✅ Embeddings created successfully")
        return embeddings, texts, metadata
    except Exception as e:
        print(f"❌ Error creating embeddings: {e}")
        raise

# Step 4: Save embeddings in FAISS index
def save_faiss_index(embeddings, texts, metadata, index_path="problems_index"):
    """Save FAISS index and metadata"""
    try:
        # Ensure embeddings are the right type
        embeddings = np.array(embeddings).astype("float32")
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        
        # Add embeddings to index
        index.add(embeddings)
        
        # Create directory if it doesn't exist
        os.makedirs(index_path, exist_ok=True)
        
        # Save index
        faiss.write_index(index, os.path.join(index_path, "problems.index"))
        
        # Save texts and metadata
        with open(os.path.join(index_path, "texts.pkl"), "wb") as f:
            pickle.dump(texts, f)
        
        with open(os.path.join(index_path, "metadata.pkl"), "wb") as f:
            pickle.dump(metadata, f)
        
        print(f"✅ FAISS index saved to '{index_path}'")
        print(f"📊 Index contains {index.ntotal} vectors of dimension {dimension}")
        
    except Exception as e:
        print(f"❌ Error saving FAISS index: {e}")
        raise

# Load existing index (bonus function)
def load_faiss_index(index_path="problems_index"):
    """Load existing FAISS index and metadata"""
    try:
        index = faiss.read_index(os.path.join(index_path, "problems.index"))
        
        with open(os.path.join(index_path, "texts.pkl"), "rb") as f:
            texts = pickle.load(f)
        
        with open(os.path.join(index_path, "metadata.pkl"), "rb") as f:
            metadata = pickle.load(f)
        
        print(f"✅ Loaded index with {index.ntotal} vectors")
        return index, texts, metadata
    
    except Exception as e:
        print(f"❌ Error loading index: {e}")
        raise

# Search function (bonus)
def search_similar(query, index, texts, metadata, model, top_k=5):
    """Search for similar documents"""
    query_embedding = model.encode([query]).astype("float32")
    distances, indices = index.search(query_embedding, top_k)
    
    results = []
    for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
        if idx != -1:  # Valid result
            results.append({
                "rank": i + 1,
                "distance": float(distance),
                "text": texts[idx][:200] + "..." if len(texts[idx]) > 200 else texts[idx],
                "metadata": metadata[idx]
            })
    
    return results

# Main execution
if __name__ == "__main__":
    try:
        folder = r"C:\Users\DELL\Desktop\sustainble\sustainable-smart-city\Samitha\problems"  # Update this to your folder path
        print("🚀 Starting document indexing process...")
        print("📂 Loading problems files...")
        docs = load_problems_docs(folder)
        
        print("🔍 Creating embeddings...")
        embeddings, texts, metadata = create_embeddings(docs)
        
        print("💾 Saving FAISS index...")
        save_faiss_index(embeddings, texts, metadata)
        
        print("🎉 Process completed successfully!")
        print(f"📈 Created index with {len(texts)} text chunks from {len(docs)} documents")
        
        # Optional: Test the search functionality
        print("\n🔍 Testing search functionality...")
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2")
            index, loaded_texts, loaded_metadata = load_faiss_index()
            
            # Example search
            test_query = "example search term"  # Replace with actual query
            results = search_similar(test_query, index, loaded_texts, loaded_metadata, model, top_k=3)
            
            print(f"Search results for '{test_query}':")
            for result in results:
                print(f"  {result['rank']}. {result['metadata']['filename']} (distance: {result['distance']:.4f})")
                
        except Exception as e:
            print(f"⚠️  Search test failed: {e}")
    
    except Exception as e:
        print(f"❌ Process failed: {e}")
        print("Please check that:")
        print("  1. The 'problems' folder exists")
        print("  2. The folder contains .txt files")
        print("  3. You have the required packages installed:")
        print("     pip install sentence-transformers faiss-cpu numpy")