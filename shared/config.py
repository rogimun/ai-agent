import os
import sys
import asyncio
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MCP_SERVER_URL = "http://localhost:8000/mcp"
    MODEL_NAME = "gpt-4o-mini"
    
settings = Settings()