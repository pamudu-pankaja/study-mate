from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import re
import json

def int_to_roman(n):
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syms = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    for i in range(len(val)):
        while n >= val[i]:
            roman_num += syms[i]
            n -= val[i]
    return roman_num.lower()

def load_pdf(file_path, index_name, chunk_size=600, chunk_overlap=20, start_page=0):
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
        current_section = "Unknown"

        for i, chunk in enumerate(chunks):
            text = chunk.page_content.strip().lower()
            pdf_page = chunk.metadata.get("page", 0)
            physical_page_number = pdf_page + offset + 1

            if physical_page_number < start_page:
                logical_page = int_to_roman(physical_page_number)
            else:
                logical_page = physical_page_number - start_page + 1

            match = re.search(r'(\d+(\.\d+)*\s+|^)([A-Za-z][A-Za-z\s]+)', text)
            if match:
                current_section = match.group(3).strip()

            if len(text.split()):
                formatted_chunks.append({
                    "id": f"{base_name}-vec{i+1}",
                    "text": text,
                    "page": logical_page,
                    "section": current_section if current_section else "Unknown"
                })

        last_page_used = max(chunk.metadata.get("page", 0) for chunk in chunks)
        update_page_offset(index_name, last_page_used)

        # print(f"Chunks ; {formatted_chunks[0:2]}")
        return formatted_chunks
    except Exception as e:
        return f"Error while loading file: {e}"


# index_name = "history-text-1"
# file_path = "app/data/4_grade-11-history-text-book.pdf"
# result = load_pdf(file_path, index_name, start_page=12)

# print(result[0:2])