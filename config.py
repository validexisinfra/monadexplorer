import os

BASE_DIR = "/root/monadai"

DB_PATH = f"{BASE_DIR}/db/monad.db"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash-lite"

MCP_URL = "http://127.0.0.1:8000"
