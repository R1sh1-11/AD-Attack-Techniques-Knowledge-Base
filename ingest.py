import os
import json
import re

def clean_text(text):
    # Remove reference sections
    text = re.sub(r'References\n.*', '', text, flags=re.DOTALL)
    # Remove sub-technique navigation tables
    text = re.sub(r'Other sub-techniques.*?Ccache Files\n', '', text, flags=re.DOTALL)
    # Remove ID/Name table rows like "T1558.001    Golden Ticket"
    text = re.sub(r'T\d{4}(\.\d{3})?\s+\S.*\n', '', text)
    # Remove ATT&CK ID rows like "G0096   APT41"
    text = re.sub(r'[GS]\d{4}\s+\S.*\n', '', text)
    # Remove citation numbers like [1][2]
    text = re.sub(r'\[\d+\]', '', text)
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

DOCUMENTS_DIR = "documents"
OUTPUT_FILE = "chunks.json"
CHUNK_SIZE = 500
OVERLAP = 100


def load_documents():
    documents = []
    for filename in os.listdir(DOCUMENTS_DIR):
        filepath = os.path.join(DOCUMENTS_DIR, filename)
        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()  # 1. Read the file content first
                text = clean_text(raw_text)  # 2. Clean it up
            documents.append({"source": filename, "text": text})
    print(f"Loaded {len(documents)} documents")
    return documents


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    chunks = []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    
    for paragraph in paragraphs:
        if len(paragraph) <= chunk_size:
            chunks.append(paragraph)
        else:
            start = 0
            while start < len(paragraph):
                end = start + chunk_size
                chunks.append(paragraph[start:end])
                start += chunk_size - overlap

    return chunks


def build_chunks(documents):
    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            if len(chunk) > 150:
                all_chunks.append({
                    "source": doc["source"],
                    "chunk_index": i,
                    "text": chunk
                })
    print(f"Total chunks: {len(all_chunks)}")
    return all_chunks


def inspect_chunks(chunks, n=5):
    print("\n--- Sample Chunks ---")
    import random
    sample = random.sample(chunks, min(n, len(chunks)))
    for c in sample:
        print(f"\nSource: {c['source']} | Chunk #{c['chunk_index']}")
        print(f"Length: {len(c['text'])} chars")
        print(c['text'])
        print("-" * 60)


if __name__ == "__main__":
    docs = load_documents()
    chunks = build_chunks(docs)
    inspect_chunks(chunks)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
    print(f"\nChunks saved to {OUTPUT_FILE}")
