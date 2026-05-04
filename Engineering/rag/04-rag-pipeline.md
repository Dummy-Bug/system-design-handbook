#rag #pipeline #retrieval #generation #vector-db #embeddings

---

# What Actually Happens When a User Asks a RAG System a Question?

A student asks the school assistant "what is the leave policy for class 10?" It answers correctly, citing the school handbook. No hallucination, no stale training data. How did it get there?

---

## There Are Two Phases — When Do They Happen?

Before any user query is answered, the system needs to know about your documents. That work happens once, offline. Then for every query, a different set of steps runs in real time.

The two phases are **indexing** and **querying**.

---

## Phase 1 — Index Time (Done Once, Offline)

This is where you prepare your knowledge base for fast, semantic retrieval.

**Step 1 — Collect your documents.**
HR policies, product docs, onboarding guides — anything the LLM should be able to reference.

**Step 2 — Chunk them.**
A 50-page document cannot be passed whole to an LLM — context windows are limited. So you split documents into smaller overlapping chunks (e.g. 500 tokens each).

**Step 3 — Embed each chunk.**
Pass each chunk through an embedding model. Every chunk becomes a vector — a list of numbers capturing its meaning.

**Step 4 — Store in a vector database.**
Store each chunk alongside its vector. The DB can now find the most semantically similar chunk to any query.

```
Documents → Chunks → Embeddings → Vector DB
```

> [!info] Indexing is like building a library's catalogue before anyone walks in. No query can be answered efficiently without it.

---

## Phase 2 — Query Time (Every User Question)

This runs live, on every request.

**Step 1 — Embed the query.**
The user's question is converted to a vector using the same embedding model used at index time. Same model is critical — the vectors must live in the same space to be comparable.

**Step 2 — Retrieve.**
The vector DB finds the top-K chunks whose vectors are closest to the query vector. These are the most semantically relevant pieces of your knowledge base.

**Step 3 — Augment the prompt.**
The retrieved chunks are injected into the LLM prompt alongside the original question:

```
Context:
[chunk 1 text]
[chunk 2 text]
...

Question: What is our appraisal policy?
Answer:
```

**Step 4 — Generate.**
The LLM reads the context + question and generates an answer grounded in the retrieved documents.

```
Query → Embed → Retrieve top-K → Augment prompt → LLM → Answer
```

---

## Why Pass Retrieved Documents Alongside the Question?

Without context, the LLM answers from training data — which contains nothing about your organisation. With context, the LLM has the actual source material in front of it and answers from that.

> [!warning] The LLM does not "remember" your documents. It reads them fresh every time they are injected into the prompt. RAG is not fine-tuning — it is runtime context injection.

---

## The Full Picture

```
INDEX TIME
──────────
Documents → Chunker → Embedding Model → Vector DB

QUERY TIME
──────────
User Question → Embedding Model → Vector DB (similarity search)
                                        ↓
                               Top-K relevant chunks
                                        ↓
                          [chunks + question] → LLM → Answer
```

---

## School Assistant Example End-to-End

1. The school uploads the student handbook PDF → chunked + embedded + stored in vector DB
2. A student asks: "what is the leave policy for class 10?"
3. Query is embedded → vector DB returns top 3 relevant chunks from the handbook
4. Chunks + question passed to the LLM
5. LLM answers citing only what is in those chunks

> [!info] The LLM's job is reasoning and language. The retriever's job is finding. RAG works because it separates these two responsibilities cleanly.

---

## Mental Model To Remember

> [!info] RAG is a chef who looks up the recipe before cooking. The vector DB is the recipe book, retrieval is finding the right page, and the LLM is the chef who reads it and cooks. Without the lookup step, the chef is guessing from memory.
