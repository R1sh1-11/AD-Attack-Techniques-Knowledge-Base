# The Unofficial Guide — Project 1

---

## Domain

This system covers Active Directory attack techniques and defenses, drawn from MITRE ATT&CK technique pages and a CISA advisory. This knowledge is valuable for security practitioners and students who need to quickly answer operational questions like "how is this attack detected?" or "what mitigations exist?" : but finding answers requires manually cross-referencing dozens of scattered technical pages. This RAG system makes that knowledge searchable in plain language.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | MITRE ATT&CK | Web page | https://attack.mitre.org/techniques/T1558/003/ |
| 2 | MITRE ATT&CK | Web page | https://attack.mitre.org/techniques/T1558/004/ |
| 3 | MITRE ATT&CK | Web page | https://attack.mitre.org/techniques/T1550/002/ |
| 4 | MITRE ATT&CK | Web page | https://attack.mitre.org/techniques/T1110/003/ |
| 5 | MITRE ATT&CK | Web page | https://attack.mitre.org/techniques/T1069/ |
| 6 | MITRE ATT&CK | Web page | https://attack.mitre.org/techniques/T1078/ |
| 7 | MITRE ATT&CK | Web page | https://attack.mitre.org/techniques/T1003/ |
| 8 | MITRE ATT&CK | Web page | https://attack.mitre.org/techniques/T1134/ |
| 9 | MITRE ATT&CK | Web page | https://attack.mitre.org/techniques/T1087/ |
| 10 | CISA | Advisory PDF | https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-008a |

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Why these choices fit your documents:** MITRE pages are structured into discrete sections (description, procedure examples, mitigations, detections). The pipeline first splits on paragraph boundaries (`\n\n`) to respect those natural section breaks, then applies fixed 500-character chunking with 100-character overlap within paragraphs that exceed that size. Overlap ensures information spanning a chunk boundary such as a mitigation that references the attack described just before it is not lost. A minimum length filter of 150 characters was applied to remove short APT reference rows (e.g. "APT41 uses Mimikatz") that carried no semantic signal and degraded retrieval quality.

**Final chunk count:** 198 chunks across 10 documents

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers (local, no API key required)

**Production tradeoff reflection:** For a production deployment I would evaluate OpenAI's text-embedding-3-small for higher accuracy on technical security text, at the cost of API latency and per-token pricing. For a multilingual deployment covering non-English threat intelligence, a multilingual-e5 model would be worth the accuracy tradeoff. For domain-specific security text, a model fine-tuned on cybersecurity corpora would likely outperform a general-purpose model like all-MiniLM-L6-v2, which was trained on general web text. The local execution of all-MiniLM-L6-v2 was the right call for this project given the free tool constraint and English-only corpus.

---

## Grounded Generation

**System prompt grounding instruction:**
You are a cybersecurity assistant with knowledge of Active Directory attacks and defenses.
Answer the user's question using ONLY the information provided in the context below.
If the context does not contain enough information to answer, say exactly: "I don't have enough information on that."
Always end your response with a Sources section listing the filenames the answer came from.

**How source attribution is surfaced in the response:** Source filenames are passed to the LLM as part of each context chunk (formatted as `Source: filename.txt` before each chunk). The system prompt instructs the model to list source filenames at the end of every response. Source filenames are also returned programmatically from the `retrieve()` function and displayed separately in the Gradio UI's Sources field, independent of the LLM output.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How does Kerberoasting work? | Attacker requests TGS tickets for SPNs and cracks them offline | Correctly explained TGS request, RC4 encryption, and offline cracking | Relevant | Accurate |
| 2 | What mitigations exist for AS-REP Roasting? | Require Kerberos pre-authentication; strong passwords | Got pre-auth mitigation correct but also pulled an unrelated OS credential dumping mitigation from wrong source | Partially relevant | Partially accurate |
| 3 | How is Pass-the-Hash detected? | Monitor Event ID 4624 logon type 3, NTLM anomalies | Returned "I don't have enough information on that" | Off-target | Inaccurate |
| 4 | What is Password Spraying and how does it differ from brute force? | One password across many accounts to avoid lockouts | Correctly explained the distinction and throttling behavior | Relevant | Accurate |
| 5 | What does OS credential dumping involve? | Extracting credentials from LSASS, SAM, NTDS.dit using Mimikatz | Correct at a high level but missed specific tools and memory locations | Partially relevant | Partially accurate |

---

## Failure Case Analysis

**Question that failed:** How is Pass-the-Hash detected?

**What the system returned:** "I don't have enough information on that."

**Root cause (tied to a specific pipeline stage):** The failure originates in the chunking and retrieval stages. Pass-the-Hash detection content exists in the documents but is distributed across multiple short chunks where each chunk contains only a fragment of the detection logic (one chunk mentions NTLM monitoring, another mentions logon event correlation). No single chunk contained enough detection-specific semantic signal for the embedding model to rank it highly against a detection-focused query. The top-5 retrieved chunks were dominated by procedural description chunks rather than detection content, leaving the LLM with insufficient context to answer.

**What you would change to fix it:** Increasing chunk size for detection and mitigation sections specifically, or using section-aware chunking that keeps entire "Detection" and "Mitigation" sections as single chunks regardless of length, would likely fix this. Alternatively, supplementing MITRE pages with richer third-party writeups (e.g. SpecterOps or harmj0y blog posts) would give the embedding model more detection-specific content to retrieve from.

---

## Spec Reflection

**One way the spec helped you during implementation:** The chunking strategy section of planning.md forced an early decision to use paragraph-based splitting rather than naive fixed-size splitting. This directly shaped the implementation when retrieval quality was poor, the spec gave a clear diagnosis framework: the issue was chunk content quality, not retrieval architecture. Without having thought through chunking before coding, debugging would have been much harder.

**One way your implementation diverged from the spec, and why:** The spec anticipated clean paragraph-based chunking would produce high-quality retrievable chunks. In practice, MITRE pages are table-heavy with minimal prose, meaning most chunks were short structured rows rather than explanatory paragraphs. A 150-character minimum filter had to be added post-hoc to remove low-signal chunks as this was not in the original spec but was necessary after seeing retrieval results dominated by APT reference one-liners.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Documents section and Chunking Strategy section from planning.md, along with the pipeline architecture diagram
- *What it produced:* A complete `ingest.py` with `load_documents()`, `clean_text()`, and `chunk_text()` functions using paragraph splitting and fixed-size chunking
- *What I changed or overrode:* The initial version had no minimum chunk length filter. After seeing retrieval dominated by one-line APT reference rows, I directed Claude to add a `len(chunk) > 150` filter in `build_chunks()`. I also directed it to add regex-based cleaning for MITRE-specific boilerplate (sub-technique navigation tables, citation numbers, ATT&CK ID rows) after inspecting raw chunk output.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section, the grounding requirement (answers from retrieved context only, with source attribution), and the pipeline diagram
- *What it produced:* `generate.py` with a Groq client, a system prompt, and an `ask()` function returning answer and sources, plus a Gradio `app.py`
- *What I changed or overrode:* The initial system prompt said "try to answer from the provided context." I directed Claude to harden the grounding instruction to "answer using ONLY the information provided" and add an explicit fallback phrase ("I don't have enough information on that") so the model declines clearly rather than hallucinating when context is insufficient.
