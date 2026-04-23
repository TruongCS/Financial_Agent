# ingest.py
import re
import sqlite3
import pandas as pd
from pathlib import Path
# ingest.py
import re
import sqlite3
import pandas as pd
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from langchain_huggingface import HuggingFaceEmbeddings
from config import (
    REPORT_PATH, DB_PATH, VECTORSTORE_PATH,
    EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
)


def extract_tables_to_sqlite(markdown: str, db_path: str):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)

    pattern = re.compile(r'(?:#{1,3}\s*(.+?)\n)?((?:\|.+\n)+)', re.MULTILINE)
    saved, skipped = 0, 0

    for i, match in enumerate(pattern.finditer(markdown)):
        heading  = (match.group(1) or f"table_{i}").strip()
        table_md = match.group(2)

        lines = [l.strip() for l in table_md.strip().split('\n') if l.strip()]
        lines = [l for l in lines if not re.match(r'^\|[\s\-|]+\|$', l)]
        rows  = [[cell.strip() for cell in l.strip('|').split('|')] for l in lines]

        if len(rows) < 2:
            skipped += 1
            continue

        headers = [re.sub(r'\W+', '_', col).lower().strip('_') or f"col_{j}"
                   for j, col in enumerate(rows[0])]

        # Deduplicate column names
        seen, deduped = {}, []
        for h in headers:
            if h in seen:
                seen[h] += 1
                deduped.append(f"{h}_{seen[h]}")
            else:
                seen[h] = 1
                deduped.append(h)

        df = pd.DataFrame(rows[1:], columns=deduped)
        table_name = re.sub(r'\W+', '_', heading[:50]).lower().strip('_')
        df.to_sql(table_name, con, if_exists='replace', index=False)
        saved += 1

    con.close()
    print(f"SQLite: saved {saved} tables, skipped {skipped}")


def build_vectorstore(markdown: str):
    Path(VECTORSTORE_PATH).mkdir(parents=True, exist_ok=True)

    # Remove table blocks before chunking — tables go to SQLite only
    clean_text = re.sub(r'((?:\|.+\n)+)', '', markdown)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(clean_text)
    docs   = [Document(page_content=chunk) for chunk in chunks]

    embedding   = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(docs, embedding)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"FAISS: saved {len(docs)} chunks to {VECTORSTORE_PATH}")


if __name__ == "__main__":
    print("Reading report...")
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    print("Extracting tables to SQLite...")
    extract_tables_to_sqlite(text, DB_PATH)

    print("Building vectorstore...")
    build_vectorstore(text)

    print("Ingestion complete.")
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from config import (
    REPORT_PATH, DB_PATH, VECTORSTORE_PATH,
    EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
)


def extract_tables_to_sqlite(markdown: str, db_path: str):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)

    pattern = re.compile(r'(?:#{1,3}\s*(.+?)\n)?((?:\|.+\n)+)', re.MULTILINE)
    saved, skipped = 0, 0

    for i, match in enumerate(pattern.finditer(markdown)):
        heading  = (match.group(1) or f"table_{i}").strip()
        table_md = match.group(2)

        lines = [l.strip() for l in table_md.strip().split('\n') if l.strip()]
        lines = [l for l in lines if not re.match(r'^\|[\s\-|]+\|$', l)]
        rows  = [[cell.strip() for cell in l.strip('|').split('|')] for l in lines]

        if len(rows) < 2:
            skipped += 1
            continue

        headers = [re.sub(r'\W+', '_', col).lower().strip('_') or f"col_{j}"
                   for j, col in enumerate(rows[0])]

        # Deduplicate column names
        seen, deduped = {}, []
        for h in headers:
            if h in seen:
                seen[h] += 1
                deduped.append(f"{h}_{seen[h]}")
            else:
                seen[h] = 1
                deduped.append(h)

        df = pd.DataFrame(rows[1:], columns=deduped)
        table_name = re.sub(r'\W+', '_', heading[:50]).lower().strip('_')
        df.to_sql(table_name, con, if_exists='replace', index=False)
        saved += 1

    con.close()
    print(f"SQLite: saved {saved} tables, skipped {skipped}")


def build_vectorstore(markdown: str):
    Path(VECTORSTORE_PATH).mkdir(parents=True, exist_ok=True)

    # Remove table blocks before chunking — tables go to SQLite only
    clean_text = re.sub(r'((?:\|.+\n)+)', '', markdown)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(clean_text)
    docs   = [Document(page_content=chunk) for chunk in chunks]

    embedding   = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(docs, embedding)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"FAISS: saved {len(docs)} chunks to {VECTORSTORE_PATH}")


if __name__ == "__main__":
    print("Reading report...")
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    print("Extracting tables to SQLite...")
    extract_tables_to_sqlite(text, DB_PATH)

    print("Building vectorstore...")
    build_vectorstore(text)

    print("Ingestion complete.")