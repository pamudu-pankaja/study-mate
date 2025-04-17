from dotenv import load_dotenv

import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ASTRA_DB_TOKEN = os.getenv("ASTRA_DATABASE_TOKEN")
ASTRA_DB_END_POINT = os.getenv("ASTRA_DATABASE_END_POINT")
ASTRA_DB_COLLECTION = os.getenv("ASTRA_DB_COLLECTION")