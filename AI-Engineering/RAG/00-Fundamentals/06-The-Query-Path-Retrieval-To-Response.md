The indexing work is done: your 100-page company PDF has been loaded, chunked page-wise, embedded into 128-dimensional vectors, and parked in the vector store alongside each chunk's text and metadata. The system now sits idle, waiting.

Then a user types:

> **"What is the company's policy on refund or return of an item?"**

Everything that happens in the next half-second is the **query path** — and it re-runs, from scratch, for every single question. Let's walk it.

---

## Step 1 — The query becomes a vector too

Look at the mismatch first. The user's query is **text**. What's sitting in the vector store is **128-dimensional vectors**. You cannot measure the similarity between a sentence and a list of numbers — the two live in different worlds. Before any comparison can happen, the query has to enter the *same world* as the stored chunks.

So the query goes through the **embedding model** — and critically, the **same embedding model** that embedded the chunks — producing a **query vector**.

How many dimensions must it have? **Exactly as many as the stored vectors: 128.** This isn't preference, it's geometry — distance between two points is only defined when they live in the same space. A query vector of any other size simply couldn't be compared against the store.

> [!important] Same embedding model, same dimensions — always. Chunks embedded with one model and queries embedded with another produce vectors in *different* semantic spaces; the distances between them are meaningless noise, even if the dimension counts happen to match. The pairing of embedder-at-index-time and embedder-at-query-time is a hard constraint of the pipeline.

---

## Step 2 — Similarity search: meaning as distance

Now both sides are vectors in one 128-dimensional space, and something beautiful falls out. Remember what those 128 numbers *are*: the captured **semantic meaning** of each text. If similar numbers encode similar meaning, then finding relevant chunks stops being a language problem and becomes a **geometry problem**:

> [!info] **Shorter distance between two vectors = more similar meaning between their texts.** Similarity search is nothing more than: measure the distance from the query vector to every stored chunk vector, and take the closest ones.

Picture the 128-dimensional space (draw it as 2-D in your head — the intuition survives). Every chunk of the PDF is a point. The refund-policy chunk sits *here*; the shipping-rules chunk nearby (related topic); the dress-code chunk far away in another neighbourhood. Now the query vector for *"refund or return of an item"* lands — and where does it land? Right in the refund neighbourhood, because its **meaning** overlaps theirs, regardless of exact wording.

The store measures distances and ranks. The result might be: refund chunk closest, returns-process chunk second, shipping chunk third... dress code nowhere. The **top-k** closest — say the top 4 — win.

```
128-dim space:      refund ●   ● returns          query ✦ lands here
                        ● shipping                (close to refund/returns)

                                    ● dress code  (far away — different meaning)

Similarity search:  distance(✦, each ●) → sort → take top 4
```

---

## Step 3 — Retrieval: you get the text back, not the vectors

The search found the 4 winning vectors. So do we send those vectors onward? **No — and understanding why locks in the whole design.**

The vectors' job is already finished. They existed for exactly two purposes: to *sit in the store* and to *make similarity computable*. Both are done. What would you even do with `[0.74, -0.09, 0.51, ...]` in a prompt? An LLM can't read meaning out of raw coordinates — augmenting numbers into a prompt achieves nothing.

What retrieval actually returns is, for each winning chunk, the two things stored *alongside* its vector:

1. **The chunk's text** — the words the LLM will actually read
2. **The chunk's metadata** — source file, page number, for attribution

These are your **retrieved chunks**: the 4 most semantically relevant pieces of the 100-page document, in readable form, with provenance attached.

---

## Step 4 — Augmentation: assembling the final prompt

Now the pipeline builds the actual prompt the LLM will see — this is **context assembly**, and it's the "A" in RAG. The final prompt contains **two ingredients**:

1. The **retrieved context** — the text of the 4 winning chunks
2. The **original query** — the user's question, unchanged

Shaped roughly like:

```
From the given context, answer the query.

Context:
[chunk 1 text — refund policy...]
[chunk 2 text — returns process...]
[chunk 3 text...]
[chunk 4 text...]

Query: What is the company's policy on refund or return of an item?
```

The name of the whole technique is sitting right there in this step: the prompt has been **augmented** with retrieved knowledge. The LLM is no longer asked to answer from its training data — it's asked to answer *from the supplied context*.

---

## Step 5 — Generation: in-context learning does the rest

The augmented prompt goes to the **LLM** as input. The model uses **in-context learning** — its ability to absorb and use information given *inside the prompt* — to read the four chunks and generate the answer to the query from them. Out comes a **relevant response**: grounded in the actual policy document, able to cite (via metadata) exactly which file and page it drew from.

The model never trained on your PDF. It's answering correctly anyway — because the pipeline put the right knowledge in front of it at the right moment.

---

## The full path, and what happens on the next question

```mermaid
flowchart LR
    Q["User query — text"] --> EM["Same embedding model"]
    EM --> QV["Query vector — 128 dims"]
    QV --> VS[("Vector store — similarity search by distance")]
    VS --> RC["Top-4 retrieved chunks — text + metadata"]
    RC --> AUG["Augmentation — context + query assembled into one prompt"]
    AUG --> LLM["LLM — in-context learning"]
    LLM --> R["Relevant, grounded response"]
```

Tomorrow the user asks a completely different question. Nothing is reused from today's query — the new question is embedded (same model, 128 dims), lands somewhere *else* in the space, finds *different* nearest chunks, gets a *different* assembled context, and produces a different grounded answer. The query path re-runs in full every time; only the indexing work stays done.

> [!tip] Interview framing — "walk me through query time"
> "The query is embedded with the *same* model used at indexing so it lands in the same vector space — same dimensions, comparable distances. Similarity search ranks stored chunks by distance to the query vector and returns the top-k — but what comes back is each chunk's *text and metadata*, not the vector; vectors exist only for the math. Augmentation assembles retrieved context plus the original query into one prompt, and the LLM answers via in-context learning — grounded in the retrieved text, attributable through the metadata."
