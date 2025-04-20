class ToolHandle():
    #MAIN FUNC
    @staticmethod
    def get_context(query,index_name):
        path = ToolHandle.tool_path(query)
        results = ToolHandle.query_handle(query,path,index_name)
        return results

    #MINOR FUNC
    @staticmethod
    def tool_path(query):
        from agents.chat_bot_agent.tools.is_english import is_english
        query = query.lower()

        if any(word in query for word in ['web search','now','latest','recently']):
            return 'web'
        if any(word in query for word in['history','who is','explain','describe','vector_search']):
            return 'vector'
        if is_english(query) is False:
            return 'translate'
        else:
            return "llm"
        
    @staticmethod
    def query_handle(query,path,index_name):
        if path == 'translate':
            from agents.chat_bot_agent.tools.translator import translate_to_english
            translated_query = translate_to_english(query)
            new_path = ToolHandle.tool_path(translated_query)
            return ToolHandle.query_handle(translated_query,new_path,index_name)
        
        elif path == 'vector':
            from agents import RAGAgent
            rag = RAGAgent()
            result = rag.vector_search(query,index_name)
            return result
        
        elif path == "web":
            from agents.web_search.web_agent import web_search
            from agents.chat_bot_agent.tools.summarizer import get_summerize_result
            search=web_search(query)
            result = get_summerize_result(search)
            return result
        
        elif path =="llm":
            return None
        
            
            
