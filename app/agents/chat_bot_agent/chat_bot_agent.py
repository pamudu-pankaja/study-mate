from app.agents.chat_bot_agent.tool_handler import ToolHandle
from app.agents.llm.llm import GeminiLLM 

class ChatBotAgent():
    @staticmethod
    def get_response(query,path,index_name = None):
        print(f"Answering using {"LLM Knowledge" if path == None else path.capitalize() + " Search"}")
        data = ToolHandle.get_context(query,path,index_name)
        result = GeminiLLM.get_response(query,context=f"{data}")
        return result