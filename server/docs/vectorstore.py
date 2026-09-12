import os
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config.db import chunk_collection

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINCONE_API_KEY = os.getenv("PINCONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "tutor-rags")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


UPLOADED_DIR = "./upload_docs"
os.makedirs(UPLOADED_DIR, exist_ok=True)

# pinecone global upsert function

pc = None
index = None

def get_pinecone_index():
    global pc, index
    if index is None:
        pc = Pinecone(api_key=PINCONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)

    return index


async def load_vectorstore(uploaded_files, role: str, doc_id:str, grade: int):
    # initialize embedding model
    embed_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    #  get pinecone indexx
    pinecone_index = get_pinecone_index()
    # loop through uploaded file
    for file in uploaded_files:
        # 1. save raw file
        save_path = Path(UPLOADED_DIR) / file.filename
        with open(save_path, "wb") as f:
            f.write(file.file.read())
        # 2. load pdf text
        loader = PyPDFLoader(str(save_path))
        documents = loader.load()
        # 3. chunk the text
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)
        # 4. guard condtions
        if not chunks: 
            print(f"No text extracted from {file.filename}, skipping...")
            continue
        # 5. dual storing
        # 5.1 store full text in mongodb
        chunk_docs=[]
        for i, chunk in enumerate(chunks):
            chunk_docs.append({
                "chunk_id": f"{doc_id}-{i}",
                "doc_id": doc_id,
                "text": chunk.page_content,
                "page": int(chunk.metadata.get("page", 0)),
                "source": file.filename,
                "grade": grade,
                "role": role
            })

        if chunk_docs:
            chunk_collection.insert_many(chunk_docs)

        # 5.2 create embeddings
        texts = [chunk.page_content for chunk in chunks]
        embeddings = await asyncio.to_thread(embed_model.embed_documents, texts)
        # upsert pinecone
        ids = [f"{doc_id}{-i}" for i in range(len(embeddings))]

        metadatas = [
            {
                "doc_id": doc_id,
                "page": int(chunks[i].metadata.get("page", 0)),
                "source": file.filename,
                "grade": grade,
                "role": role
            }
            for i in range(len(embeddings))
        ]


        pinecone_index.upsert(vectors=zip(ids, embeddings, metadatas))

    print(f"Succefully indexed {file.filename}")
