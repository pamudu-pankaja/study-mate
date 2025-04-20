from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def load_pdf(file_path, chunk_size=250, chunk_overlap=20):

    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]

    try:
        loader = PyPDFLoader(file_path=file_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        chunks = splitter.split_documents(docs)

        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            text = chunk.page_content.strip().lower()

            if len(text.split()) <= 90:
                formatted_chunks.append({
                    "id": f"{base_name}-vec{i+1}",
                    "text": text
                })

        return formatted_chunks
    except Exception as e:
        return f"Error while loading file : {e}"



