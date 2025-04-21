from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import re
import json

def load_pdf(file_path, index_name, start_page, chunk_size=600, chunk_overlap=20):
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
        effective_start_page = max(start_page, offset + 1)
        
        # Filter out documents before the start page
        filtered_docs = [
            doc for doc in docs 
            if doc.metadata.get('page', 0) + 1 >= effective_start_page]

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        chunks = splitter.split_documents(filtered_docs)

        formatted_chunks = []
        current_section = "Unknown"
        last_pdf_page_used = offset

        for i, chunk in enumerate(chunks):
            text = chunk.page_content.strip().lower()

            match = re.search(r'(\d+(\.\d+)*\s+|^)([A-Za-z][A-Za-z\s]+)', text)

            if match:
                current_section = match.group(3).strip()

            pdf_page_number = chunk.metadata.get('page', 0) + 1
            logical_page_number = pdf_page_number - start_page + 1
            last_pdf_page_used = max(last_pdf_page_used, pdf_page_number)

            # Debugging output
            print(f"Debug Info: pdf_page_number={pdf_page_number}, logical_page_number={logical_page_number}") 

            if len(text.split()):
                formatted_chunks.append({
                    "id": f"{base_name}-vec{i+1}",
                    "text": text,
                    "page": logical_page_number,  # Page number assignment
                    "section": current_section if current_section else "Unknown"
                })

        if formatted_chunks: 
            update_page_offset(index_name, last_pdf_page_used)

        # Debugging output to check formatted chunks
        for chunk in formatted_chunks[:3]:
            print(f"Page: {chunk['page']}, ID: {chunk['id']}")

        return formatted_chunks

    except Exception as e:
        return f"Error while loading file: {e}"

# Example usage
index_name = "history-text-1"
file_path = "app/data/4_grade-11-history-text-book.pdf"
result = load_pdf(file_path, index_name, start_page=24)
print(result)
