import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MODEL_NAME = os.getenv("MODEL_NAME")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
settings = Settings()