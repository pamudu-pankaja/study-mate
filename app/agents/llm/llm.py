from google import genai
from google.genai import types
from app.config.config import GOOGLE_API_KEY

client = genai.Client(api_key=GOOGLE_API_KEY)

chat_history = []


class GeminiLLM:

    @staticmethod
    def get_response(prompt, query):

        contents = []

        if len(chat_history) > 2:
            older_history = chat_history[:-2]
            recent_history = chat_history[-2:]

            history_text = "\n".join(
                [msg["role"] + " : " + msg["content"] for msg in older_history]
            )
            from app.agents.chat_bot_agent.tools.summarizer import Summarizer

            summary = Summarizer.get_summerize_text(history_text)

            contents.append(
                {
                    "role": "user",
                    "parts": [{"text": f"Summary of previous conversation: {summary}"}],
                }
            )

            for msg in recent_history:
                contents.append(
                    {"role": msg["role"], "parts": [{"text": msg["content"]}]}
                )
        else:
            for msg in chat_history:
                contents.append(
                    {"role": msg["role"], "parts": [{"text": msg["content"]}]}
                )

        contents.append({"role": "user", "parts": [{"text": prompt}]})
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are an AI assistant that helps users learn from textbooks and reliable web sources. When using online information, Keep answers short , concise and aligned with model answers. Match their key terms, phrasing, and structure exactly when available (e.g., 'It failed because...'). Avoid extra background, summaries, or phrases like 'consult the textbook' unless asked. Clearly state the purpose and result in cause-effect questions. If a question is unclear or broad, ask for clarification."
                    )
                ),
            )

            full_response = response.candidates[0].content.parts[0].text

            answer_only = (
                full_response.split("Context:")[0].replace("Answer:", "").strip()
            )

            chat_history.append({"role": "model", "content": answer_only})
            chat_history.append({"role": "model", "content": query})

            return full_response
        except Exception as e:
            return f"LLM Error : {e}"
