# Project 1 Planning: The Unofficial Guide

---

## Domain

This project builds a RAG system over Active Directory attack and defense knowledge drawn from MITRE ATT&CK and CISA advisories. This knowledge exists across dozens of scattered technical pages and this makes security practitioners waste time cross-referencing multiple sources to answer questions like "how is this attack detected?" or "what mitigations exist?" A searchable, grounded Q&A system makes this operationally useful.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | MITRE ATT&CK | Kerberoasting (T1558.003) | https://attack.mitre.org/techniques/T1558/003/ |
| 2 | MITRE ATT&CK | AS-REP Roasting (T1558.004) | https://attack.mitre.org/techniques/T1558/004/ |
| 3 | MITRE ATT&CK | Pass-the-Hash (T1550.002) | https://attack.mitre.org/techniques/T1550/002/ |
| 4 | MITRE ATT&CK | Password Spraying (T1110.003) | https://attack.mitre.org/techniques/T1110/003/ |
| 5 | MITRE ATT&CK | Permission Groups Discovery (T1069) | https://attack.mitre.org/techniques/T1069/ |
| 6 | MITRE ATT&CK | Valid Accounts (T1078) | https://attack.mitre.org/techniques/T1078/ |
| 7 | MITRE ATT&CK | OS Credential Dumping (T1003) | https://attack.mitre.org/techniques/T1003/ |
| 8 | MITRE ATT&CK | Access Token Manipulation (T1134) | https://attack.mitre.org/techniques/T1134/ |
| 9 | MITRE ATT&CK | Account Discovery (T1087) | https://attack.mitre.org/techniques/T1087/ |
| 10 | CISA | AD Security Advisory (AA21-008a) | https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-008a |

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Reasoning:** MITRE pages are structured into discrete sections (description, procedure examples, mitigations, detections). Paragraph-based splitting is used first to respect those boundaries, then fixed-size chunking (500 chars) is applied within paragraphs that are too long. 100-character overlap ensures that information spanning a chunk boundary — like a mitigation technique that references the attack described just before it — isn't lost. 500 characters is large enough to carry semantic meaning per chunk but small enough that retrieval stays precise.

---

## Retrieval Approach

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers (runs locally, no API key)

**Top-k:** 5

**Production tradeoff reflection:** For a production deployment I'd evaluate text-embedding-3-small (OpenAI) for higher accuracy on technical security text, but it adds API cost and latency. For a multilingual deployment covering non-English threat intel, a multilingual-e5 model would be worth the tradeoff. all-MiniLM-L6-v2 is the right call here — free, fast, and the domain is English-only.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | How does Kerberoasting work? | Attackers request service tickets for SPNs and crack them offline to recover plaintext credentials |
| 2 | What mitigations exist for AS-REP Roasting? | Require Kerberos pre-authentication for all accounts; use strong passwords on accounts that must have it disabled |
| 3 | How is Pass-the-Hash detected? | Monitor for logon events using NTLM where credentials don't match the source host; Event ID 4624 logon type 3 |
| 4 | What is Password Spraying and how does it differ from brute force? | Password spraying tries one password across many accounts to avoid lockouts; brute force tries many passwords on one account |
| 5 | What does OS credential dumping involve? | Extracting credential material from LSASS memory, SAM database, or NTDS.dit using tools like Mimikatz |

---

## Anticipated Challenges

1. **Chunk boundary splitting mitigations from detections** — MITRE pages list mitigations and detections in separate sections, but if a chunk ends mid-mitigation, retrieval may return an incomplete answer. Paragraph-based splitting should reduce this but won't eliminate it entirely.

2. **Short procedure example chunks carrying no semantic signal** — Some MITRE procedure examples are one sentence referencing a specific APT group. These chunks may match queries on keyword overlap but provide no actionable answer, diluting retrieval quality.

---

## Architecture
documents/
*.txt, *.pdf
|
v
[Ingestion] — Python, pdfplumber for PDFs
|
v
[Chunking] — paragraph split → fixed 500-char chunks, 100-char overlap
|
v
[Embedding] — sentence-transformers (all-MiniLM-L6-v2)
|
v
[Vector Store] — ChromaDB (local), metadata: source filename + chunk index
|
v
[Retrieval] — top-5 semantic search
|
v
[Generation] — Groq (llama-3.3-70b-versatile), grounded prompt, source attribution
|
v
[Interface] — Gradio web UI

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
Give Claude the Documents section (file types: .txt and .pdf) and the Chunking Strategy section. Ask it to implement `ingest.py` with a `load_documents()` function and a `chunk_text()` function that does paragraph splitting first, then fixed 500-char chunking with 100-char overlap. Verify output by printing 5 chunks and confirming none are fragments or HTML artifacts.

**Milestone 4 — Embedding and retrieval:**
Give Claude the Architecture diagram and Retrieval Approach section. Ask it to implement `embed.py` that loads chunks from `ingest.py`, embeds with all-MiniLM-L6-v2, and stores in ChromaDB with source filename metadata. Ask it to implement a `retrieve(query, k=5)` function. Verify by running 3 eval questions and checking distance scores are below 0.5.

**Milestone 5 — Generation and interface:**
Give Claude the full Architecture diagram and the grounding requirement (answer from retrieved context only, cite source filenames). Ask it to implement `generate.py` with a prompt template that enforces grounding and a `ask(question)` function returning `{answer, sources}`. Then ask it to implement `app.py` as a Gradio UI wired to `ask()`. Verify by asking an out-of-scope question and confirming the system declines rather than hallucinating.