Everything so far has been theory: what embeddings are, how the space is shaped, how you measure distance, how dimensionality trades nuance against cost. Now we actually generate some. But the moment you go to run an embedding model, a fork in the road appears — there are **two fundamentally different kinds of model** you can reach for, and the choice shapes your cost, your privacy, and your ops. This note takes the first road; the next note takes the second.

---

## Two kinds of embedding model — proprietary vs open-source

The first kind is a **proprietary** model, also called **closed-source**. The defining property is blunt: you **cannot** download it and run it on your own machine. The company that built it — OpenAI, for instance — keeps the architecture and the trained weights private. They are not published for anyone to grab. Instead, the model runs on **their** servers, and you reach it through an **API**: you send your text over the network, their server embeds it, and you get the vector back. Because it's their compute doing the work, you **pay** for it — typically per token or per call, on a subscription.

The second kind is an **open-source** model. Here the weights **are** published — you can download the model and run it on your own hardware, on your own server, with no per-call fee and no text leaving your infrastructure. That's the subject of the next note (using Ollama). For now, hold onto the contrast:

```
Proprietary (closed-source)          Open-source
─────────────────────────            ─────────────────────────
can't download the weights           download and run yourself
runs on the provider's servers       runs on your hardware
accessed via API over the network    accessed locally
pay per use (subscription)           free to run (you own the compute)
e.g. OpenAI text-embedding-3         e.g. embeddinggemma via Ollama
```

> [!info] Proprietary / closed-source embedding models live behind an API — the weights are private, the compute is the provider's, and you pay per use. Open-source models are downloadable and run on your own hardware for free. Neither is universally **better**; the next note lays out the full trade-off. This note shows the proprietary path with OpenAI.

---

## Setting up the OpenAI embedder

We'll use LangChain's wrapper around OpenAI's embedding models. Two imports do the heavy lifting — the embedder class itself, and `load_dotenv` to pull the OpenAI API key out of a `.env` file (a proprietary model needs a key, because you're calling a paid API):

```python
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

# reads OPENAI_API_KEY from your .env into the environment
load_dotenv()
```

OpenAI offers two embedding models in this generation, and they differ in exactly the dimensionality dimension we just spent a whole note on:

```python
MODEL_SMALL = "text-embedding-3-small"   # 1536 dimensions
MODEL_LARGE = "text-embedding-3-large"   # 3072 dimensions
```

The `-small` model returns **1536**-dimensional vectors; the `-large` returns **3072**. Straight off the shelf, `-large` gives you more nuance (and costs more to store and move, per the previous note); `-small` is the cheaper, lighter default. You create an embedder object for whichever you want:

```python
embedder_small = OpenAIEmbeddings(model=MODEL_SMALL)
embedder_large = OpenAIEmbeddings(model=MODEL_LARGE)
```

An `OpenAIEmbeddings` object is just a handle to the remote model — nothing is embedded yet. It's the thing you call to turn text into vectors.

---

## Embedding a single query — `embed_query`

The first thing you'll ever want is to embed one piece of text — usually the user's question. That's `embed_query`, which takes a single string and returns a single vector:

```python
query = "What is Openclaw/Moltbot and what are the major security concerns regarding this tool"

embeddings_large = embedder_large.embed_query(text=query)
```

`embeddings_large` is now a plain list of floating-point numbers — the query as a point in the embedding space. Two sanity checks confirm what the theory promised. First, its length is exactly the model's dimensionality:

```python
len(embeddings_large)      # → 3072   (the -large model)
```

And peeking at the first handful of values shows the dense, all-non-zero vector from the word-embeddings note — every slot carries a real number, nothing like the mostly-zero sparse vectors of bag-of-words:

```python
embeddings_large[0:10]
# → [-0.017, 0.021, -0.004, 0.038, ...]   dense floats, one per dimension
```

Swap in the small model and the only thing that changes is the length — `1536` instead of `3072`:

```python
embeddings_small = embedder_small.embed_query(text=query)
len(embeddings_small)      # → 1536
```

> [!info] `embed_query(text=...)` embeds **one** string and returns **one** vector, whose length equals the model's dimensionality. It's the call you use for the incoming user query at retrieval time — one question in, one point in space out.

---

## Embedding a whole document — `embed_documents`

Retrieval has two sides. The query is one text embedded once, and that's `embed_query`. But the **knowledge base** is thousands of chunks that all need embedding — and for that there's a separate method, `embed_documents`, which takes a **list** of texts and embeds them in one batch. This is the ingestion half of RAG, and it sits right on top of the document-loader and text-splitter stages from the earlier modules.

Walk the full path. Load a PDF into document objects, split it into chunks, then embed those chunks:

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. load — PDF pages into Document objects
loader = PyPDFLoader(file_path="../Openclaw_Research_Report.pdf")
docs = loader.load()
len(docs)          # number of pages

# 2. split — pages into overlapping chunks
chunker = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = chunker.split_documents(docs)
len(chunks)        # number of chunks
```

`embed_documents` wants the raw text of each chunk, not the `Document` wrapper, so pull out `page_content` first, then embed the whole list at once:

```python
# 3. embed — every chunk in one batch call
text_documents = [doc.page_content for doc in chunks]

document_embeddings = embedder_large.embed_documents(texts=text_documents)

len(document_embeddings)        # → one vector per chunk (same as len(chunks))
document_embeddings[0:3]        # → the first three chunk vectors, each 3072-dim
```

The result is a list of vectors — exactly one per chunk, each of the model's dimensionality. Those are what you'd load into a vector database so the query vector can later find its nearest neighbours among them.

> [!important] `embed_query` vs `embed_documents` is the query-side vs corpus-side split. `embed_query(text=one_string)` → one vector, for the incoming question. `embed_documents(texts=list_of_strings)` → a list of vectors, for the whole knowledge base. Same model, same space — that shared space is what makes a query able to match a chunk — but two methods because one side is a single text and the other is a batch.

---

## Turning the dimensionality knob — the `dimensions` parameter

The last note treated dimensionality as a property of the model. With OpenAI's models it's also a **parameter you can dial down**. Pass `dimensions=` when you build the embedder and the model returns shorter vectors than its native size:

```python
embedder_large_custom = OpenAIEmbeddings(
    model=MODEL_LARGE,     # natively 3072-dimensional
    dimensions=256         # ask for 256 instead
)

query_embeddings = embedder_large_custom.embed_query(text=query)
len(query_embeddings)      # → 256
```

The `-large` model is natively 3072-dimensional, but here it hands back a **256**-dimensional vector. This is the storage-vs-nuance trade-off from the previous note made into a one-line setting: shrink the dimensions and every vector gets cheaper to store and faster to compare, at the cost of some captured nuance. There's a lower and an upper limit to what you can request, but within that band you're free to pick the size that balances quality against cost for your corpus — exactly the **experiment to find the sweet spot** advice, now with a concrete lever to turn.

> [!tip] `OpenAIEmbeddings(model=..., dimensions=n)` lets you truncate the output to `n` dimensions instead of the model's native size — a direct way to trade a little accuracy for smaller, cheaper, faster vectors. It's the practical control behind the whole dimensionality trade-off.

---

That's the complete proprietary path: pick a model, `embed_query` for the question, `embed_documents` for the corpus, and optionally dial the `dimensions`. Everything runs on OpenAI's servers and bills to your API key. The next note does the same job with the opposite kind of model — an open-source one you download and run yourself, with Ollama — and lays out when each choice is the right one.
