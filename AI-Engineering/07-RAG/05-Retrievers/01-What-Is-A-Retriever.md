By now the pipeline has built up a knowledge base. Documents were loaded, split into chunks, each chunk was embedded, and every embedding was persisted inside a vector store together with its text and metadata. But storing was never the point — **retrieving** is. When a user asks a question, something has to reach into that store and pull out the handful of chunks that actually answer it. That something is the **retriever**.

---

## The retriever's job — text goes in, relevant documents come out

The first thing to fix in your head is the retriever's shape: **its input is always a plain-text query, and its output is a list of relevant documents.**

That input detail trips people up. You might expect a retriever to take a *vector* — after all, similarity search is vector math. It doesn't. You hand it ordinary text, exactly the words the user typed. The reason is that the retriever is a **sub-component of the vector store**, and the vector store already owns the embedding step. So the retriever quietly does the embedding for you: you give it text, and internally it turns that text into a query vector using the same embedding model the store was built with. This is the same convenience `similarity_search` gave us in the vector-store module — you never embed the query by hand.

Once it has the query vector, the work is the retrieval you already know. Recall that a vector store really does three jobs — it **stores** the embeddings, **indexes** them for fast lookup, and **searches** them; the retriever is what drives that third job, the search. The query vector lands in the store's multidimensional space and the store uses its distance metric and its index — HNSW, for the ChromaDB we've been using — to build a **local neighbourhood** around the query: the region of the space closest in meaning. Every candidate document in that neighbourhood is scored against the query and then **sorted** by that score, and the top ones are handed back. Which direction "best" sorts depends on the metric: with a *distance* metric the smallest values are the closest, so it sorts ascending; with a *similarity* metric the largest values are the closest, so it sorts descending. Either way, the documents nearest in meaning end up on top.

And here is the part worth slowing down on: what comes back is **not** a bare vector. Each result is a full record — the `id`, the `metadata`, the embedding, **and the actual document text**. The embedding is what the distance math ran on, but the embedding is not what you want. You want the *text*, because the text is what you will feed to the language model in a moment. The metadata rides along too, so you can later say which source or page an answer came from. A retriever that returned only vectors would be useless; the point is to get back readable, attributable chunks.

![[AI-Engineering/07-RAG/05-Retrievers/Images/01-Retriever-Sub-Component.png]]

> [!info] A **retriever** takes a plain-text query and returns a list of relevant `Document`s.
> It is a **sub-component of the vector store** — it embeds the query internally, runs the nearest-neighbour search over the store's index, and returns full records (text + metadata + embedding), not just vectors.

---

## Why a retriever at all — the vector store already searches

There is an obvious objection here. Back in the vector-store module, `vector_store.similarity_search("some text", k=3)` already took plain text and returned the nearest documents. If the store can already do that, why wrap it in a separate "retriever" component at all?

Two reasons, and they are the whole justification for this module.

**First, customizability.** The store's built-in `similarity_search` does exactly one thing: basic top-`k` nearest-neighbour retrieval. It offers almost no knobs. But "find the closest few" is not the only way you ever want to retrieve.
* Sometimes you want to keep only documents above a quality bar. 
* Sometimes you want results that are relevant *and* diverse, so you don't get three near-identical chunks. 
* Sometimes you want old-fashioned keyword matching instead of semantic similarity. 
A full-fledged retriever is the object that lets you choose the **search algorithm** and tune its **parameters** — the number to fetch, a score cutoff, metadata filters, and more. `similarity_search` gives you basic retrieval; a retriever gives you *retrieval strategies*.

**Second, a standard interface.** In LangChain, a retriever is a standard, composable component — it exposes a uniform `.invoke(query)` method, the same shape every other piece of a LangChain pipeline uses. That means the retrieval step slots into a chain right next to the loader, the splitter, the prompt, and the LLM, all speaking the same interface. The raw `similarity_search` method is a method on the store; the retriever is a first-class *component* you can drop into a pipeline. That composability is why, in practice, you almost always retrieve through a retriever rather than by calling the store's search method directly.

> [!important] The vector store's `similarity_search` only does **basic** retrieval, with almost no tuning.
> A **retriever** exists to give you
>  (1) **customizable search strategies and parameters**, and 
>  (2) a **standard `.invoke()` interface** that plugs uniformly into a LangChain pipeline.

---

## Creating a retriever from a vector store

Because the retriever is attached to the store, you never build one from scratch — you ask the store for one. Any vector store you have populated with embeddings can hand you a retriever through a single call, `.as_retriever(...)`. What comes back is a **retriever object**. You then drive it with `.invoke(query)`, passing your text query, and it returns the list of relevant documents.

```
vector_store  ──.as_retriever(...)──▶  retriever object
retriever.invoke("user's text query")  ──▶  [relevant Document, Document, ...]
```

The `.as_retriever(...)` call is where the customization lives. It takes a `search_type` — *which* algorithm to use — and `search_kwargs`, a dictionary of that algorithm's parameters (how many to return, a score threshold, and so on). You can also give it a metadata **filter**, so it only ever considers documents matching some condition — for example, "only retrieve chunks whose `source` is Wikipedia." Those exact search types and parameters are what the next note works through in code; for now the shape is the thing to hold: *store → `as_retriever` → retriever object → `invoke` → documents.*

---

## From retrieved documents to a grounded answer

The retriever's output is not the final answer — it is the raw material for the step the whole RAG pipeline was building toward. The documents it returns are **relevant, heavily filtered, external context**, and they now get folded into the prompt alongside the user's original question. This is the **augmentation** step: the prompt is assembled as *"here is some context: {retrieved chunks}; here is the user's question: {query}; answer the question using this context."*

Two details in that prompt matter enormously. The first is a **guardrail**: you explicitly instruct the model to answer *only* from the provided context, and — critically — *"if the answer is not in the context, say 'I don't know'."* Without that line the model happily falls back on its own memory and invents a confident wrong answer; with it, missing information produces an honest "I don't know" instead of a hallucination. The second is that because the retrieved chunks arrived with their **metadata**, you can also use that metadata for **source attribution** — telling the user not just the answer but which document and page it came from.

That augmented prompt goes to the LLM, which generates the response, and the response is shown to the user. And this is where the payoff of the entire pipeline finally lands:

![[AI-Engineering/07-RAG/05-Retrievers/Images/02-Retriever-Benefits.png]]

- **Higher accuracy, factually grounded.** The answer is built from relevant, filtered, external information you supplied — not from the language model's fuzzy, half-remembered training. The response is grounded in real retrieved text, so it is far more likely to be factually correct.
- **Latest knowledge, no retraining.** The model is no longer leaning on its frozen pretrained knowledge. To teach it something new you do **not** retrain it — you simply put the fresh information into the context at query time. This is exactly how RAG dissolves the knowledge-cutoff problem: the LLM's weights can be a year stale, yet the answer reflects a document you added this morning.

---

## What a retriever gives you — and what it doesn't

> [!info] **What a retriever guarantees**
> - Plain text in, a ranked list of **relevant documents** out — each carrying its text and metadata, not just a vector.
> - A **choice of search strategy** and tunable parameters (via `search_type` + `search_kwargs`).
> - A **standard `.invoke()` interface** that composes cleanly into a LangChain pipeline.

> [!danger] **What a retriever does *not* do**
> - It does **not generate the answer** — it only fetches context. Composing that context into a final response is the LLM's job in the generation step.
> - It is **not smarter than its inputs** — retrieval quality is still bounded by how well the documents were chunked and embedded. A retriever can only find what the store meaningfully holds.
> - It offers **no free lunch on tuning** — a badly chosen parameter (say, a score threshold set too high) can return nothing at all, as the next note shows.

> [!tip] Interview framing
> "A retriever is the component that turns a user's text query into the relevant chunks that answer it. It's a sub-component of the vector store — you hand it plain text, it embeds the query internally, runs the nearest-neighbour search over the store's index, and returns full documents with their text and metadata. You could call the store's `similarity_search` directly, but a retriever exists for two reasons: it lets you customize the search strategy and its parameters, and it exposes a standard `.invoke()` interface that plugs into a LangChain pipeline. Its output feeds the augmentation step — the retrieved chunks go into the prompt alongside the question, with a guardrail to answer only from that context, and the LLM generates a grounded, up-to-date response."
