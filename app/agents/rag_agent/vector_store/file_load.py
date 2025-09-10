from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor
import os
import re
import json
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import numpy as np
import random
from typing import List, Dict, Tuple
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
    'chi_sim': r'[\u4e00-\u9fff]'  # Chinese Simplified
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
    if not text_sample or not text_sample.strip():
        return ['eng']
    
    detected_languages = []
    text_length = len(text_sample)
    language_stats = {}
    
    print(f"Analyzing text sample of {text_length} characters...")
    
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
    
    if not detected_languages:
        detected_languages = ['eng']
        print("  No languages detected above threshold, defaulting to English")
    
    return detected_languages

def is_page_corrupted(text: str, threshold: float = 0.7) -> bool:
    """Check if page text is corrupted/unreadable"""
    if not text or not text.strip():
        return True  # empty page = corrupted

    text = text.strip()
    total_chars = len(text)
    
    if total_chars == 0:
        return True

    matched_chars = 0
    for pattern in language_patterns.values():
        matched_chars += len(re.findall(pattern, text))

    coverage = matched_chars / total_chars if total_chars > 0 else 0
    return coverage < threshold

def safe_extract_page_data(args) -> Dict:
    """Safely extract page data for multiprocessing"""
    file_path, page_num, use_ocr = args
    
    try:
        doc = fitz.open(file_path)
        page = doc.load_page(page_num)
        
        if use_ocr:
            mat = fitz.Matrix(2, 2)  # Increase resolution for better OCR
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            result = {
                'page_num': page_num,
                'data': img_data,
                'type': 'image',
                'success': True
            }
        else:
            extracted_text = page.get_text()
            result = {
                'page_num': page_num,
                'data': extracted_text,
                'type': 'text',
                'success': True
            }
        
        doc.close()
        return result
        
    except Exception as e:
        return {
            'page_num': page_num,
            'data': None,
            'type': 'error',
            'success': False,
            'error': str(e)
        }

def extract_page_data(file_path: str, use_ocr: bool, max_workers: int = None) -> List[Dict]:
    """Pre-extract all page data with parallel processing"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    # Get total pages first
    doc = fitz.open(file_path)
    total_pages = len(doc)
    doc.close()
    
    if total_pages == 0:
        print("PDF has no pages")
        return []
    
    print(f"Extracting data from {total_pages} pages...")
    
    # Prepare arguments for parallel processing
    if max_workers is None:
        max_workers = min(multiprocessing.cpu_count(), total_pages, 8)  # Cap at 8 workers
    
    args_list = [(file_path, page_num, use_ocr) for page_num in range(total_pages)]
    pages_data = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all extraction tasks
        future_to_page = {
            executor.submit(safe_extract_page_data, args): args[1] 
            for args in args_list
        }
        
        completed = 0
        for future in as_completed(future_to_page):
            result = future.result()
            
            if result['success']:
                pages_data.append(result)
            else:
                print(f"Failed to extract page {result['page_num']}: {result.get('error', 'Unknown error')}")
            
            completed += 1
            if completed % 20 == 0 or completed == total_pages:
                print(f"Extracted {completed}/{total_pages} pages")
    
    # Sort by page number to maintain order
    pages_data.sort(key=lambda x: x['page_num'])
    
    print(f"Successfully extracted {len(pages_data)} pages out of {total_pages}")
    return pages_data

def process_page_ocr(page_data: Dict, ocr_language: str) -> Dict:
    """Extract text from page image data using OCR - for multiprocessing"""
    try:
        img_data = page_data['data']
        page_num = page_data['page_num']
        
        if img_data is None:
            return {
                'text': '',
                'page_num': page_num,
                'success': False,
                'error': 'No image data'
            }
        
        img = Image.open(io.BytesIO(img_data))
        
        # Optimize OCR configuration
        custom_config = f'--oem 3 --psm 6 -l {ocr_language}'
        
        try:
            ocr_text = pytesseract.image_to_string(img, config=custom_config)
        except Exception as ocr_error:
            # Fallback to basic OCR without specific language
            print(f"OCR with language {ocr_language} failed for page {page_num}, trying basic OCR: {ocr_error}")
            try:
                ocr_text = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
            except Exception as fallback_error:
                print(f"Fallback OCR also failed for page {page_num}: {fallback_error}")
                return {
                    'text': '',
                    'page_num': page_num,
                    'success': False,
                    'error': f'OCR failed: {fallback_error}'
                }
        
        return {
            'text': ocr_text,
            'page_num': page_num,
            'success': True
        }
    except Exception as e:
        print(f"OCR processing failed for page {page_data.get('page_num', 'unknown')}: {e}")
        return {
            'text': '',
            'page_num': page_data.get('page_num', 0),
            'success': False,
            'error': str(e)
        }

def process_page_direct(page_data: Dict) -> Dict:
    """Process pre-extracted text - for multiprocessing"""
    try:
        extracted_text = page_data['data']
        page_num = page_data['page_num']
        
        if extracted_text is None:
            extracted_text = ''
        
        return {
            'text': extracted_text,
            'page_num': page_num,
            'success': True
        }
    except Exception as e:
        print(f"Direct processing failed for page {page_data.get('page_num', 'unknown')}: {e}")
        return {
            'text': '',
            'page_num': page_data.get('page_num', 0),
            'success': False,
            'error': str(e)
        }

def determine_ocr_need_and_language(file_path: str, pdf_language: str, start_page: int, total_pages: int) -> Tuple[bool, str]:
    """Determine if OCR is needed and what languages to use with improved error handling"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False, "eng"
    
    doc = None
    use_ocr = False
    ocr_language = "eng"
    
    auto_detect_language = True if pdf_language.lower() == "auto" else False
    
    try:
        doc = fitz.open(file_path)
        
        # Convert start_page to 0-indexed for internal processing
        start_page_idx = max(0, start_page - 1) if start_page > 0 else 0
        
        # Sample from start_page onwards where the actual content is
        available_pages = max(0, total_pages - start_page_idx)
        
        if available_pages == 0:
            print("No pages available for analysis after start_page")
            return False, "eng"
            
        population = list(range(start_page_idx, total_pages))
        if not population:
            return False, "eng"

        # Sample up to 3 pages, but not more than population size
        sample_size = min(len(population), 3)
        sample_pages = random.sample(population, sample_size)
        
        print(f"Analyzing {sample_size} sample pages for OCR need: {sample_pages}")

        mojibake_count = 0
        for page_num in sample_pages:
            try:
                page = doc.load_page(page_num)
                text = page.get_text()
                if is_page_corrupted(text):
                    mojibake_count += 1
                    print(f"Page {page_num + 1} appears corrupted/unreadable")
                else:
                    print(f"Page {page_num + 1} has readable text")
            except Exception as e:
                print(f"Error analyzing page {page_num}: {e}")
                mojibake_count += 1

        use_ocr = mojibake_count >= max(1, sample_size // 2)
        print(f"OCR needed: {use_ocr} ({mojibake_count}/{sample_size} pages corrupted)")

        if use_ocr and auto_detect_language:
            detected_languages = []
            print("Auto-detecting language from OCR samples...")

            # Sample from start_page onwards for language detection
            lang_population = list(range(start_page_idx, min(start_page_idx + available_pages // 2, total_pages)))
            if not lang_population:
                lang_population = [start_page_idx] if start_page_idx < total_pages else [0]
                
            language_sample_size = min(len(lang_population), 2)
            language_sample_pages = random.sample(lang_population, language_sample_size)
            
            print(f"Using pages {language_sample_pages} for language detection")

            for page_num in language_sample_pages:
                try:
                    page = doc.load_page(page_num)
                    mat = fitz.Matrix(2, 2)
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))

                    # Try OCR with multiple languages for detection
                    langs = "eng+ara+hin+jpn+kor+sin+tam+chi_sim+rus"
                    try:
                        ocr_result = pytesseract.image_to_string(img, config=f'--oem 3 --psm 6 -l {langs}')
                        if ocr_result and ocr_result.strip():
                            page_languages = detect_language(ocr_result)
                            detected_languages.extend(page_languages)
                            print(f"Page {page_num + 1} detected languages: {page_languages}")
                        else:
                            print(f"Page {page_num + 1}: No OCR text detected")
                            detected_languages.append("eng")
                    except Exception as ocr_e:
                        print(f"OCR language detection failed for page {page_num + 1}: {ocr_e}")
                        detected_languages.append("eng")
                        
                except Exception as e:
                    print(f"Language detection failed for page {page_num + 1}: {e}")
                    detected_languages.append("eng")

            unique_languages = list(set(detected_languages))
            ocr_language = "+".join(unique_languages) if unique_languages else "eng"
            print(f"Final detected languages: {unique_languages}")

        elif use_ocr and not auto_detect_language:
            ocr_language = pdf_language
            print(f"Using specified language: {ocr_language}")

    except Exception as e:
        print(f"Error during OCR need determination: {e}")
        use_ocr = False
        ocr_language = "eng"
    finally:
        if doc:
            doc.close()

    print(f"Final decision - Use OCR: {use_ocr}, Language: {ocr_language}")
    return use_ocr, ocr_language

def read_pdf_text(file_path: str, pdf_language: str, start_page: int = 0) -> Tuple[List[Dict], bool, str]:
    """
    Load PDF using PyMuPDF with optional parallel OCR
    
    Args:
        file_path: Path to PDF file
        pdf_language: Language code or 'auto'
        start_page: Starting page number (1-indexed) - NOT used to filter pages, only for logical numbering
    
    Returns:
        Tuple of (documents, use_ocr, ocr_language)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    print(f"Loading PDF: {file_path}")
    
    # Get total pages first
    try:
        doc = fitz.open(file_path)
        total_pages = len(doc)
        doc.close()
        print(f"PDF has {total_pages} pages")
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return [], False, "eng"
    
    if total_pages == 0:
        print("PDF has no pages")
        return [], False, "eng"
    
    # Determine OCR need and language
    use_ocr, ocr_language = determine_ocr_need_and_language(file_path, pdf_language, start_page, total_pages)
    
    # Pre-extract all page data to avoid file handle conflicts
    try:
        pages_data = extract_page_data(file_path, use_ocr)
    except Exception as e:
        print(f"Error extracting page data: {e}")
        return [], use_ocr, ocr_language
    
    if not pages_data:
        print("No page data extracted")
        return [], use_ocr, ocr_language
    
    documents = []
    
    try:
        if use_ocr:
            print(f"Processing {len(pages_data)} pages with OCR using up to {min(multiprocessing.cpu_count(), 4)} processes...")
            # Use ProcessPoolExecutor for CPU-intensive OCR, but limit workers to avoid memory issues
            max_workers = min(multiprocessing.cpu_count(), 4, len(pages_data))
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # Submit all OCR tasks with pre-extracted image data
                future_to_page = {
                    executor.submit(process_page_ocr, page_data, ocr_language): page_data['page_num'] 
                    for page_data in pages_data
                }
                
                completed = 0
                # Collect results as they complete
                for future in as_completed(future_to_page):
                    result = future.result()
                    completed += 1
                    
                    if result['success']:
                        documents.append({
                            'text': result['text'],
                            'page_num': result['page_num']
                        })
                    else:
                        print(f"Failed to process page {result['page_num']}: {result.get('error', 'Unknown error')}")
                    
                    # Progress update every 10 pages or on completion
                    if completed % 10 == 0 or completed == len(pages_data):
                        print(f"OCR Progress: {completed}/{len(pages_data)} pages processed")
                        
        else:
            print(f"Processing {len(pages_data)} pages with direct text extraction...")
            # For direct text extraction, use ThreadPoolExecutor (I/O bound)
            max_workers = min(8, len(pages_data))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all direct extraction tasks
                future_to_page = {
                    executor.submit(process_page_direct, page_data): page_data['page_num'] 
                    for page_data in pages_data
                }
                
                completed = 0
                # Collect results as they complete
                for future in as_completed(future_to_page):
                    result = future.result()
                    completed += 1
                    
                    if result['success']:
                        documents.append({
                            'text': result['text'],
                            'page_num': result['page_num']
                        })
                    else:
                        print(f"Failed to process page {result['page_num']}: {result.get('error', 'Unknown error')}")
                    
                    # Progress update every 20 pages or on completion
                    if completed % 20 == 0 or completed == len(pages_data):
                        print(f"Text Extraction Progress: {completed}/{len(pages_data)} pages processed")
        
        # Sort documents by page number to maintain order
        documents.sort(key=lambda x: x['page_num'])
        
    except Exception as e:
        print(f"Error during parallel processing: {e}")
        import traceback
        traceback.print_exc()
        return [], use_ocr, ocr_language
    
    print(f"Successfully processed {len(documents)} pages")
    return documents, use_ocr, ocr_language

def clean_text(text: str) -> str:
    """Clean and normalize multilingual text (including Sinhala)"""
    if not text:
        return ""
    
    # Remove excessive whitespace while preserving structure
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double newline
    text = re.sub(r'[\u200c\u200d]', '', text)
    
    # Remove empty lines but preserve paragraph structure
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line:  # Keep non-empty lines
            cleaned_lines.append(line)
        elif cleaned_lines and cleaned_lines[-1]:  # Keep one empty line after content
            cleaned_lines.append('')
    
    return '\n'.join(cleaned_lines)

def detect_sections(docs: List[Document]) -> Dict[int, str]:
    """Detect sections across all pages with improved pattern matching"""
    page_sections = {}
    
    # Enhanced section detection patterns
    numbered_section = re.compile(
        r"^\s*(?:Chapter\s*)?(\d+)\s*[\.\s]\s*(\d+)\s+([A-Za-z].+)$", 
        re.IGNORECASE | re.UNICODE
    )
    
    bullet_section = re.compile(
        r"^\s*[]+\s*(.*)", re.UNICODE
    )
    
    # Additional patterns for different numbering systems
    simple_numbered = re.compile(
        r"^\s*(\d+)\.\s*([A-Za-z].+)$",
        re.UNICODE
    )
    
    roman_numbered = re.compile(
        r"^\s*([IVXLCDMivxlcdm]+)\.\s*([A-Za-z].+)$",
        re.UNICODE
    )

    for doc in docs:
        text = doc.page_content
        page = doc.metadata.get("page", 0)
        lines = text.splitlines()
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:  # Skip very short lines
                continue

            # Try different section patterns in order of specificity
            patterns_to_try = [
                (numbered_section, lambda m: f"{m.group(1)}.{m.group(2)} {m.group(3).strip()}"),
                (simple_numbered, lambda m: f"{m.group(1)} {m.group(2).strip()}"),
                (roman_numbered, lambda m: f"{m.group(1)} {m.group(2).strip()}"),
                (bullet_section, lambda m: m.group(1).strip())
            ]
            
            section_found = False
            for pattern, formatter in patterns_to_try:
                match = pattern.match(line)
                if match:
                    section = formatter(match)
                    word_count = len(section.split())
                    
                    # Skip if looks like an activity or is too long
                    if (section.lower().startswith("activity") or 
                        word_count > 8 or 
                        len(section) > 100):
                        continue
                    
                    page_sections[page] = section
                    print(f"Found section on page {page + 1}: {section}")
                    section_found = True
                    break
            
            if section_found:
                break
    
    print(f"Detected {len(page_sections)} sections across all pages")
    return page_sections

def load_pdf(file_path: str, start_page: int = 1, pdf_language: str = 'auto', 
             chunk_size: int = 450, chunk_overlap: int = 60) -> Tuple[List[Dict], str]:
    """
    Load and process PDF with chunking and section detection
    
    Args:
        file_path: Path to PDF file
        start_page: The PDF page number that corresponds to logical page 1 (1-indexed)
        pdf_language: Language code or 'auto'
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
    
    Returns:
        Tuple of (formatted_chunks, ocr_language)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]
    
    print(f"Loading PDF: {file_name}")
    print(f"Start page: {start_page}, Language: {pdf_language}")

    try:
        # Read PDF text with parallel processing
        pages_data, use_ocr, ocr_language = read_pdf_text(
            file_path=file_path, 
            pdf_language=pdf_language, 
            start_page=start_page
        )
        
        if not pages_data:
            print("No pages could be processed")
            return [], ocr_language
        
        print(f"Creating document objects from {len(pages_data)} pages...")
        
        # Create Document objects with text cleaning
        docs = []
        for page_data in pages_data:
            text = page_data['text']
            
            if text and text.strip():  # Only add non-empty pages
                # Apply light cleaning - be careful not to break section detection
                cleaned_text = clean_text(text)
                
                if len(cleaned_text.strip()) > 10:  # Minimum content threshold
                    doc = Document(
                        page_content=cleaned_text,
                        metadata={'page': page_data['page_num']}
                    )
                    docs.append(doc)

        if not docs:
            print("No valid document content found after cleaning")
            return [], ocr_language
        
        print(f"Created {len(docs)} valid documents")

        # Enhanced section detection
        print("Detecting sections...")
        page_sections = detect_sections(docs)

        # Split documents into chunks
        print(f"Splitting documents into chunks (size: {chunk_size}, overlap: {chunk_overlap})...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = splitter.split_documents(docs)
        print(f"Created {len(chunks)} chunks")

        # Format chunks with metadata
        formatted_chunks = []
        skipped_chunks = 0
        
        for i, chunk in enumerate(chunks):
            text = chunk.page_content.strip()
            
            if not text or len(text) < 20:  # Skip very short chunks
                skipped_chunks += 1
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
                logical_page = physical_page_number - start_page + 1 if start_page > 0 else physical_page_number 

            # Find current section by looking backwards from current page
            current_section = ""
            for p in range(pdf_page, -1, -1):
                if p in page_sections:
                    current_section = page_sections[p]
                    break

            # Only add chunks with meaningful content
            word_count = len(text.split())
            if word_count >= 5:  # At least 5 words
                formatted_chunks.append({
                    "id": f"{base_name}-vec{len(formatted_chunks)+1}",  # Sequential numbering
                    "text": text,
                    "page": logical_page,
                    "section": current_section,
                })

        print(f"Successfully processed {len(formatted_chunks)} chunks from {len(docs)} pages")
        if skipped_chunks > 0:
            print(f"Skipped {skipped_chunks} chunks that were too short")
            
        return formatted_chunks, ocr_language

    except Exception as e:
        print(f"Error while loading file: {e}")
        import traceback
        traceback.print_exc()
        return [], "eng"