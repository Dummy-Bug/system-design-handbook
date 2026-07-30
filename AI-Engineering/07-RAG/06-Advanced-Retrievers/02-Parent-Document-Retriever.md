The contextual compression retriever cut the noise *inside* a retrieved chunk. The **parent document retriever** goes after a deeper tension — one baked into the chunk *size* itself. It turns out that the ideal chunk size for finding the right passage is the exact opposite of the ideal chunk size for feeding the answer, and no single size can satisfy both. This retriever's whole trick is to stop trying.

---

## The compression problem — small chunks embed better than big ones

Start from what an embedding model does when it embeds a chunk: it **compresses**. It takes the text and squeezes its entire meaning into a fixed-size vector — say 768 numbers — trying to lose no information, so that all the semantic content survives the conversion. If a chunk covers five topics, the model tries to pack the essence of all five into that one vector.

But there's only so much room. The more text you feed in, the more aggressively the model has to compress to fit it into the same fixed vector — and the more it compresses, the more meaning leaks away. A **short** chunk barely needs compressing, so its embedding is a faithful representation. A **long** chunk gets crushed hard into the same 768 numbers, so some of its semantic meaning is simply lost. The rule to remember: **as chunk length grows, embedding quality falls.**

---

## Two jobs, two opposite wishes

Now recall that a retriever does two things, and hold both in mind at once:

- **Similarity search** — finding the chunks nearest the query.
- **Augmentation** — building the context you hand the LLM.

Ask what each one *wants*, and they pull in opposite directions.

For the **best possible similarity search**, you want retrieval to be razor-accurate — the returned chunks should be genuinely, highly similar to the query. That requires high-quality embeddings, and high-quality embeddings require **small chunks** (low compression, faithful representation). So: *small chunks give better retrieval.*

But then comes augmentation. If you take those same small chunks and stuff them into the context, the context is **starved** — each chunk carries so little text that the total information volume is inadequate. To give the LLM enough to work with, you want **large chunks** with plenty of surrounding information. So: *large chunks give better context.*

And if you try to satisfy augmentation by embedding **large** chunks in the first place? Retrieval quality collapses — the heavy compression on those big chunks loses semantic meaning, so similarity search returns worse matches. You can't win. This is a genuine, counter-intuitive **trade-off**: small chunks win retrieval and lose context; large chunks win context and lose retrieval. One chunk size cannot be good at both.

> [!important] The chunk-size trade-off: **small chunks → precise retrieval but thin context; large chunks → rich context but imprecise retrieval.** Embedding compression is why — long text embeds worse than short text.

---

## The trick — retrieve on children, return parents

The parent document retriever refuses the trade-off by using **two different chunk sizes for the two different jobs**: it runs retrieval on *small* chunks (so search is precise) but hands the LLM *large* chunks (so context is rich). The small chunks are called **children**, the large ones **parents**, and each child remembers which parent it came from.

To pull this off it wires together four components:

1. **Parent splitter** — a text splitter that cuts your documents into **large** "parent" chunks.
2. **Child splitter** — a text splitter that cuts each *parent* into several **small** "child" chunks.
3. **Vector store** (e.g. Chroma) — holds only the **child** embeddings. Children are the *only* thing that gets embedded and searched.
4. **Docstore** — holds the **parent** chunks, keyed by ID. This is a plain key-value store, either in memory or on disk.

The link between the two is an **ID**: every parent gets a unique ID (a UUID), and every child carries its parent's ID in its metadata. That ID is the thread that lets a retrieved child pull back its parent.

---

## The flow — ingestion, then retrieval

**Ingestion.** Your original documents go through the parent splitter into large parent chunks — say 5 parents, `P1`–`P5` — and each parent is stored in the docstore under its own unique ID. Then each parent is fed to the child splitter and shattered into many small children — say 10 per parent, so 50 children in all — each tagged with its parent's ID. Only the children are embedded, and those child embeddings go into the vector store.

![[AI-Engineering/07-RAG/06-Advanced-Retrievers/Images/02-Parent-Document-Ingestion.png]]

So after ingestion you have two stores holding two granularities: 50 small child embeddings in the vector store (for searching) and 5 large parent chunks in the docstore (for answering).

**Retrieval.** A query runs a similarity search over the **child** embeddings. Because the children are small and their embeddings are high-quality, this search is precise — it returns the genuinely most relevant small chunks (say `k=3`: `C3`, `C20`, `C35`).

![[AI-Engineering/07-RAG/06-Advanced-Retrievers/Images/03-Parent-Document-Retrieval.png]]

But — and this is the whole point — those tiny children are **not** what goes into the context; on their own their information volume is inadequate. Instead, the retriever reads each retrieved child's `parent-id`, looks those parents up in the docstore, and returns the **parent** chunks. If several retrieved children belong to the same parent, that parent is returned once (deduplicated). The precise search happened on children; the rich context comes from parents.

> [!info] **Children are used only for retrieval; parents are used for the context.** Small children make the similarity search precise; the parents they point to give the LLM a full, information-rich passage. You get accurate retrieval *and* adequate context — the trade-off dissolved.

---

## In code — `ParentDocumentRetriever`

The imports come from `langchain_classic` again (same deprecation caveat as the ensemble and compression retrievers). Note the two storage helpers — one in-memory, one on-disk:

```python
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_classic.storage import InMemoryStore, LocalFileStore, create_kv_docstore

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
```

The two splitters are where "parent" and "child" become concrete — the parent chunk is nearly four times the size of the child:

```python
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)   # large → context
child_splitter  = RecursiveCharacterTextSplitter(chunk_size=400,  chunk_overlap=50)    # small → retrieval
```

Wire up the two stores and the retriever. The vector store will hold the child embeddings; the `InMemoryStore` will hold the parents:

```python
store_memory = InMemoryStore()
vectorstore_memory = Chroma(collection_name="memory_children", embedding_function=embeddings)

retriever_memory = ParentDocumentRetriever(
    vectorstore=vectorstore_memory,   # child embeddings live here
    docstore=store_memory,            # parent chunks live here
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
    search_kwargs={"k": 3},
)

retriever_memory.add_documents(docs)
```

That single `add_documents` call does the entire ingestion pipeline for you: split into parents, store the parents, split each parent into children, embed the children, and store the child embeddings. You can see the two granularities by counting each store — there are many more children than parents:

```python
parent_count = len(list(store_memory.yield_keys()))
child_count  = len(vectorstore_memory.get()["ids"])
print(f"parent chunks: {parent_count}  |  child chunks in vectorstore: {child_count}")
```

Now query it. You search with plain text, but what comes back is **parent** chunks — the retriever has already swapped the matched children for their parents under the hood:

```python
query = "How do transformer architectures work in deep learning?"
results_memory = retriever_memory.invoke(query)   # → parent chunk(s), not children
```

### Persisting the parents — `InMemoryStore` vs `LocalFileStore`

The docstore is just a key-value store, so it has the same in-memory-versus-on-disk choice we saw with vector stores. `InMemoryStore` keeps the parents in RAM — gone when the process exits. Swap in a `LocalFileStore` (wrapped by `create_kv_docstore`) and the parents are written to disk, surviving a restart:

```python
fs = LocalFileStore("./local_parent_store")
store_fs = create_kv_docstore(fs)

vectorstore_fs = Chroma(collection_name="fs_children", embedding_function=embeddings)

retriever_fs = ParentDocumentRetriever(
    vectorstore=vectorstore_fs,
    docstore=store_fs,               # parents now persisted on disk
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
    search_kwargs={"k": 3},
)
retriever_fs.add_documents(docs)

results_fs = retriever_fs.invoke(query)   # same parents, now durable across runs
```

Everything else is identical; only where the parents live has changed.

---

## What the parent document retriever gives you — and what it costs

> [!info] **What it guarantees**
> - **Precise retrieval *and* rich context at once** — it searches over small, faithfully-embedded child chunks but returns the large parent chunks they belong to.
> - **Automatic plumbing** — one `add_documents` call splits into parents, stores them, splits into children, embeds and stores those; `invoke` returns parents transparently.
> - **A choice of parent storage** — `InMemoryStore` (fast, ephemeral) or `LocalFileStore` (durable across runs).

> [!danger] **What it costs**
> - **Two stores to manage** — a vector store for children and a separate docstore for parents, kept in sync by parent IDs.
> - **Two size knobs to tune** — parent and child `chunk_size` both matter; children too big lose retrieval precision, parents too big drown the context in text again.
> - Parents are returned **whole** — you get the full parent even if only a small part of it was relevant (contextual compression is the tool that trims that back down).

> [!tip] Interview framing
> "The parent document retriever solves the chunk-size trade-off. Embeddings compress, so small chunks embed well and give precise retrieval, but small chunks make thin context; large chunks give rich context but embed poorly and hurt retrieval. Instead of compromising on one size, it uses two: a child splitter makes small chunks that get embedded and searched, and a parent splitter makes large chunks stored separately in a docstore. Each child carries its parent's ID, so you run similarity search on the precise little children, then return the large parents they point to as the context. In LangChain it's `ParentDocumentRetriever` with a `child_splitter`, a `parent_splitter`, a vector store for child embeddings, and a docstore — `InMemoryStore` or `LocalFileStore` — for the parents."
