Every retriever so far — similarity, MMR, BM25, hybrid — answers the same question: **which documents should I return?** The **contextual compression retriever** answers a different one: **within a document I've returned, which part is actually worth keeping?** It's the first of the **advanced retrievers,** and it fixes a problem the others quietly ignore — that even a perfectly-retrieved chunk is mostly noise.

---

## The problem — a retrieved chunk is mostly noise

Go back to what an embedding does: it **compresses**. When the pipeline embeds a chunk, the model squeezes everything in that chunk into one fixed-size vector. But a real chunk is rarely about a single thing. A paragraph pulled from a document might touch on five different sub-topics at once — call them T1 through T5 — and the embedding model dutifully tries to represent all five, blended together, in that one set of numbers.

Now the trouble. Your query is usually relevant to only **one** of those sub-topics — say T2. But retrieval doesn't return **the T2 part**; it returns the **whole chunk**. So the context you hand the language model contains the one relevant sub-topic plus four sub-topics of noise.

Make it concrete with the documents this notebook uses. Each is a dense paragraph packing several distinct points into one block — here's the medicine one:

```
"CRISPR gene editing technology has revolutionized medical genomics...
 Researchers are using genomic data to develop personalized medicine...
 Recent breakthroughs in mRNA technology, accelerated by COVID-19 vaccine
 development, are now being applied to cancer immunotherapy...
 Hospital information systems are increasingly integrating genomic data
 to support clinical decision-making at the point of care."
```

Four different ideas in one chunk: CRISPR, personalized medicine, mRNA/cancer vaccines, and hospital IT systems. Ask **How is CRISPR acting as a big enabler in creating personalized medicine?** and only the first two sentences matter — but plain retrieval returns the entire paragraph, mRNA vaccines and hospital software included.

Why does that noise hurt? Because you instruct the LLM to answer **only from the provided context**. If that context is padded with irrelevant sentences, the model has to wade through them, can latch onto the wrong detail, and generally produces a worse, more confused answer. The more noise you stuff into the context, the more you undermine the very grounding you retrieved for. What you want in the context is **only** the relevant information — nothing else.

---

## The idea — compress the context after retrieving it

The name spells out the fix: **contextual compression** means compressing the retrieved **context** down to only what's relevant. It works in two stages:

1. A **base retriever** does ordinary retrieval — it fetches the full chunks, exactly as before.
2. A **compressor** then post-processes each retrieved chunk, stripping out everything not relevant to the query and keeping only the relevant part — producing a new, smaller **compressed chunk**.

![[AI-Engineering/07-RAG/06-Advanced-Retrievers/Images/01-Contextual-Compression-Concept.png]]

Think of the compressor as running a loop over every chunk the base retriever returned: for each one, it pulls out the query-relevant information, discards the noisy remainder, and emits a trimmed chunk. The medicine paragraph goes in whole and comes out as just the CRISPR-and-personalized-medicine sentences. Do that for all the retrieved chunks and your final context is short, precise, and relevant — and **that** is what goes to the LLM to generate the answer.

> [!info] A **contextual compression retriever** wraps a base retriever with a **compressor**. The base retriever fetches full chunks; the compressor trims each one down to only the parts relevant to the query. The result is a **shorter, precise, less-noisy context** for the LLM.

---

## In code — the built-in `ContextualCompressionRetriever`

The imports come from `langchain_classic` (the same module family as the ensemble retriever — see the deprecation note at the end). We need an LLM this time, because one of the compressors uses it to do the trimming:

```python
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import (
    LLMChainExtractor,
    EmbeddingsFilter,
    DocumentCompressorPipeline,
)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-5-mini", temperature=0)
```

The documents are six deliberately dense, multi-topic paragraphs (AI, climate, space, medicine, economics, quantum computing) — each one a little pile of mixed sub-topics, which is exactly the noise the compressor is meant to cut. Build an ordinary base retriever over them:

```python
vectorstore = InMemoryVectorStore.from_documents(docs, embedding=embeddings)
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
```

Run the query through the base retriever alone and you get the **whole** paragraphs back — the relevant sentences buried inside three big blocks of mostly-irrelevant text:

```python
query = "How is CRISPR acting as a big enabler in creating personalized medicine?"
base_results = base_retriever.invoke(query)   # → 3 full, noisy paragraphs
```

Now wrap it. There are three compressor strategies, and they trade cost against precision.

### Strategy 1 — `LLMChainExtractor`: let an LLM extract the relevant sentences

This is the **compressor model** from the concept above, made real. `LLMChainExtractor` uses the LLM to read each retrieved chunk against the query and return **only** the sentences that are relevant:

```python
compressor = LLMChainExtractor.from_llm(llm)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever,
)

compressed_results = compression_retriever.invoke(query)
```

The base retriever still fetches the three full paragraphs, but now each passes through the LLM, which keeps only the query-relevant lines. The medicine paragraph comes back trimmed to just its CRISPR / personalized-medicine sentences; the mRNA-vaccine and hospital-IT sentences are gone. The output is dramatically shorter and sharper than the baseline. The cost: it makes an LLM call for **each** retrieved chunk — accurate, but not free.

### Strategy 2 — `EmbeddingsFilter`: a cheap, LLM-free filter

Calling an LLM per chunk is expensive. `EmbeddingsFilter` skips the LLM entirely: it embeds each retrieved chunk, measures its similarity to the query, and keeps only those above a threshold:

```python
embeddings_filter = EmbeddingsFilter(
    embeddings=embeddings,
    similarity_threshold=0.732,
)

compression_retriever_emb = ContextualCompressionRetriever(
    base_compressor=embeddings_filter,
    base_retriever=base_retriever,
)

emb_results = compression_retriever_emb.invoke(query)   # each doc carries a relevance_score
```

This is fast and cheap — no LLM in the loop — and it attaches a `relevance_score` to each surviving document. But it's coarser: it filters **whole chunks** (dropping the ones that don't clear the threshold) rather than trimming **within** a chunk. It removes irrelevant documents; it doesn't cut the noise out of a document that's partly relevant.

### Strategy 3 — `DocumentCompressorPipeline`: chain them for the best of both

You don't have to choose. A `DocumentCompressorPipeline` chains compressors so each cleans up after the last:

```python
pipeline_compressor = DocumentCompressorPipeline(
    transformers=[embeddings_filter, compressor]
)

compression_retriever_pipeline = ContextualCompressionRetriever(
    base_compressor=pipeline_compressor,
    base_retriever=base_retriever,
)

pipeline_results = compression_retriever_pipeline.invoke(query)
```

The cheap `EmbeddingsFilter` runs first and throws out the clearly-irrelevant chunks; then the expensive `LLMChainExtractor` runs only on the survivors, trimming them sentence-by-sentence. You get the LLM's precise within-chunk compression **without** paying for an LLM call on chunks that were never relevant in the first place — cheap filtering to narrow the field, expensive extraction to polish what's left.

---

## What contextual compression gives you — and what it costs

> [!info] **What it guarantees**
> - A **shorter, higher-signal context** — noise is stripped from retrieved chunks before they reach the LLM, so grounding is cleaner and answers sharper.
> - **Flexible compressors** — `LLMChainExtractor` (precise, LLM-based within-chunk extraction), `EmbeddingsFilter` (cheap whole-chunk filtering), and `DocumentCompressorPipeline` (chain them).

> [!danger] **What it costs**
> - `LLMChainExtractor` makes **an LLM call per retrieved chunk** — extra latency and money on every query.
> - `EmbeddingsFilter` is cheap but **coarse** — it drops whole chunks and can't trim within one; too high a `similarity_threshold` can filter out something useful.
> - It adds a **post-processing stage** on top of retrieval — more moving parts than a plain retriever.

> [!tip] Interview framing
> **A contextual compression retriever tackles noise, not recall. Embeddings compress a multi-topic chunk into one vector, so even a correctly-retrieved chunk carries lots of irrelevant text, and dumping that into the prompt confuses the LLM. It wraps a base retriever with a compressor: the base retriever fetches full chunks, then the compressor trims each down to just the query-relevant parts. `LLMChainExtractor` uses an LLM to extract the relevant sentences — precise but one LLM call per chunk; `EmbeddingsFilter` cheaply keeps only chunks above a similarity threshold — fast but coarse; and `DocumentCompressorPipeline` chains them, filtering cheaply first and extracting expensively on the survivors. The payoff is a shorter, cleaner context and a better-grounded answer.**
