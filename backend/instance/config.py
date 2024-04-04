from dotenv import load_dotenv
import os
load_dotenv(".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")