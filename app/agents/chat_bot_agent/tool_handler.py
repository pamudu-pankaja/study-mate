class ToolHandle():
    #MAIN FUNC
    @staticmethod
    def get_context(query,path,index_name):
        print(path)
        results = ToolHandle.query_handle(query,path,index_name)
        return results

    #MINOR FUNC
    @staticmethod
    def query_handle(query,path,index_name):
        if path == 'translate':
            from agents.chat_bot_agent.tools.translator import translate_to_english
            translated_query = translate_to_english(query)
            new_path = ToolHandle.tool_path(translated_query)
            return ToolHandle.query_handle(translated_query,new_path,index_name)
        
        if path == "web":
            from agents.web_search.web_agent import web_search
            from agents.chat_bot_agent.tools.summarizer import Summarizer
            search=web_search(query)
            result = Summarizer.get_summerize_result(search)
            return result
        
        if path == 'vector':
            from agents import RAGAgent
            from agents.chat_bot_agent.tools.summarizer import Summarizer

            rag = RAGAgent()
            result = rag.vector_search(query,index_name)
            return result
        
        else: 
            return None
        
            
            
