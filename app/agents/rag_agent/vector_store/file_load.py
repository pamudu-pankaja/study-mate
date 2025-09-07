from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import re
import json
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import numpy as np
import random
from typing import List, Dict, Tuple, Optional
import multiprocessing

# Configure Tesseract path (adjust for your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

language_patterns = {
    'sin': r'[\u0D80-\u0DFF0-9]',  # Sinhala
    'tam': r'[\u0B80-\u0BFF0-9]',  # Tamil
    'hin': r'[\u0900-\u097F]',  # Hindi/Devanagari
    'ara': r'[\u0600-\u06FF]',  # Arabic
    'jpn': r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]',  # Japanese (Hiragana, Katakana, Kanji)
    'kor': r'[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]',  # Korean (Hangul Syllables, Jamo, Compatibility)
    'eng': r'[A-Za-z0-9]',  # English (basic Latin alphabet)
    'rus': r'[\u0400-\u04FF]',  # Russian (Cyrillic)
}

def int_to_roman(n: int) -> str:
    """Convert integer to lowercase Roman numeral"""
    if n <= 0:
        return str(n)
    
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syms = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ""
    for i in range(len(val)):
        while n >= val[i]:
            roman_num += syms[i]
            n -= val[i]
    return roman_num.lower()

def detect_language(text_sample: str) -> List[str]:
    """
    Detect the primary language in text sample
    Returns list of appropriate Tesseract language codes
    """
    
    #THIS GATE IS ALSO NOT MINE
    if not text_sample.strip():
        return ['eng']
    
    detected_languages = []
    text_length = len(text_sample)
    language_stats = {}
    
    for lang_code, pattern in language_patterns.items():
        matches = re.findall(pattern, text_sample)
        match_count = len(''.join(matches)) 
        
        if match_count > 0:
            percentage = (match_count / text_length) * 100
            language_stats[lang_code] = {'count': match_count, 'percentage': percentage}
            
            threshold = 5 if lang_code == 'eng' else 30
            
            if percentage >= threshold:
                detected_languages.append(lang_code)
                print(f"  Language {lang_code}: {match_count} chars ({percentage:.1f}%) - INCLUDED")
            else:
                print(f"  Language {lang_code}: {match_count} chars ({percentage:.1f}%) - below threshold ({threshold}%)")
    
    #THIS STAYS AS A COMMENT FOR ACCUARCY OF THE TEXT
    # Always include English as the default fallback
    # if 'eng' not in detected_languages:
    #     detected_languages.append('eng')
    #     print(f"  Language eng: added as default fallback")
    
    
    #THIS STYAS AS A COMMENT BECAUSE THIS ISNT A MY IDEA I WILL CONSIDER USING THIS IF THIS LOOKS FITS
    # If we have Sinhala with high confidence (>60%), and other languages with much lower confidence, 
    # only keep Sinhala + English to avoid confusion
    # if 'sin' in language_stats and language_stats['sin']['percentage'] > 60:
    #     # Check if other languages (except English) have significantly lower percentages
    #     other_significant_langs = []
    #     for lang in detected_languages:
    #         if lang not in ['eng', 'sin'] and lang in language_stats:
    #             if language_stats[lang]['percentage'] > language_stats['sin']['percentage'] * 0.4:  # If other lang is >40% of Sinhala percentage
    #                 other_significant_langs.append(lang)
        
    #     if not other_significant_langs:
    #         detected_languages = ['eng', 'sin']
    #         print(f"  Simplified to primary languages: eng+sin (Sinhala dominant at {language_stats['sin']['percentage']:.1f}%)")
    
    return detected_languages

def is_page_corrupted(text: str, threshold: float = 0.7) -> bool:
    """Check if page text is corrupted/unreadable"""
    total_chars = len(text.strip())
    if total_chars == 0:
        return True  # empty page = corrupted

    matched_chars = 0
    for pattern in language_patterns.values():
        matched_chars += len(re.findall(pattern, text))

    coverage = matched_chars / total_chars if total_chars > 0 else 0
    return coverage < threshold

def process_page_ocr(file_path: str, page_num: int, ocr_language: str) -> Dict:
    """Extract text from a single page using OCR - for multiprocessing"""
    try:
        doc = fitz.open(file_path)
        page = doc.load_page(page_num)
        
        mat = fitz.Matrix(2, 2)  # Increase resolution for better OCR
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        
        img = Image.open(io.BytesIO(img_data))
        
        custom_config = f'--oem 3 --psm 6 -l {ocr_language}'
        ocr_text = pytesseract.image_to_string(img, config=custom_config)
        
        doc.close()
        
        return {
            'text': ocr_text,
            'page_num': page_num,
            'success': True
        }
    except Exception as e:
        print(f"OCR failed for page {page_num}: {e}")
        return {
            'text': '',
            'page_num': page_num,
            'success': False,
            'error': str(e)
        }

def process_page_direct(file_path: str, page_num: int) -> Dict:
    """Extract text from a single page using direct extraction - for multiprocessing"""
    try:
        doc = fitz.open(file_path)
        page = doc.load_page(page_num)
        
        extracted_text = page.get_text()
        doc.close()
        
        return {
            'text': extracted_text,
            'page_num': page_num,
            'success': True
        }
    except Exception as e:
        print(f"Direct extraction failed for page {page_num}: {e}")
        return {
            'text': '',
            'page_num': page_num,
            'success': False,
            'error': str(e)
        }

def determine_ocr_need_and_language(file_path: str, pdf_language: str, start_page: int, total_pages: int) -> Tuple[bool, str]:
    """Determine if OCR is needed and what languages to use"""
    doc = fitz.open(file_path)
    use_ocr = False
    ocr_language = ""
    
    auto_detect_language = True if pdf_language.lower() == "auto" else False
    try:
        # Convert start_page to 0-indexed for internal processing
        start_page_idx = max(0, start_page - 1) if start_page > 0 else 0
        
        # Sample from start_page onwards where the actual content is
        available_pages = max(0, total_pages - start_page_idx)
        population = list(range(start_page_idx, total_pages))
        if not population:
            return False, "eng"

        # Sample up to 3 pages, but not more than population size
        sample_size = min(len(population), 3)
        sample_pages = random.sample(population, sample_size)

        mojibake_count = 0
        for page_num in sample_pages:
            page = doc.load_page(page_num)
            text = page.get_text()
            if is_page_corrupted(text):
                mojibake_count += 1

        use_ocr = mojibake_count >= max(1, sample_size // 2)

        if use_ocr and auto_detect_language:
            detected_languages = []

            # Sample from start_page onwards for language detection (where actual content is)
            lang_population = list(range(start_page_idx, min(start_page_idx + available_pages // 2, total_pages)))
            if not lang_population:
                return True, "eng"  
            language_sample_size = min(len(lang_population), 2)
            language_sample_pages = random.sample(lang_population, language_sample_size)

            for page_num in language_sample_pages:
                page = doc.load_page(page_num)
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))

                try:
                    ocr_result = pytesseract.image_to_string(img, config='--oem 3 --psm 6 -l sin+eng+tam+hin+jpn+kor+ara+rus+chi_sim')
                    page_languages = detect_language(ocr_result)
                    detected_languages.extend(page_languages)
                except Exception as e:
                    print(f"Language detection failed for page {page_num}: {e}")
                    detected_languages.append("eng")

            unique_languages = list(set(detected_languages))
            ocr_language = "+".join(unique_languages) if unique_languages else "eng"
            print(f"Using OCR with languages: {ocr_language}")

        elif use_ocr and not auto_detect_language:
            ocr_language = pdf_language
            print(f"Using OCR with languages: {ocr_language}")

    except Exception as e:
        print(f"Error during OCR need determination: {e}")
        use_ocr = False
        ocr_language = "eng"
    finally:
        doc.close()

    return use_ocr, ocr_language


def read_pdf_text(file_path: str, pdf_language: str, start_page: int = 0) -> List[Dict]:
    """
    Load PDF using PyMuPDF with optional parallel OCR
    
    Args:
        file_path: Path to PDF file
        start_page: Starting page number (0-indexed) - NOT used to filter pages, only for logical numbering
    
    Returns:
        List of dictionaries with text and page_num
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    # Get total pages first
    doc = fitz.open(file_path)
    total_pages = len(doc)
    doc.close()
    
    # Process ALL pages, regardless of start_page
    # start_page is only used for logical page numbering, not for filtering
    
    # Determine OCR need and language
    use_ocr, ocr_language = determine_ocr_need_and_language(file_path, pdf_language, start_page, total_pages)
    
    documents = []
    page_range = list(range(0, total_pages))  # Process all pages
    
    try:
        if use_ocr:
            print(f"Processing {len(page_range)} pages with OCR using {multiprocessing.cpu_count()} processes...")
            # Use ProcessPoolExecutor for CPU-intensive OCR
            max_workers = min(multiprocessing.cpu_count(), len(page_range))
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # Submit all OCR tasks
                future_to_page = {
                    executor.submit(process_page_ocr, file_path, page_num, ocr_language): page_num 
                    for page_num in page_range
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_page):
                    result = future.result()
                    if result['success']:
                        documents.append({
                            'text': result['text'],
                            'page_num': result['page_num']
                        })
                    else:
                        print(f"Failed to process page {result['page_num']}: {result.get('error', 'Unknown error')}")
        else:
            print(f"Processing {len(page_range)} pages with direct text extraction...")
            # For direct text extraction, we can also use parallel processing
            # but it's less CPU-intensive, so we might use fewer workers
            max_workers = min(4, len(page_range))  # Fewer workers for I/O bound operations
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # Submit all direct extraction tasks
                future_to_page = {
                    executor.submit(process_page_direct, file_path, page_num): page_num 
                    for page_num in page_range
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_page):
                    result = future.result()
                    if result['success']:
                        documents.append({
                            'text': result['text'],
                            'page_num': result['page_num']
                        })
                    else:
                        print(f"Failed to process page {result['page_num']}: {result.get('error', 'Unknown error')}")
        
        # Sort documents by page number to maintain order
        documents.sort(key=lambda x: x['page_num'])
        
    except Exception as e:
        print(f"Error during parallel processing: {e}")
        return []
    
    print(f"Successfully processed {len(documents)} pages")
    return documents , use_ocr , ocr_language

def clean_text(text: str) -> str:
    """Clean and normalize multilingual text (including Sinhala)"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    return '\n'.join(lines)

def load_pdf(file_path: str, start_page: int = 1, pdf_language: str = 'Auto', chunk_size: int = 450, chunk_overlap: int = 60) -> List[Dict]:
    """
    Load and process PDF with chunking and section detection
    
    Args:
        file_path: Path to PDF file
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        start_page: The PDF page number that corresponds to logical page 1 (1-indexed)
                   Pages before this will be numbered with Roman numerals
    
    Returns:
        List of formatted chunks with metadata
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]

    try:
        # Read PDF text with parallel processing (process all pages)
        pages_data, use_ocr , ocr_language = read_pdf_text(file_path=file_path, pdf_language=pdf_language, start_page=start_page)
        
        if not pages_data:
            print("No pages could be processed")
            return []
        
        # Create Document objects
        docs = []
        for page_data in pages_data:
            # cleaned_text = clean_text(page_data['text']) DO NOT RUN THIS , THIS WILL FUCK UP THE SECTION 
            if page_data['text'].strip():  # Only add non-empty pages
                doc = Document(
                    page_content=page_data['text'],
                    metadata={'page': page_data['page_num']}
                )
                docs.append(doc)

        if not docs:
            print("No valid document content found")
            return []

        # Section detection patterns
        bullet_section = re.compile(r"^\s*[•\-\*]+\s*(.*)", re.UNICODE)
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

        # Split documents into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
        chunks = splitter.split_documents(docs)

        # Format chunks with metadata
        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            text = chunk.page_content.strip()
            if not text:  # Skip empty chunks
                continue
                
            pdf_page = chunk.metadata.get("page", 0)
            physical_page_number = pdf_page + 1  # Convert from 0-indexed to 1-indexed

            # Calculate logical page number based on start_page
            if physical_page_number < start_page:
                # Pages before start_page get Roman numerals
                roman_page = physical_page_number
                logical_page = int_to_roman(roman_page)
            else:
                # Pages from start_page onwards get regular numbering starting from 1
                logical_page = physical_page_number - start_page + 1

            # Find current section
            current_section = ""
            for p in range(pdf_page, -1, -1):
                if p in page_sections:
                    current_section = page_sections[p]
                    break

            # Only add chunks with meaningful content
            if len(text.split()) > 5:  # At least 5 words
                formatted_chunks.append({
                    "id": f"{base_name}-vec{i+1}",
                    "text": text,
                    "page": logical_page,
                    "section": current_section,
                })

        print(f"Successfully processed {len(formatted_chunks)} chunks from {len(docs)} pages")
        return formatted_chunks , ocr_language

    except Exception as e:
        print(f"Error while loading file: {e}")
        return []

