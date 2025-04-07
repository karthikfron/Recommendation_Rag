import streamlit as st
import faiss
import numpy as np
import json
import google.generativeai as genai

# Load the FAISS index
index = faiss.read_index("faiss_index.index")

# Load the assessment data
with open("enriched_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# FAISS search function
def search_assessments(query_embedding, top_k=10):
    distances, indices = index.search(np.array([query_embedding]).astype("float32"), top_k)
    results = [data[i] for i in indices[0]]
    return results

# Gemini embedding function
def generate_embedding(text):
    try:
        response = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_query"
        )
        return response['embedding']
    except Exception as e:
        st.error(f"Embedding error: {e}")
        return None

# --- UI Setup ---
st.set_page_config(page_title="SHL Assessment Recommender", layout="centered")
st.title("🔍 SHL Assessment Recommendation System")
st.markdown("Enter a job description or query to get the most relevant SHL assessments below.")

# --- Input Text ---
user_input = st.text_area("💬 Enter Job Description / Query", height=100)

# --- Future Filters Placeholder ---
with st.expander("🎛 Optional Filters ", expanded=False):
    st.checkbox("✅ Remote Testing Only")
    st.checkbox("⚡ Adaptive/IRT Only")
    st.slider("⏱ Max Duration (minutes)", 10, 100, 100)

# --- Search Button ---
if st.button("🚀 Find Assessments"):
    if user_input.strip():
        st.info("Searching assessments...")

        query_embedding = generate_embedding(user_input)
        if query_embedding:
            results = search_assessments(query_embedding)

            for result in results:
                with st.container():
                    st.markdown("----")
                    st.subheader(result.get("title", "Untitled"))
                    st.write(f"**Duration:** {result.get('duration', 'N/A')} mins")
                    st.write(f"**Type:** {result.get('type', 'N/A')}")
                    st.write(f"**Remote Testing Support:** {result.get('remote', 'N/A')}")
                    st.write(f"**Adaptive/IRT Support:** {result.get('adaptive', 'N/A')}")
                    if 'url' in result:
                        st.markdown(f"[🔗 Assessment Link]({result['url']})")
                    else:
                        st.markdown("*No assessment link available.*")
        else:
            st.error("Failed to generate embedding. Please try again.")
    else:
        st.warning("Please enter a job description or query.")
