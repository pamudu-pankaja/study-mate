class RAGAgent:  # RAGAgent is more procedural than autonomous
    # MAJOR FUNCs
    @staticmethod
    def import_file(file_path, book_name, start_page , pdf_language):
        try:
            print("Getting Chunks...")
            chunks , ocr_language = RAGAgent.get_chunks(file_path, start_page , pdf_language)

            result = RAGAgent.upsert_chunks(chunks, book_name , ocr_language)
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
    def get_chunks(file_path, start_page , pdf_language = "auto"):
        from app.agents.rag_agent.vector_store import file_load

        chunks , ocr_language = file_load.load_pdf(file_path, start_page , pdf_language)
        return chunks , ocr_language

    @staticmethod
    def upsert_chunks(chunks, book_name):
        from app.agents.rag_agent.vector_store import pinecorn_client

        db = pinecorn_client.pinecone_db()
        return db.upsert(chunks, book_name)
