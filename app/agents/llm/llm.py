from google import genai
from google.genai import types
import time 
import random

from app.config.config import GOOGLE_API_KEY


client = genai.Client(api_key=GOOGLE_API_KEY)


class GeminiLLM:

    @staticmethod
    def get_response(prompt, query, chat_history):

        chat_history = chat_history["meta"]["content"]["conversation"]
        chat_history = manage_chat_history(chat_history)

        contents = []
        for msg in chat_history:
            content_item = {"role": msg["role"], "parts": [{"text": msg["content"]}]}

            if msg["role"] == "assistant" and "used_context" in msg:
                content_item["parts"].append(
                    {"text": f"Context: {msg['used_context']}"}
                )

            contents.append(content_item)

        contents.append({"role": "user", "parts": [{"text": prompt}]})
        
        print(contents)
        
        retries = 3
        
        for attempt in range(retries):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=(
                            """ 
                            You are an AI assistant that helps users learn from textbooks and reliable web sources.
                            When using online information, Keep answers short , concise and aligned with model answers.
                            Match their key terms, phrasing, and structure exactly when available (e.g., 'It failed because...'). 
                            Avoid extra background, summaries, or phrases like 'consult the textbook' unless asked.
                            Clearly state the purpose and result in cause-effect questions. If a question is unclear or broad, ask for clarification.
                            If the user asks for answers for the given context feel free to provide them without hesitating
                            You do not have persistent memory. However, you can remember information from earlier messages in this session if the user provides them.
                            If a user asks for their name or other details they told you earlier in the current conversation, you should respond correctly without saying you lack memory.
                            Avoid repeating phrases like “I do not have memory.” Just answer based on the current conversation.
                            
                            """
                        )
                    ),
                )

                full_response = response.candidates[0].content.parts[0].text

                return full_response
            except Exception as e:
                if "503" in str(e):
                    wait_time = 2 ** attempt + random.random()
                    print(f"503 received. Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
                elif "429" in str(e):
                    return "Quota exhausted or rate-limited. Try later." 
                else:
                    return f"LLM Error : {e}"    
        return "⚠️ Gemini is overloaded. Please try again soon" 

    @staticmethod
    def generate_title(message):
        prompt = f"Summarize the user's message into a short, relevant title. No punctuation, no quotes.:\n\nUser: {message}"

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=10, temperature=0.3),
        )

        return response.text.strip().title()


def estimate_tokens(text):
    return int(len(text.split()) * 1.3)


def manage_chat_history(chat_history):
    from app.agents.chat_bot_agent.tools.summarizer import Summarizer

    updated_history = []
    total_tokens = 0
    context_tokens = 0
    context_buffer = []

    max_total_tokens = 50000
    max_context_tokens = 5000

    for msg in reversed(chat_history):
        content = msg["content"]
        token_count = estimate_tokens(content)

        if msg["role"] == "assistant" and "used_context" in msg:
            used_ctx = msg["used_context"]
            used_text = ""

            if isinstance(used_ctx, list):
                used_text = " ".join(ctx["text"] for ctx in used_ctx)
            elif isinstance(used_ctx, str):
                used_text = used_ctx

            ctx_token_count = estimate_tokens(used_text)

            if context_tokens + ctx_token_count > max_context_tokens:
                context_buffer.append(used_text)
                msg.pop("used_context", None)
            else:
                context_tokens += ctx_token_count

        total_tokens += token_count

        updated_history.append(msg)

    updated_history.reverse()

    if total_tokens > max_total_tokens:
        print("Summarizing old messages due to total token overflow...")

        text_to_summarize = " ".join([msg["content"] for msg in updated_history[:-10]])
        summary = Summarizer.get_summerize_text(text_to_summarize)

        updated_history = [
            {"role": "system", "content": f"Summary: {summary}"}
        ] + updated_history[-10:]

    if context_buffer:
        context_summary = Summarizer.get_summerize_text(" ".join(context_buffer))
        updated_history.append(
            {
                "role": "system",
                "content": "Summary of old context:",
                "used_context": context_summary,
            }
        )

    return updated_history


