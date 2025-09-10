from pinecone import Pinecone, ServerlessSpec
from app.config.config import PINECORN_API_KEY
import time
import numpy as np

pc = Pinecone(api_key=PINECORN_API_KEY)

class pinecone_db:
    @staticmethod
    def create_index(index_name):
        """Create Pinecone index with proper error handling"""
        try:
            if index_name not in pc.list_indexes().names():
                print(f"Creating new index: {index_name}")
                pc.create_index(
                    name=index_name,
                    dimension=768,
                    metric="euclidean",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
                print(f"Index {index_name} created successfully")
            else:
                print(f"Index {index_name} already exists")
            return f"Successfully created the index : {index_name}"
        except Exception as e:
            if "ALREADY_EXISTS" in str(e):
                print(f"Index {index_name} already exists")
                return f"Index {index_name} already exists"
            else:
                print(f"Error creating index {index_name}: {e}")
                return f"Error while creating index: {e}"

    @staticmethod
    def create_embedding_text(chunk_data):
        """Create enriched text for embedding with metadata"""
        text = chunk_data.get("text", "")
        section = chunk_data.get("section", "")
        page = chunk_data.get("page", "")

        # Clean up the text
        if not text or not text.strip():
            return ""
            
        text = text.strip()

        # Build enriched text with context
        if section and page:
            return f"Section: {section} | Page: {page} | Content: {text}"
        elif section:
            return f"Section: {section} | Content: {text}"
        elif page:
            return f"Page: {page} | Content: {text}"
        else:
            return text

    @staticmethod
    def validate_embedding(embedding, embedding_id):
        """Validate embedding dimensions and values"""
        if embedding is None:
            print(f"Embedding is None for id {embedding_id}")
            return False
            
        if not isinstance(embedding, (list, np.ndarray)):
            print(f"Embedding is not a list or array for id {embedding_id}, got {type(embedding)}")
            return False
            
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
            
        if not isinstance(embedding, list):
            print(f"Cannot convert embedding to list for id {embedding_id}")
            return False
            
        if len(embedding) != 768:
            print(f"Invalid embedding dimension for id {embedding_id}: expected 768, got {len(embedding)}")
            return False
            
        # Check for NaN or infinite values
        try:
            if any(not isinstance(x, (int, float)) or np.isnan(x) or np.isinf(x) for x in embedding):
                print(f"Embedding contains invalid values (NaN/Inf) for id {embedding_id}")
                return False
        except (TypeError, ValueError) as e:
            print(f"Error validating embedding values for id {embedding_id}: {e}")
            return False
            
        return True

    @staticmethod
    def upsert(data, namespace, ocr_language, index_name="text-books", batch_size=500):
        """Upsert data to Pinecone with improved error handling and validation"""
        
        # Create index first
        create_result = pinecone_db.create_index(index_name)
        if "Error" in create_result:
            return create_result

        from app.agents.rag_agent.vector_store.embedder import Embed_text

        try:
            # Validate input data
            if not data:
                print("No data provided for upserting")
                return "Error: No data provided"
                
            # Filter and validate data structure
            valid_data = []
            for i, d in enumerate(data):
                if not isinstance(d, dict):
                    print(f"Skipping item {i}: not a dictionary")
                    continue
                if "text" not in d or "id" not in d:
                    print(f"Skipping item {i}: missing 'text' or 'id' field")
                    continue
                if not d["text"] or not d["text"].strip():
                    print(f"Skipping item {i}: empty text content")
                    continue
                valid_data.append(d)

            if not valid_data:
                print("No valid data items found after filtering")
                return "Error: No valid data items found"

            print(f"Processing {len(valid_data)} valid items out of {len(data)} total items")

            # Create enriched embedding texts
            embedding_texts = []
            for d in valid_data:
                enriched_text = pinecone_db.create_embedding_text(d)
                if enriched_text:
                    embedding_texts.append(enriched_text)
                else:
                    print(f"Warning: Empty enriched text for item {d.get('id', 'unknown')}")
                    embedding_texts.append(d.get("text", ""))

            if not embedding_texts:
                print("No valid embedding texts created")
                return "Error: No valid embedding texts"

            print(f"Embedding {len(embedding_texts)} text chunks...")
            embeddings = Embed_text.embed_chunks(embedding_texts, ocr_language)

            # Check for embedding errors
            if isinstance(embeddings, str) and embeddings.startswith("StudyMate Error"):
                print(f"Embedding error: {embeddings}")
                return embeddings

            if not embeddings:
                print("No embeddings returned from embedding service")
                return "Error: No embeddings generated"

            print(f"Generated {len(embeddings)} embeddings")

            # Validate embedding count matches data count
            if len(embeddings) != len(valid_data):
                print(f"Error: Mismatch between data ({len(valid_data)}) and embeddings ({len(embeddings)})")
                return f"Error: Mismatch between data ({len(valid_data)}) and embeddings ({len(embeddings)})"

            # Create and validate vectors
            vectors = []
            invalid_count = 0
            
            for d, e in zip(valid_data, embeddings):
                embedding_id = str(d["id"])
                
                if pinecone_db.validate_embedding(e, embedding_id):
                    # Convert to list if it's a numpy array
                    if isinstance(e, np.ndarray):
                        e = e.tolist()
                        
                    vectors.append({
                        "id": embedding_id,
                        "values": e,
                        "metadata": {
                            "text": str(d["text"]),  
                            "page": str(d.get("page", "")),
                            "section": str(d.get("section", "")),  
                        },
                    })
                else:
                    invalid_count += 1
                    print(f"Invalid embedding for id {embedding_id}. Skipping...")

            if invalid_count > 0:
                print(f"Skipped {invalid_count} invalid embeddings out of {len(embeddings)} total")

            if not vectors:
                print("No valid vectors to upsert after validation")
                return "Error: No valid vectors to upsert after validation"

            print(f"Prepared {len(vectors)} valid vectors for upserting")

            # Wait for index to be ready
            print("Waiting for index to be ready...")
            max_wait_time = 300  # 5 minutes max
            wait_start = time.time()
            
            while not pc.describe_index(index_name).status["ready"]:
                if time.time() - wait_start > max_wait_time:
                    return "Error: Index creation timeout"
                time.sleep(2)

            index = pc.Index(index_name)

            # Batch upsert with progress tracking
            print(f"Starting upsert in batches of {batch_size}...")
            total_upserted = 0
            total_batches = (len(vectors) + batch_size - 1) // batch_size
            
            for i in range(0, len(vectors), batch_size):
                batch_vectors = vectors[i : i + batch_size]
                batch_num = i // batch_size + 1

                attempt = 0
                max_attempts = 3
                success = False
                
                while attempt < max_attempts and not success:
                    try:
                        res = index.upsert(vectors=batch_vectors, namespace=namespace)
                        total_upserted += len(batch_vectors)
                        
                        # Log progress every 5 batches or on last batch
                        if batch_num % 5 == 0 or batch_num == total_batches:
                            print(f"Upserted batch {batch_num}/{total_batches}: {len(batch_vectors)} vectors")
                            
                        if hasattr(res, 'upserted_count'):
                            print(f"Pinecone confirmed {res.upserted_count} vectors upserted")
                        
                        success = True
                        
                    except Exception as e:
                        attempt += 1
                        wait_time = min(60, 2**attempt)
                        print(f"Error on upsert batch {batch_num} (attempt {attempt}): {e}")
                        
                        if attempt < max_attempts:
                            print(f"Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            print(f"Failed to upsert batch {batch_num} after {max_attempts} attempts")
                            return f"Error: Failed to upsert batch {batch_num} after {max_attempts} attempts: {e}"

            print(f"SUCCESS: {total_upserted} total vectors upserted to namespace '{namespace}'")
            print(f"Index '{index_name}' now contains the embedded document chunks")

            return "success"

        except Exception as e:
            print(f"Critical error during upsert process: {e}")
            import traceback
            traceback.print_exc()
            return f"Error during upsert process: {e}"