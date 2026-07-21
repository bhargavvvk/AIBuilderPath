from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.tools import tool

VECTOR_DB = "vectorstore"

_embedding_model = None
_db = None


def _get_db():
    global _embedding_model, _db

    if _db is not None:
        return _db

    _embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

    _db = FAISS.load_local(
        VECTOR_DB,
        _embedding_model,
        allow_dangerous_deserialization=True
    )

    return _db


@tool
def search_hr_policy(query: str, k: int = 3):
    """
    Search HR policy documents and return the most relevant chunks.
    """
    db = _get_db()
    results = db.similarity_search(query, k=k)

    return "\n\n".join(doc.page_content for doc in results)
if __name__ == "__main__":
    question = input("Ask a HR question: ")

    answer = search_hr_policy.invoke({"query": question})

    print("\nRetrieved Context:\n")
    print(answer)