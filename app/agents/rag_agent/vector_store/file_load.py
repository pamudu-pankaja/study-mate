from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import re

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
        current_section = "Unknown"

        for i, chunk in enumerate(chunks):
            text = chunk.page_content.strip().lower()

            match = re.search(r'(\d+(\.\d+)*\s+|^)([A-Za-z][A-Za-z\s]+)', chunks)

            if match:
                current_section = match.group(3).strip()

            if len(text.split()) <= 90:
                formatted_chunks.append({
                    "id": f"{base_name}-vec{i+1}",
                    "text": text,
                    "page":chunk.metadata.get("page","unknown"),
                    "section":current_section
                })

        return formatted_chunks
    except Exception as e:
        return f"Error while loading file : {e}"



