class ToolHandle():
    def tool_path(query):
        from tools.is_english import is_english
        query = query.lower()

        if any(word in query for word in ['web search','now','latest','recently']):
            return 'web'
        if any(word in query for word in['history','who is','explain','describe','vector_search']):
            return 'vector'
        if is_english(query) is not True:
            return 'translate'
        else:
            return "llm"
    
    def query_handle(query,path,index_name):
        if path == 'translate':
            from tools.translator import translate_to_english
            translated_query = translate_to_english(query)
            new_path = ToolHandle.tool_path(translated_query)
            return ToolHandle.query_handle(translated_query,new_path,index_name)
        
        elif path == 'vector':
            from agents import RAGAgent
            rag = RAGAgent()
            result = rag.vector_search(query,index_name)
            return result
        
        elif path =="llm":
            return None
        
            
            
