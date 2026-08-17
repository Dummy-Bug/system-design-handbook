
## Why ChromaDB — and why it's not your only option

The first thing to know is that ChromaDB is **not** the only vector store LangChain can talk to. LangChain ships integrations for many of them — FAISS, Pinecone, Qdrant, Milvus, Weaviate, and more — and they all sit behind a similar interface, so the store is a swappable component (the same swappability we saw with embedding models). You could replace Chroma with another and most of your code wouldn't change.

So why Chroma here? Because vector stores come in two flavours. On one side are **vanilla vector stores** — simple libraries that do little more than hold embeddings and run a similarity search over them. On the other are **full vector databases** — with proper database features on top: persistence, collections, metadata filtering, and cloud/enterprise options for production. **ChromaDB is a full-fledged vector database**, it's free to run locally, and it's beginner-friendly to inspect, which makes it the ideal one to learn on.

> [!info] A vector store is a swappable component in LangChain — Chroma, FAISS, Pinecone, Qdrant, Milvus, Weaviate all sit behind a similar interface. 
> 
> They range from **vanilla stores** (just embeddings + search) to **full vector databases** (persistence, collections, filtering, cloud features). 
> 
> ChromaDB is a full vector database, free and local, which is why it's the one to start with.

### In-memory vs on-disk — the persistence choice

Chroma can hold your vectors in one of two places, and this choice matters more than it first appears:

- **In-memory** — the embeddings live in RAM while your program runs. Fast, zero setup, but the moment the process exits, everything is gone. Re-run tomorrow and you're re-embedding from scratch.

- **On-disk (persistent)** — the embeddings are written to a directory on disk. Close the program, reopen it next week, point at the same directory, and every vector is still there — no re-embedding.

It's worth knowing what actually lands on disk when you persist, because you can open the folder and look. Inside the `persist_directory`, Chroma writes a **SQLite database file** plus a **subfolder for the collection** that holds the embedding store. Between them they keep everything a record is made of — the embeddings, the document text, the metadata, and the IDs — which is exactly why reopening the directory reconstructs the full store and not just the raw vectors. The persistence isn't a magic black box; it's an ordinary on-disk database you could inspect by hand.

---

## Setting up the store

Start with the imports. Notice `langchain_chroma` for the store, `Document` for the record type, `OpenAIEmbeddings` for the embedding model, and `uuid4` — which we'll need for unique IDs in a moment.

```python
import os
import shutil
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
```

Next, resolve where things live and load the API key. The project root is found relative to the notebook, and the `.env` file supplies `OPENAI_API_KEY` (needed because we're embedding with OpenAI's paid API):

```python
project_root = Path.cwd()
if project_root.name == "notebooks":
    project_root = project_root.parent

dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path)

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Please add your OPENAI_API_KEY to the .env file before running this notebook.")
```

Now two settings that define the store — the **collection name** and the **persist directory**:

```python
collection_name = "demo_2"
persist_directory = project_root / "notebooks" / "chroma_langchain_db"
```

A **collection** is Chroma's word for a named group of vectors — like a table in a regular database. One Chroma database can hold several collections; `collection_name` says which one we're working in. The `persist_directory` is the folder on disk where those vectors get written — this is what makes the store on-disk rather than in-memory.

Because we're going to run this notebook repeatedly while learning, we wipe any old copy of that directory first, so each run starts clean:

```python
if persist_directory.exists():
    shutil.rmtree(persist_directory)
    print("Removed the old Chroma directory.")
else:
    print("No previous Chroma directory was found.")
```

Finally, create the embedding model and the store itself:

```python
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vector_store = Chroma(
    collection_name=collection_name,
    embedding_function=embeddings,
    persist_directory=str(persist_directory),
)
```

Three arguments, each doing exactly what the earlier notes set up. `collection_name` names the group of vectors. `embedding_function=embeddings` hands Chroma the embedding model — from now on, whenever you give Chroma raw text, it will call this model to turn that text into a vector for you. And `persist_directory` is the on-disk home. The store is now live and empty, waiting for documents.

> [!important] The **`embedding_function`** is the key wiring: you hand Chroma the embedding model **once**, and thereafter you pass it plain text — Chroma embeds it internally. 
> 
> You never call `embed_documents` yourself here; the store does it. The `persist_directory` makes it survive across sessions.

---

## Inserting documents — and why every one needs a unique ID

We need something to store. Here are ten short example documents across four topics (AI, RAG, LLM, and Cricket), each a small dictionary with its text and some metadata:

```python
document_examples = [
    {"topic": "AI",  "doc_number": 1, "text": "Artificial intelligence helps machines perform tasks that usually need human reasoning."},
    {"topic": "AI",  "doc_number": 2, "text": "AI systems can analyze patterns in data to support predictions and automation."},
    {"topic": "AI",  "doc_number": 3, "text": "Responsible AI development includes fairness, transparency, and safety checks."},
    {"topic": "RAG", "doc_number": 4, "text": "RAG combines retrieval with generation so the model can answer using external knowledge."},
    {"topic": "RAG", "doc_number": 5, "text": "A retriever in a RAG pipeline finds relevant chunks before the language model generates an answer."},
    {"topic": "RAG", "doc_number": 6, "text": "Vector stores are important in RAG because they make semantic search over embedded documents possible."},
    {"topic": "LLM", "doc_number": 7, "text": "LLMs generate text by predicting likely next tokens from patterns learned during training."},
    {"topic": "LLM", "doc_number": 8, "text": "Prompt design can improve how clearly an LLM follows instructions and returns useful answers."},
    {"topic": "Cricket", "doc_number": 9,  "text": "Cricket teams score runs through batting partnerships, boundaries, and quick running between the wickets."},
    {"topic": "Cricket", "doc_number": 10, "text": "A cricket bowler can pressure batters with pace, swing, spin, and accurate line and length."},
]
```

Chroma doesn't store raw dictionaries, though — it stores **`Document`** objects (the same `page_content` + `metadata` shape the loaders produced back in the document-loaders module). So we convert each dictionary into a `Document`, and here's the important bit: we give every one a **unique ID** generated by `uuid4()`.

```python
documents = [
    Document(
        id=str(uuid4()),
        page_content=item["text"],
        metadata={"topic": item["topic"], "doc_number": item["doc_number"]},
    )
    for item in document_examples
]
```

Why bother with `uuid4()`? Because IDs in a store must be unique, and if two documents ended up sharing an ID, you'd have a collision — updates and deletes would hit the wrong record, or one document would silently overwrite another. `uuid4()` generates a random, practically-never-colliding identifier (`print(uuid4())` shows something like `f47ac10b-58cc-4372-a567-0e02b2c3d479`), so every document gets its own guaranteed-distinct handle. That handle is what we'll use later to update and delete specific records.

Now insert them. `add_documents` takes the list, embeds each one's text with the `embedding_function` we wired in, and stores the vector alongside its text and metadata:

```python
document_ids = vector_store.add_documents(documents)
```

It returns the list of IDs it stored — the same UUIDs we generated — confirming all ten landed in the collection.

> [!info] `vector_store.add_documents(documents)` embeds each `Document`'s text (via the store's `embedding_function`) and inserts it, returning the stored IDs. 
> Each `Document` carries its own `id=str(uuid4())` so it has a unique, addressable handle — essential for later updating or deleting that exact record without touching others.

---

## Reading the stored data back

Once documents are in, `get()` pulls records straight out of the collection. Ask it to `include` the parts you want — the embeddings, the metadata, the document text:

```python
raw_records = vector_store.get(include=["embeddings", "metadatas", "documents"])
raw_records.keys()
```

This returns a dictionary with `ids`, `embeddings`, `metadatas`, and `documents` keys — and it proves the point : a vector-store record isn't just a vector, it's the embedding **plus** the original text **plus** the metadata, all sitting together. You can even check the shape of the stored vectors:

```python
print(raw_records["embeddings"][0:2, 0:20].shape)
```

If you only want specific records, `get_by_ids` fetches by the UUIDs you hold. Here we grab the last three that were inserted:

```python
selected_ids = document_ids[-3:]
selected_documents = vector_store.get_by_ids(selected_ids)
```

`get()` reads everything (or filters); `get_by_ids()` targets exact records. Neither runs a similarity search — they're direct lookups, the **R** in CRUD.

---

## The main event — similarity search

This is what the whole store exists for. Give it a natural-language query and ask for the `k` closest documents:

```python
query = "How does RAG help an LLM answer questions using outside knowledge?"

search_results = vector_store.similarity_search(query, k=3)
```

Notice you pass **plain text**, not a vector. Chroma embeds the query for you (again via the `embedding_function`), then runs the nearest-neighbour search — using HNSW under the hood, exactly the indexing from note 03 — and returns the `k=3` most semantically similar `Document` objects. For this query, the RAG-topic documents come back on top, because their meaning is closest to the question, even though the question shares few exact words with them. That's semantic search doing its job.

Often you want to know **how** close each match was, not just the ranking. `similarity_search_with_score` returns each document paired with a **distance score**:

```python
vector_store.similarity_search_with_score(query=query, k=4)
```

Each result comes back as `(Document, score)`. The score is a distance, so **lower means more similar** — the nearest neighbour has the smallest score. This is what you'd use to set a relevance threshold (e.g. **ignore anything with a distance above X**) rather than blindly taking the top `k`.

> [!important] `similarity_search(query, k=n)` takes **plain text** — Chroma embeds it internally and returns the `k` nearest `Document`s by meaning (HNSW under the hood). 
> `similarity_search_with_score(query, k=n)` additionally returns a **distance score** per result, where **lower = closer**. Use the plain version for **give me the top k**; use the scored version when you need a relevance cutoff.

---

## Updating documents

Documents change. To update, you address the exact records by their IDs and hand Chroma new `Document`s to replace them. Here we update two — the RAG document (#4) and the LLM document (#8):

```python
ids_to_update = [document_ids[3], document_ids[7]]

updated_examples = [
    {"id": ids_to_update[0], "topic": "RAG", "doc_number": 4,
     "text": "RAG improves answer quality by retrieving relevant context before the language model generates a response."},
    {"id": ids_to_update[1], "topic": "LLM", "doc_number": 8,
     "text": "Well-written prompts help an LLM stay focused, follow instructions, and produce more reliable outputs."},
]

updated_documents = [
    Document(id=item["id"], page_content=item["text"],
             metadata={"topic": item["topic"], "doc_number": item["doc_number"]})
    for item in updated_examples
]

vector_store.update_documents(ids=ids_to_update, documents=updated_documents)
```

`update_documents(ids=..., documents=...)` re-embeds the new text and overwrites those two records **in place** — same IDs, new content and new vectors. This is why unique IDs mattered: they let you surgically replace records 4 and 8 without disturbing the other eight. A `get(ids=ids_to_update)` afterwards shows the fresh text, and re-running the similarity search now surfaces the updated wording.

---

## Deleting documents

Deletion works the same way — by ID. Say we no longer want the two Cricket documents (#9 and #10):

```python
ids_to_delete = [document_ids[8], document_ids[9]]

vector_store.delete(ids=ids_to_delete)
```

`delete(ids=...)` removes exactly those records. Verify with a plain `get()`:

```python
remaining_records = vector_store.get()
remaining_ids = remaining_records["ids"]

print(f"Remaining document count: {len(remaining_ids)}")
```

The count drops from ten to eight, and checking the deleted IDs against `remaining_ids` confirms they're gone. That completes the full **CRUD** set: **C**reate (`add_documents`), **R**ead (`get` / `get_by_ids` / `similarity_search`), **U**pdate (`update_documents`), **D**elete (`delete`).


> [!tip] Interview framing: In code, ChromaDB via LangChain gives you a vector store with full CRUD. 
> 
> You create it with a collection name, an embedding function, and a persist directory; 
> 
> `add_documents` embeds and inserts `Document`s (each with a unique `uuid4` id so it's individually addressable) 
> 
> `similarity_search` takes plain text, embeds it, and returns the k nearest by meaning, with a `_with_score` variant for a distance cutoff; and 
> 
> `update_documents` / `delete` operate by id. 
> 
> The key production detail is the **persist directory** — reopen the same directory and collection in a new process and all vectors load from disk with no re-embedding, which is exactly why you use a vector store instead of an in-memory list.

