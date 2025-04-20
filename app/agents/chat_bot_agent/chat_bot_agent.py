from agents.chat_bot_agent.tool_handler import ToolHandle
from agents.llm.llm import GeminiLLM 

class ChatBotAgent():
    @staticmethod
    def get_response(query,path,index_name = None):
        data = ToolHandle.get_context(query,path,index_name)
        print(data.get())
        result = GeminiLLM.get_response(query,context=data)
        return result