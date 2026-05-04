#rag #embeddings #chunking #vector-db #ann #hnsw #indexing

---

# You Have 1000 Documents. How Do You Make Them Searchable by Meaning?

You understand embeddings — a sentence goes in, a vector comes out, similar meanings produce similar vectors. Now you have a thousand-page school handbook. How do you actually build something a query can search against?

---

## Can You Embed the Whole Page as One Vector?

A single page might cover leave policy in paragraph 1, exam schedule in paragraph 2, and canteen timings in paragraph 3. If you embed the whole page as one vector, that vector is trying to represent three different topics at once.

What happens when a query about leave policy comes in? The page vector is diluted — it doesn't closely match anything specific. You get poor retrieval.

> [!danger] Embedding too much text in one vector dilutes meaning. The vector becomes a blurry average of everything on the page.

---

## Can You Embed Line by Line?

The other extreme: embed every sentence individually.

Consider this line: *"Students must submit it 3 days in advance."*

Submit *what*? Without the surrounding sentences, this line has no meaning. Its embedding captures almost nothing useful — and it will match the wrong things.

> [!danger] Embedding too little loses context. A sentence without its neighbours is often ambiguous or meaningless on its own.

---

## What Is the Right Unit?

A **chunk** — a paragraph or a fixed window of sentences that share the same topic and context. Large enough to carry meaning, small enough to be specific.

**Rule of thumb:** a chunk should be able to answer one question on its own.

In practice, a common strategy is a sliding window — each chunk overlaps slightly with the next so context isn't cut off at boundaries.

---

## What Does Index Time Look Like?

Once you have chunks, the pipeline is:

```
Raw documents
    ↓
Split into chunks (e.g. 200–500 tokens each)
    ↓
Pass each chunk through an embedding model
    ↓
Store (chunk text + vector + metadata) in a vector DB
```

This happens **once**, before any user ever queries the system. It is called **index time** — you are building the searchable index.

> [!info] Index time is offline work. Query time is live work. The vector DB is the artifact that connects them.

---

## How Does the Vector DB Find the Closest Vector at Query Time?

The naive approach: embed the query, then calculate distance from the query vector to every stored vector, return the closest K.

Correct — but slow at scale. 5 million chunks means 5 million distance calculations per query.

The vector DB solves this with **ANN — Approximate Nearest Neighbour** search. Instead of finding the *exact* closest vector, it finds one that is *close enough*, orders of magnitude faster.

The most common algorithm is **HNSW (Hierarchical Navigable Small World)** — it builds a graph where each vector node is connected to its nearest neighbours. At query time, you navigate the graph rather than scanning everything.

You never implement this yourself. The vector DB (Pinecone, Qdrant, Weaviate, pgvector) handles it internally.

> [!info] ANN trades a tiny bit of accuracy for a massive gain in speed. In practice, the top-K results are indistinguishable from exact search for RAG use cases.

---

## What Gets Stored in the Vector DB?

Each entry holds three things:

| Field | What it is |
|---|---|
| `id` | Unique identifier for this chunk |
| `vector` | The embedding (e.g. 1536 floats) |
| `metadata` | Original text, source file, page number, date |

The vector is what gets searched. The metadata is what gets returned and fed to the LLM.

---

## How Do You Get the Original Text Back From a Search Result?

The vector is just numbers — you cannot reverse it back into the original paragraph. So how does the system return actual readable text to the LLM?

Simple: store the chunk text directly inside the metadata field, alongside the vector. When ANN search returns top-K results, each result already carries the original paragraph. No extra lookup needed.

**But isn't storing all that text expensive?**

Run the numbers:

| What | Size |
|---|---|
| One chunk (~300 tokens) | ~1–2 KB |
| One embedding vector (1536 floats × 4 bytes) | ~6 KB |

The text is smaller than the vector itself. At paragraph scale, storing text in metadata barely moves the needle.

**When would you use an S3 pointer instead?**

When the original content is large — a full PDF, an image, a video transcript. In that case you store a pointer (S3 URL or file path) in metadata and fetch the full content only when needed. For paragraph-sized chunks, inline text is simpler and cheaper.

> [!info] The vector finds the right chunk. The metadata carries the chunk home.

---

## Mental Model To Remember

> [!info] Building a vector index is like hiring a librarian before the library opens. They read every book, write a meaning-summary for each page, and file those summaries in a lookup system. When a reader arrives with a question, the librarian finds the closest summaries in seconds — not by reading every book again, but by navigating the index they already built.

