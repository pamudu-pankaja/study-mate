import google.generativeai as genai
import os
from app.config.config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)

def list_supported_models():
    """Prints all models supported by the Gemini API."""
    print("Available Gemini API models:")
    for model in genai.list_models():
        # Filter for models that support generating content
        if 'generateContent' in model.supported_generation_methods:
            print(model.name)
        # Filter for models that support embeddings
        elif 'embedContent' in model.supported_generation_methods:
            print(model.name)

list_supported_models()
