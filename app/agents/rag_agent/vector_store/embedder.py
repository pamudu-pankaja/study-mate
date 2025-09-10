from google import genai
from google.genai import types
from transformers import AutoTokenizer, AutoModel
from app.config.config import GOOGLE_API_KEY
import time
import torch
import numpy as np
import os

client = genai.Client(api_key=GOOGLE_API_KEY)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")


def embed_sentences(texts, tokenizer, model, batch_size=8):
    """Embed multiple sentences using local model with proper batching"""
    if not texts:
        return np.array([])

    embeddings = []
    total_batches = (len(texts) + batch_size - 1) // batch_size

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        batch_num = i // batch_size + 1

        if batch_num % 10 == 0 or batch_num == total_batches:
            print(f"Processing embedding batch {batch_num}/{total_batches}")

        try:
            # Tokenize with consistent parameters
            inputs = tokenizer(
                batch,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512,
                add_special_tokens=True,  # Ensure consistent tokenization
            ).to(DEVICE)

            with torch.no_grad():
                outputs = model(**inputs)

                # Use mean pooling with attention mask for better representations
                # attention_mask = inputs["attention_mask"]
                # token_embeddings = outputs.last_hidden_state

                # Masked mean pooling
                # input_mask_expanded = (
                #     attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                # )
                # sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
                # sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                # batch_emb = sum_embeddings / sum_mask

                # # Normalize embeddings for better similarity calculations
                # batch_emb = torch.nn.functional.normalize(batch_emb, p=2, dim=1)
                # Instead of complex masked pooling:
                batch_emb = outputs.last_hidden_state[: , 0, :].cpu().numpy()

                from sklearn.preprocessing import normalize
                
                batch_emb = normalize(batch_emb , norm='l2')

                embeddings.append(batch_emb)

        except Exception as e:
            print(f"Error in batch {batch_num}: {e}")
            # Return zero embeddings for failed batch
            embedding_dim = 768  # Default for most BERT models
            batch_emb = np.zeros((len(batch), embedding_dim))
            embeddings.append(batch_emb)

    if not embeddings:
        return np.array([])

    return np.vstack(embeddings)


def embed_sentence(text, tokenizer, model):
    """Embed a single sentence using local model"""
    if not text or not text.strip():
        return np.zeros(768)

    result = embed_sentences([text], tokenizer, model, batch_size=1)
    return result[0] if len(result) > 0 else np.zeros(768)


class Embed_text:
    # Cache for loaded models to ensure consistency
    _model_cache = {}
    
    @staticmethod
    def embed_query(query: str, lang: str) :
        """Embed a query string based on language with consistent preprocessing"""
        if not query or not query.strip():
            return np.zeros(768).tolist()
        
        
        SINHALA_MODEL = "./models/SinhalaBERTo/model.safetensors"
        MULTILANG_MODEL = "./models/LaBSE/model.safetensors"
        
        try:
            if lang == 'eng':
                return Gemini_Embedding.embed_query(query)
            # elif lang == 'sin' and os.path.exists(SINHALA_MODEL):
            #     return LaBSE_Embedding.embed_query(query)
            elif os.path.exists(MULTILANG_MODEL):
                return LaBSE_Embedding.embed_query(query)
            else:
                return "StudyMate Error : There was a problem with embedding models, make sure to download the correct model before using languages other than English."
        except Exception as e:
            print(f"Error in embed_query: {e}")
            return f"StudyMate Error : Error during query embedding: {e}"
    
    @staticmethod
    def embed_chunks(chunks: list, lang: str):
        """Embed multiple chunks based on language with consistent preprocessing"""
        if not chunks:
            return []
        
        SINHALA_MODEL = "./models/SinhalaBERTo/model.safetensors"
        MULTILANG_MODEL = "./models/LaBSE/model.safetensors"
        
        print(f"Embedding {len(chunks)} chunks using language: {lang}")
        
        try:
            if lang == 'eng':
                return Gemini_Embedding.embed_chunks(chunks)
            # elif lang == 'sin' and os.path.exists(SINHALA_MODEL):
            #     return LaBSE_Embedding.embed_chunks(chunks)
            elif os.path.exists(MULTILANG_MODEL):
                return LaBSE_Embedding.embed_chunks(chunks)
            else:
                return "StudyMate Error : There was a problem with embedding models, make sure to download the correct model before using languages other than English."
        except Exception as e:
            print(f"Error in embed_chunks: {e}")
            return f"StudyMate Error : Error during chunk embedding: {e}"

class Gemini_Embedding:
    @staticmethod
    def embed_query(query: str):
        """Embed query using Gemini API with consistent preprocessing"""
        if not query or not query.strip():
            return np.zeros(768).tolist()        
        
        try:
            result = client.models.embed_content(
                model="text-embedding-004",
                contents=f"{query}",
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"Gemini embedding error: {e}")
            return f"StudyMate Error : Error during embedding : {e}"
    
    @staticmethod
    def embed_chunks(chunks: list, batch_size=100):
        """Embed chunks using Gemini API with proper error handling"""
        if not chunks:
            return []
        
        embeddings = []
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            batch_num = i // batch_size + 1
            
            print(f"Processing Gemini batch {batch_num}/{total_batches}")
            
            attempt = 0
            max_attempts = 3
            
            while attempt < max_attempts:
                try:
                    result = client.models.embed_content(
                        model="text-embedding-004",
                        contents=batch,
                        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
                    )
                    
                    if result and result.embeddings:
                        for embedding in result.embeddings:
                            if embedding and embedding.values:
                                embeddings.append(embedding.values)
                            else:
                                embeddings.append(None)
                        break
                    else:
                        print(f"No embeddings returned for batch {batch_num}")
                        for _ in batch:
                            embeddings.append(None)
                        break
                        
                except Exception as e:
                    attempt += 1
                    wait = min(60, 2**attempt)
                    print(f"Error on embedding batch {batch_num} (attempt {attempt}): {e}")
                    
                    if attempt < max_attempts:
                        print(f"Retrying in {wait}s...")
                        time.sleep(wait)
                    else:
                        print(f"Failed to process batch {batch_num} after {max_attempts} attempts")
                        for _ in batch:
                            embeddings.append(None)
        
        return embeddings

class SinhalaBERTo_Embedding:
    MODEL_PATH = "./models/SinhalaBERTo"
    tokenizer = None
    model = None
    
    @classmethod
    def get_model(cls):
        """Load model with proper error handling and caching"""
        cache_key = f"sinhala_bert_{cls.MODEL_PATH}"
        
        if cache_key not in Embed_text._model_cache:
            try:
                print("Loading SinhalaBERTo model...")
                tokenizer = AutoTokenizer.from_pretrained(cls.MODEL_PATH)
                model = AutoModel.from_pretrained(cls.MODEL_PATH)
                model.to(DEVICE)
                model.eval()
                
                # Cache the model to ensure consistency
                Embed_text._model_cache[cache_key] = (tokenizer, model)
                print("SinhalaBERTo model loaded successfully")
            except Exception as e:
                print(f"Error loading SinhalaBERTo model: {e}")
                raise e
        
        return Embed_text._model_cache[cache_key]
    
    @staticmethod
    def embed_query(query: str):
        """Embed query using SinhalaBERTo with consistent preprocessing"""
        if not query or not query.strip():
            return np.zeros(768).tolist()
        
        try:
            tokenizer, model = SinhalaBERTo_Embedding.get_model()
            embedding = embed_sentence(query, tokenizer, model)
            return embedding.tolist()
        except Exception as e:
            print(f"SinhalaBERTo query embedding error: {e}")
            return f"StudyMate Error : Error during SinhalaBERTo query embedding: {e}"
    
    @staticmethod
    def embed_chunks(chunks: list, batch_size=8):
        """Embed chunks using SinhalaBERTo with optimized batching and consistency"""
        if not chunks:
            return []
        
        
        try:
            tokenizer, model = SinhalaBERTo_Embedding.get_model()
            embeddings = embed_sentences(chunks, tokenizer, model, batch_size)
            
            # Proper error handling for numpy arrays
            if isinstance(embeddings, str):  # Error string returned
                return embeddings
            elif isinstance(embeddings, np.ndarray) and embeddings.size > 0:
                return embeddings.tolist()
            else:
                return []
        except Exception as e:
            print(f"SinhalaBERTo chunk embedding error: {e}")
            return f"StudyMate Error : Error during SinhalaBERTo chunk embedding: {e}"

class LaBSE_Embedding:
    MODEL_PATH = "./models/LaBSE"
    
    @classmethod
    def get_model(cls):
        """Load model with proper error handling and caching"""
        cache_key = f"labse_{cls.MODEL_PATH}"
        
        if cache_key not in Embed_text._model_cache:
            try:
                print("Loading LaBSE model...")
                tokenizer = AutoTokenizer.from_pretrained(cls.MODEL_PATH)
                model = AutoModel.from_pretrained(cls.MODEL_PATH)
                model.to(DEVICE)
                model.eval()
                
                # Cache the model to ensure consistency
                Embed_text._model_cache[cache_key] = (tokenizer, model)
                print("LaBSE model loaded successfully")
            except Exception as e:
                print(f"Error loading LaBSE model: {e}")
                raise e
        
        return Embed_text._model_cache[cache_key]
    
    @staticmethod
    def embed_query(query: str):
        """Embed query using LaBSE with consistent preprocessing"""
        if not query or not query.strip():
            # Dynamically determine dimensions
            try:
                tokenizer, model = LaBSE_Embedding.get_model()
                dummy_result = embed_sentences(["test"], tokenizer, model, batch_size=1)
                if isinstance(dummy_result, np.ndarray) and dummy_result.size > 0:
                    return np.zeros(dummy_result.shape[1]).tolist()
            except:
                pass
            return np.zeros(768).tolist()  # Fallback      
        
        try:
            tokenizer, model = LaBSE_Embedding.get_model()
            embedding = embed_sentence(query, tokenizer, model)
            return embedding.tolist()
        except Exception as e:
            print(f"LaBSE query embedding error: {e}")
            return f"StudyMate Error : Error during LaBSE query embedding: {e}"
    
    @staticmethod
    def embed_chunks(chunks: list, batch_size=8):
        """Embed chunks using LaBSE with optimized batching and consistency"""
        if not chunks:
            return []
        
        
        try:
            tokenizer, model = LaBSE_Embedding.get_model()
            embeddings = embed_sentences(chunks, tokenizer, model, batch_size)
            
            # Proper error handling for numpy arrays
            if isinstance(embeddings, str):  # Error string returned
                return embeddings
            elif isinstance(embeddings, np.ndarray) and embeddings.size > 0:
                return embeddings.tolist()
            else:
                return []
        except Exception as e:
            print(f"LaBSE chunk embedding error: {e}")
            return f"StudyMate Error : Error during LaBSE chunk embedding: {e}"

