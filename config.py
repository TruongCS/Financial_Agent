#Central place for all paths and settings so nothing is hardcoded:
# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR      = Path(__file__).parent
DATA_DIR      = BASE_DIR / "data"
DB_PATH       = str(DATA_DIR / "uber_financials.db")
VECTORSTORE_PATH = str(DATA_DIR / "vectorstore")
REPORT_PATH   = str(DATA_DIR / "uber_report.md")

OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL       = "openai:gpt-4o"
CHUNK_SIZE      = 500
CHUNK_OVERLAP   = 50