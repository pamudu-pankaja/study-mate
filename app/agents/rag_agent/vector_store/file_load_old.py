from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import re
import json
from flask import current_app


def int_to_roman(n):
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syms = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ""
    for i in range(len(val)):
        while n >= val[i]:
            roman_num += syms[i]
            n -= val[i]
    return roman_num.lower()


def load_pdf(file_path, book_name, chunk_size=450, chunk_overlap=60, start_page=0):
    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]

    try:
        loader = PyPDFLoader(file_path=file_path)
        docs = loader.load()

        bullet_section = re.compile(r"^\s*[]+\s*(.*)", re.UNICODE)
        numbered_section = re.compile(
            r"^\s*(?:Chapter\s*)?(\d+)\s*[\.\s]\s*(\d+)\s+([A-Za-z].+)$", re.IGNORECASE
        )

        page_sections = {}

        for doc in docs:
            text = doc.page_content
            page = doc.metadata.get("page", 0)
            lines = text.splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                match = numbered_section.match(line)
                if match:
                    section = (
                        f"{match.group(1)}.{match.group(2)} {match.group(3).strip()}"
                    )
                    page_sections[page] = section
                    break

                match = bullet_section.match(line)
                if match:
                    section = match.group(1).strip()
                    word_count = len(section.split())

                    if section.lower().startswith("activity"):
                        continue

                    if word_count > 4:
                        continue

                    page_sections[page] = section
                    break

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        chunks = splitter.split_documents(docs)

        formatted_chunks = []

        for i, chunk in enumerate(chunks):
            text = chunk.page_content.strip()
            pdf_page = chunk.metadata.get("page", 0)
            physical_page_number = pdf_page + 1

            if physical_page_number < start_page:
                logical_page = int_to_roman(physical_page_number)
            else:
                logical_page = physical_page_number - start_page + 1

            current_section = ""
            for p in range(pdf_page, -1, -1):
                if p in page_sections:
                    current_section = page_sections[p]
                    break

            if len(text.split()):
                formatted_chunks.append(
                    {
                        "id": f"{base_name}-vec{i+1}",
                        "text": text,
                        "page": logical_page,
                        "section": current_section,
                    }
                )

        last_page_used = max(chunk.metadata.get("page", 0) for chunk in chunks)

        return formatted_chunks

    except Exception as e:
        print(f"Error while loading file: {e}")
        return None
