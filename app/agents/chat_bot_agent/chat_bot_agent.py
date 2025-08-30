from app.agents.chat_bot_agent.tool_handler import ToolHandle
from app.agents.llm.llm import GeminiLLM
import re


class ChatBotAgent:
    @staticmethod
    def get_response(query, path, chat_history ,book_name=None ):

        print(
            f"Answering using {'LLM Knowledge' if path is None else path.capitalize() + 'Search'}..."
        )

        data = ToolHandle.get_context(query, path, book_name)

        prompt = ""
        if path == "vector":
            
            from app.agents.chat_bot_agent.tools.summarizer import Summarizer
            
            # data  = Summarizer.get_summerize_text(data,amount=3)
            
            prompt = (
                query
                if not data
                else f"""
You are a helpful assistant extracting answers from context for a user's query.

Use the provided context (retrieved via a vector search or a web search) to answer the user query and Respond in the user's query language and translate only if needed.
If no context is given, use your own knowledge and memory to answer the question clearly , But mentione that you have used your own knowledge to answer the query.

Context: {data} 

User Query: {query}

Follow this exact format for the response:

Answer:
- If the users query contains more than one quation you need to answer all of them do not skip any of the quations. List the answers in oder.
- A short, direct answer to the question. Focus only on what's asked. And do not mention that you have extracted this answer from a context.
- If only the user is asking for a explained answer , make sure to explain the answer and the quation more clearly with more words.
- If the provided contet does not contain information about the quation , tell the users that "we couldnt find the information to answer your quation with in your book". 
- If the provided context dosen't match the given quation at all . check the previous conversatino history for the answer, but if that did not worked either tell the user to be more spesific.


Pages and Sections: Format it exactly like this, using bullet points
- 📄 Pages: Only the page numbers that were used to get the answer,
- 📚 Sections: No extra explanation Just the sections. Use Only 1-2 sections titles that were used to get the answer. Use the given sections . But if the sections are not given , What might be the section for the given context depending on the examples in the given context (e.g."3.2 Engagement in Public Debates","Coal Industry","Industrial Revolution"," Receiving of Independence to Sri Lanka"," Impact on the Society"). 
                        
                        """
            )
        if path == None:
            prompt = f"""                       
Query :
{query}"""
        if path == "web":
            prompt = f""" 
You are an assistant with access to the following search results. Your task is to answer the user's query by using the information available below. If the answer is incomplete or missing information, use whatever is available to provide the most relevant response. Please answer to the best of your ability based on what you know.

Here are the search results:
{data}

Question: {query}

Follow this exact format for the response:

Answer(Just include the answer only do not include the key word "Answer")

Used Web Pages:
- Include the links of the websites you used to generate the answer .
- The links should be in a oder(Maximum 5 links).
Example : [WebsiteName](https://websitename.com) 
"""

        result = GeminiLLM.get_response(prompt, query , chat_history)
        return {
            "reply" : result,
            "context": data if path != None else None
        }

