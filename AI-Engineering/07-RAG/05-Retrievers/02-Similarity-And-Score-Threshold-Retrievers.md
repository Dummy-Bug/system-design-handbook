## Building a store to retrieve from

Both notebooks start the same way — a handful of small documents across a few topics, embedded and dropped into a Chroma collection. The topic metadata is there so we can see, at a glance, whether the retriever pulled back the right subject.

```python
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()

docs = [
    Document(page_content="Rockets work by expelling gas at high speed, generating thrust through Newton's third law of motion.", metadata={"topic": "space"}),
    Document(page_content="The International Space Station orbits Earth at about 400 km altitude and travels at 28,000 km/h.", metadata={"topic": "space"}),
    Document(page_content="DNA is a double-helix molecule that carries the genetic instructions for all living organisms.", metadata={"topic": "biology"}),
    Document(page_content="Photosynthesis allows plants to convert sunlight, water, and CO2 into glucose and oxygen.", metadata={"topic": "biology"}),
    Document(page_content="Mitochondria generate ATP through cellular respiration, powering nearly all cellular processes.", metadata={"topic": "biology"}),
    Document(page_content="The Roman Empire at its peak covered over 5 million square kilometers across three continents.", metadata={"topic": "history"}),
    # ... a dozen documents in total, across space / biology / history / geography
]

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    collection_name="similarity_search_demo",
)
```

`Chroma.from_documents` is the one-shot ingest from the vector-store module — it creates the collection, embeds every document, and inserts them in a single call. We now have a populated store to point a retriever at.

---

## Search type 1 — plain similarity (fixed top-k)

The first and simplest search type is `"similarity"`: return the `k` nearest documents to the query, where you choose `k`.

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2},
)
```

`search_type="similarity"` picks the algorithm — ordinary nearest-neighbour search. `search_kwargs={"k": 2}` is that algorithm's one parameter: *always bring back the 2 closest documents.* This is the retriever wrapper around the exact same operation `similarity_search` did — but now it is a reusable object with a standard interface.

Drive it with `.invoke()`, handing it plain text:

```python
query = "How do rockets work?"

results = retriever.invoke(query)

print(f"{query}\n")
for i, doc in enumerate(results, 1):
    print(f"Result {i} [topic={doc.metadata['topic']}]")
    print(f"{doc.page_content}")
    print()
```

The query embeds internally, the search runs, and the two nearest chunks come back — the space-topic documents about rockets and the ISS, because their meaning sits closest to the question. Notice the metadata (`topic=space`) travelled back with each result, exactly as the theory promised.

For comparison, the store's raw method returns the same thing without the retriever object wrapped around it:

```python
query = "How do cells generate their energy?"

results = vectorstore.similarity_search(query, k=3)
```

Same nearest-neighbour search, same kind of result — the difference is purely that `.as_retriever(...)` gives you a composable *component*, while `.similarity_search(...)` is a bare method call on the store.

> [!info] `search_type="similarity"` with `search_kwargs={"k": n}` returns **exactly the `n` nearest documents** — a fixed count, chosen by you.

---

## The blunt edge of a fixed k

`k` is simple, but it is *blind to quality*. It returns `k` documents no matter what — even when that is the wrong number.

Ask for `k=2` when only **one** document is genuinely relevant, and you still get two: the retriever pads the result with the next-nearest chunk even though it is a weak, barely-related match, and that weak chunk now pollutes the context you hand the LLM. Ask for `k=2` when **five** documents are all strongly relevant, and you throw three good ones away. `k` cannot see how good the matches are — it only counts. What you often want instead is: *"give me everything that clears a quality bar, however many that turns out to be."* That is the second search type.

---

## Search type 2 — similarity score threshold (a quality bar)

`"similarity_score_threshold"` flips the philosophy. You do **not** pass a `k`. You pass a `score_threshold`, a single float, and the retriever returns **every document whose similarity to the query is at or above that bar** — which might be five documents, might be one, might be zero. The count is now *dynamic*, decided by the data rather than fixed by you.

```python
query = "How does ML model training work?"

threshold = 0.43

retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": threshold},
)

results = retriever.invoke(query)
```

Before we watch it run, there is one subtlety the lecture spends real time on — and it is the single most confusing thing about score thresholds.

---

## The score subtlety — distance vs similarity, and the `1 − score` trick

When you ask the store directly for scores, what it hands back is a **distance**, and for a distance **lower means closer**:

```python
similarity_scores = vectorstore.similarity_search_with_score(query, k=3)

for doc, score in similarity_scores:
    print(f"Score: {score:.4f} | Topic: {doc.metadata['topic']} | Content: {doc.page_content}")
```

```
Score: 0.5683 | Topic: ml | Content: Training data quality and quantity are the most important factors...
Score: 0.5720 | Topic: ml | Content: Supervised learning trains models on labeled input-output pairs...
Score: 0.6079 | Topic: ml | Content: Overfitting occurs when a model memorises training data...
```

The best match has the *smallest* number (0.5683), because it is the smallest distance. But a phrase like "score **threshold**" naturally means "keep the ones scoring **high**." The two conventions point in opposite directions — and that mismatch is exactly the trap. The threshold retriever works on a **similarity** score where **higher means better**, and it gets there by converting the distance with a simple `1 − distance`:

```python
for _, score in similarity_scores:
    print(f"Similarity Score: {1 - score:.4f}")
```

```
Similarity Score: 0.4317
Similarity Score: 0.4280
Similarity Score: 0.3921
```

Now the numbers read the intuitive way: the nearest document scores highest (0.4317), and they descend from there. This conversion is only meaningful because the collection was built on **cosine** distance — the notebook sets that explicitly when it creates the store:

```python
vectorstore = Chroma(
    embedding_function=embeddings,
    collection_name="demo",
    collection_configuration={"hnsw": {"space": "cosine"}},
)
```

Setting `space: cosine` in the HNSW index is what makes cosine distance the thing being measured, so that `1 − distance` lands in a sensible similarity range. Hold the mental model: **the store measures distance (lower = closer); the threshold retriever converts to similarity (higher = closer) and keeps everything above your bar.**

> [!important] `similarity_search_with_score` returns a **distance** — *lower = more similar*.
> The `similarity_score_threshold` retriever compares against a **similarity** score — *higher = more similar* — obtained as `1 − distance`. Same ranking, inverted number. Mixing the two up is the classic reason a threshold "returns nothing when it obviously should return something."

---

## Watching the threshold bite

With the similarity scores in hand — 0.4317, 0.4280, 0.3921 — a threshold of `0.43` clears exactly one of them:

```
=== Threshold = 0.43 — 1 document(s) returned ===
  [1] topic=ml: Training data quality and quantity are the most important factors in model performance.
```

Only the 0.4317 document sits at or above 0.43, so **one** document comes back. That is the threshold doing precisely its job — gating on quality, not on count.

Now the danger. Set the bar *above* your best match and the retriever returns an **empty list**:

```python
results   # threshold set too high
```

```
[]
```

Nothing clears the bar, so nothing is retrieved — and a downstream pipeline that assumed it would always get context now has none. This is the flip side of the dynamic count: a threshold that is too strict silently starves the LLM, while a threshold that is too loose lets weak, off-topic chunks flood the context. The right value is not universal — it depends on your embedding model and your corpus, and you tune it by watching, as the lecture does, how the retrieved set grows and shrinks as you slide the threshold up and down.

---

## k versus threshold — choosing between them

```
search_type="similarity"                 search_type="similarity_score_threshold"
  fix the COUNT (k)                         fix the QUALITY BAR (score_threshold)
  always returns exactly k                  returns however many clear the bar (0..N)
  blind to how good matches are             gates on match quality
  predictable size, may include weak docs   variable size, may return nothing
  good when downstream wants a fixed number good when "nothing" beats "garbage"
```

Reach for **`similarity` / k** when the rest of your pipeline expects a fixed amount of context — for instance, you always want to stuff the top 3 chunks into a prompt of known size. Its weakness is that it cannot tell a strong match from a filler one; it just returns `k`.

Reach for **`similarity_score_threshold`** when you would rather return nothing than return junk — when a confidently wrong answer built on an irrelevant chunk is worse than an honest "I don't know." Its cost is that the threshold is a real tuning parameter you have to calibrate, and set carelessly it returns either too much or nothing at all.

> [!tip] Interview framing
> "The two basic retriever search types answer 'how many documents come back' in opposite ways. `search_type='similarity'` with `k` returns a fixed number of nearest neighbours — predictable, but blind to quality, so it'll pad with weak matches or drop good ones. `search_type='similarity_score_threshold'` instead returns every document above a similarity cutoff, so the count is dynamic and quality-gated — it can even return nothing. The gotcha is the score itself: `similarity_search_with_score` gives a *distance* where lower is closer, but the threshold retriever works on a *similarity* of `1 − distance` where higher is closer, which is why the collection is built on cosine space. Use k when downstream needs a fixed amount of context; use the threshold when you'd rather return nothing than something irrelevant."
