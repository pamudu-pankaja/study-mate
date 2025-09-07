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

def embed_sentences(texts, tokenizer , model , batch_size=32 ):
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        inputs = tokenizer(batch, return_tensors="pt", truncation=True, padding=True).to(DEVICE)
        with torch.no_grad():
            outputs = model(**inputs)
        batch_emb = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        embeddings.append(batch_emb)
    return np.vstack(embeddings)

def embed_sentence(text):
    return embed_sentences([text])[0]

class Embed_text:    
    @staticmethod
    def embed_query(query ,lang):
        SINHALA_MODEL = "./models/SinhalaBERTo/model.safetensors"
        MULTILANG_MODEL = "./models/LaBSE/model.safetensors"
        
        if lang == 'eng':
            return Gemini_Embedding.embed_query(query)
        elif lang == 'sin' and os.path.exists(SINHALA_MODEL):
            return SinhalaBERTo_Embedding.embed_query(query)
        elif os.path.exists(MULTILANG_MODEL):
            return LaBSE_Embedding.embed_query(query)
        else:
            return "StudyMate Error : There was a problem with embedding models, make sure to download the correct model before using lanugages other than English."
            
    @staticmethod
    def embed_chunks(chunks , lang):
        SINHALA_MODEL = "./models/SinhalaBERTo/model.safetensors"
        MULTILANG_MODEL = "./models/LaBSE/model.safetensors"
        
        if lang == 'eng':
            return Gemini_Embedding.embed_chunks(chunks)
        elif lang == 'sin' and os.path.exists(SINHALA_MODEL):
            return SinhalaBERTo_Embedding.embed_chunks(chunks)
        elif os.path.exists(MULTILANG_MODEL):
            return LaBSE_Embedding.embed_chunks(chunks)
        else:
            return "StudyMate Error : There was a problem with embedding models, make sure to download the correct model before using lanugages other than English."
            


class Gemini_Embedding:
    @staticmethod
    def embed_query(query):
        query = query.lower()
        try:
            result = client.models.embed_content(
                model="text-embedding-004",
                contents=f"{query}",
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
            )
            return result.embeddings[0].values
        except Exception as e:
            return f"StudyMate Error : Error during embedding : {e}"

    @staticmethod
    def embed_chunks(chunks, batch_size=100):
        
        embeddings = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            attempt = 0
            while True:
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
                except Exception as e:
                    attempt += 1
                    wait = min(60, 2**attempt)
                    print(
                        f"Error on embedding batch {i//batch_size+1}: {e} | retrying in {wait}s"
                    )
                    time.sleep(wait)
        return embeddings


class SinhalaBERTo_Embedding:
    MODEL_PATH = "./models/SinhalaBERTo"
    tokenizer = None
    model = None

    @classmethod
    def get_model(cls):
        if cls.tokenizer is None or cls.model is None:
            cls.tokenizer = AutoTokenizer.from_pretrained(cls.MODEL_PATH)
            cls.model = AutoModel.from_pretrained(cls.MODEL_PATH)
            cls.model.to(DEVICE)
            cls.model.eval()
        return cls.tokenizer, cls.model

    @staticmethod
    def embed_query(query):
        tokenizer, model = SinhalaBERTo_Embedding.get_model()
        embeddings = embed_sentence(query, tokenizer, model)
        return embeddings

    @staticmethod
    def embed_chunks(chunks, batch_size=32):
        tokenizer, model = SinhalaBERTo_Embedding.get_model()
        embeddings = embed_sentences(chunks, tokenizer, model, batch_size)
        return embeddings


class LaBSE_Embedding:
    MODEL_PATH = "./models/LaBSE"
    tokenizer = None
    model = None

    @classmethod
    def get_model(cls):
        if cls.tokenizer is None or cls.model is None:
            cls.tokenizer = AutoTokenizer.from_pretrained(cls.MODEL_PATH)
            cls.model = AutoModel.from_pretrained(cls.MODEL_PATH)
            cls.model.to(DEVICE)
            cls.model.eval()
        return cls.tokenizer, cls.model

    @staticmethod
    def embed_query(query):
        tokenizer, model = SinhalaBERTo_Embedding.get_model()
        embeddings = embed_sentence(query, tokenizer, model)
        return embeddings

    @staticmethod
    def embed_chunks(chunks, batch_size=32):
        tokenizer, model = SinhalaBERTo_Embedding.get_model()
        embeddings = embed_sentences(chunks, tokenizer, model, batch_size)
        return embeddings


    
    
