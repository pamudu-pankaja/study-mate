from dotenv import load_dotenv

import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECORN_API_KEY = os.getenv("PINECORN_API_KEY")