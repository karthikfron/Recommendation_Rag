import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load Gemini API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load enriched assessment data
with open("enriched_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert each assessment into a text chunk for embedding
def prepare_text_for_embedding(item):
    return f"Title: {item['title']}. Duration: {item['duration']}. Type: {item['type']}. Remote: {item['remote']}. Adaptive: {item['adaptive']}."

texts = [prepare_text_for_embedding(item) for item in data]

# Use Gemini to embed the texts
model = genai.embed_content

embeddings = []
for text in texts:
    try:
        response = model(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        embeddings.append(response["embedding"])
    except Exception as e:
        print(f"Failed to embed: {text[:30]}... | Error: {e}")
        embeddings.append([0.0] * 768)  # fallback vector

# Save embeddings and their metadata for FAISS
import pickle

with open("assessment_embeddings.pkl", "wb") as f:
    pickle.dump({"data": data, "embeddings": embeddings}, f)

print("✅ Embeddings generated and saved to 'assessment_embeddings.pkl'")


import faiss
import numpy as np

# Convert embeddings to NumPy array
embedding_matrix = np.array(embeddings).astype("float32")

# Create FAISS index (L2 distance)
dimension = len(embedding_matrix[0])  # should be 768 for Gemini
index = faiss.IndexFlatL2(dimension)

# Add vectors to the FAISS index
index.add(embedding_matrix)

# Save the index for later use
faiss.write_index(index, "faiss_index.index")
print("✅ FAISS index created and saved to 'faiss_index.index'")

