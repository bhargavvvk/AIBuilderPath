from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

import os

DATA_FOLDER = "data"
VECTOR_DB = "vectorstore"

documents = []

# Read all PDFs
for file in os.listdir(DATA_FOLDER):
    if file.endswith(".pdf"):
        reader = PdfReader(os.path.join(DATA_FOLDER, file))

        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        documents.append(text)

print(f"Loaded {len(documents)} document(s).")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = []

for doc in documents:
    chunks.extend(splitter.create_documents([doc]))

print(f"Created {len(chunks)} chunks.")
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
db = FAISS.from_documents(
    chunks,
    embedding_model
)

db.save_local(VECTOR_DB)

print("Vector database created successfully!")