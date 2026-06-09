import os
import json

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
                text = f.read()
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