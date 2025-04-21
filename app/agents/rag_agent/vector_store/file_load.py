from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import re
import json

def load_pdf(file_path, index_name, chunk_size=600, chunk_overlap=20):

    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]

    def get_page_offset(index_name):
        if not os.path.exists("page_offsets.json"):
            return 0
        with open("page_offsets.json", "r") as f:
            offsets = json.load(f)
        return offsets.get(index_name, 0)

    def update_page_offset(index_name, last_page):
        if os.path.exists("page_offsets.json"):
            with open("page_offsets.json", "r") as f:
                offsets = json.load(f)
        else:
            offsets = {}
        offsets[index_name] = last_page
        with open("page_offsets.json", "w") as f:
            json.dump(offsets, f)

    try:
        loader = PyPDFLoader(file_path=file_path)
        docs = loader.load()

        offset = get_page_offset(index_name)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        chunks = splitter.split_documents(docs)

        formatted_chunks = []
        current_section = " Unknown"

        for i, chunk in enumerate(chunks):
            text = chunk.page_content.strip().lower()

            match = re.search(r'(\d+(\.\d+)*\s+|^)([A-Za-z][A-Za-z\s]+)', text)

            if match:
                current_section = match.group(3).strip()

            if len(text.split()):
                formatted_chunks.append({
                    "id": f"{base_name}-vec{i+1}",
                    "text": text,
                    "page": chunk.metadata.get("page", 0) + offset + 1, 
                    "section": current_section if current_section else "Unknown"
                })

        last_page_used = max(chunk.metadata.get("page", 0) for chunk in chunks)
        update_page_offset(index_name, last_page_used)

        return formatted_chunks
    except Exception as e:
        return f"Error while loading file: {e}"
