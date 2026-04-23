from pathlib import Path
p = Path("data/vectorstore")
print(p.exists())
print(list(p.iterdir()))