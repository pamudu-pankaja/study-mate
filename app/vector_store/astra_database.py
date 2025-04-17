from app.config import ASTRA_DB_TOKEN,ASTRA_DB_END_POINT,ASTRA_DB_COLLECTION,GOOGLE_API_KEY

class astra_db():

    def load_pdf(self,file_path,chunk_size,chunk_overlap):
        from langchain_community.document_loaders import PyPDFLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        try:
            loader = PyPDFLoader(file_path=file_path)
            docs = loader.load()

            splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                model_name="text-embedding-004",
                chunk_size = chunk_size,
                chunk_overlap = chunk_overlap
            )

            chunks = splitter.split_documents(docs)
            return chunks  
        except Exception as e:
            return f"Error while loading file : {e}"      

    def store_data(self,data,collection_name):
        from langchain_astradb import AstraDBVectorStore
        from langchain_openai import OpenAIEmbeddings

        
        try:
            embedding = OpenAIEmbeddings()
        
            vstore = AstraDBVectorStore(
                embedding=embedding,
                collection_name=collection_name,
                token=ASTRA_DB_TOKEN,
                api_endpoint=ASTRA_DB_END_POINT
            )
            
            return "Storing successful ✅"
        except Exception as e:
            return f"Error while storing data : {e}"