from dotenv import load_dotenv
import os

# modify file to read env vars from the environemnt using os.environ.get("VAR-NAME")

load_dotenv(".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
VECTOR_DB_HOSTNAME = os.getenv("VECTOR_DB_HOSTNAME", "vectordb")