import json
from sentence_transformers import SentenceTransformer
import chromadb

CHUNKS_FILE = "chunks.json"
COLLECTION_NAME = "ad_attacks"

client = chromadb.PersistentClient(path="./chroma_db")
model = SentenceTransformer("all-MiniLM-L6-v2")


def load_chunks():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def embed_and_store(chunks):
    collection = client.get_or_create_collection(COLLECTION_NAME)

    texts = [c["text"] for c in chunks]
    ids = [f"{c['source']}_{c['chunk_index']}" for c in chunks]
    metadatas = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks]

    print("Embedding chunks... this may take a minute")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB")
    return collection


def retrieve(query, k=5):
    collection = client.get_or_create_collection(COLLECTION_NAME)
    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    return results


def print_results(query, results):
    print(f"\nQuery: {query}")
    print("=" * 60)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances)):
        print(f"\nResult #{i+1} | Source: {meta['source']} | Distance: {round(dist, 3)}")
        print(doc[:300])
        print("-" * 60)


if __name__ == "__main__":
    chunks = load_chunks()
    embed_and_store(chunks)

    test_queries = [
        "How does Kerberoasting work?",
        "What mitigations exist for AS-REP Roasting?",
        "How is Pass-the-Hash detected?"
    ]

    for query in test_queries:
        results = retrieve(query)
        print_results(query, results)