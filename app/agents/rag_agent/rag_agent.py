class RAGAgent:  # RAGAgent is more procedural than autonomous
    # MAJOR FUNCs
    @staticmethod
    def import_file(file_path, book_name, start_page):
        try:
            print("Getting Chunks...")
            chunks = RAGAgent.get_chunks(file_path, book_name, start_page)

            # RAGAgent.chunk_embedder(chunks)
            result = RAGAgent.upsert_chunks(chunks, book_name)
            return result

        except Exception as e:
            print(e)

    @staticmethod
    def vector_search(query, book_name):
        from app.agents.rag_agent.vector_store import vectore_search

        result = vectore_search.search(query, book_name)
        return result

    # MINOR FUNCs
    @staticmethod
    def get_chunks(file_path, book_name, start_page):
        from app.agents.rag_agent.vector_store import file_load

        chunks = file_load.load_pdf(file_path, book_name, start_page=start_page)
        return chunks

    # @staticmethod
    # def chunk_embedder(chunks):
    #     from app.agents.rag_agent.vector_store import embedder

    #     embed = embedder.Embedding()
    #     embeddings = embed.get_embedding_chunks(chunks)
    #     return embeddings

    @staticmethod
    def upsert_chunks(chunks, book_name):
        from app.agents.rag_agent.vector_store import pinecorn_client

        db = pinecorn_client.pinecone_db()
        return db.upsert(chunks, book_name)
