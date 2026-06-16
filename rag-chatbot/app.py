import streamlit as st
import faiss
import pickle
import numpy as np
import requests

from sentence_transformers import SentenceTransformer

st.title("📚 PDF Question Answering Chatbot (RAG)")
with st.sidebar:
    st.header("About")
    st.write("""
    This chatbot uses:
    - FAISS Vector Search
    - Sentence Transformers
    - Ollama Mistral
    - Retrieval Augmented Generation (RAG)
    """)
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index("faiss_index.index")

with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

question = st.text_input("Ask a question")

if question:

    query_embedding = embed_model.encode([question])

    distances, indices = index.search(
        np.array(query_embedding),
        k=3
    )

    retrieved_context = "\n\n".join(
        [chunks[i] for i in indices[0]]
    )

    prompt = f"""
Use the context below to answer.

Context:
{retrieved_context}

Question:
{question}

Answer:
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )

    answer = response.json()["response"]

    st.subheader("Answer")
    st.write(answer)

    with st.expander("Retrieved Context"):
        st.write(retrieved_context)
    st.caption(f"Retrieved {len(indices[0])} relevant chunks")