class RAGAgent(): #RAGAgent is more procedural than autonomous
    #MAJOR FUNCs
    @staticmethod
    def import_file(file_path ,index_name, chunk_size=250 ,chunk_overlap=20):
        chunks=RAGAgent.get_chunks(file_path,chunk_size,chunk_overlap)
        RAGAgent.chunk_embedder(chunks)
        print(RAGAgent.upsert_chunks(chunks,index_name))
    
    @staticmethod
    def vector_search(query,inde_name):
        from agents.rag_agent.vector_store import  vectore_search
        result = vectore_search.search(query,inde_name)
        return result

    #MINOR FUNCs
    @staticmethod
    def get_chunks(file_path , chunk_size=250 ,chunk_overlap=20):
        from agents.rag_agent.vector_store import  file_load
        chunks = file_load.load_pdf(file_path,chunk_size,chunk_overlap)  
        return chunks
    
    @staticmethod
    def chunk_embedder(chunks):
        from agents.rag_agent.vector_store import embedder
        embed = embedder.Embedding()
        embeddings = embed.get_embedding_chunks(chunks)
        return embeddings
    
    @staticmethod
    def upsert_chunks(chunks,index_name):
        from agents.rag_agent.vector_store import pinecorn_client
        db = pinecorn_client.pinecone_db()
        print(db.create_index(index_name))
        print(db.upsert(chunks,index_name))


    

    
    
     