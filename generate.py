import os
from groq import Groq
from dotenv import load_dotenv
from embed import retrieve

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a cybersecurity assistant with knowledge of Active Directory attacks and defenses.
Answer the user's question using ONLY the information provided in the context below.
If the context does not contain enough information to answer, say exactly: "I don't have enough information on that."
Always end your response with a Sources section listing the filenames the answer came from."""

def ask(question):
    results = retrieve(question, k=5)
    chunks = results["documents"][0]
    sources = list(set(m["source"] for m in results["metadatas"][0]))

    context = "\n\n---\n\n".join(
        f"Source: {results['metadatas'][0][i]['source']}\n{chunk}"
        for i, chunk in enumerate(chunks)
    )

    prompt = f"""Context:
{context}

Question: {question}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content
    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    # Quick test
    result = ask("How does Kerberoasting work?")
    print(result["answer"])
    print("\nSources:", result["sources"])