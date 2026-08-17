The two retrievers so far — plain `similarity` and `similarity_score_threshold` — share a blind spot. Both rank documents by one thing only: how close each document is to the query. Neither of them ever looks at how the retrieved documents relate to **each other**. That sounds harmless until you notice what it does to the results, and fixing it is the whole reason **MMR — Maximal Marginal Relevance** — exists.

---

## The redundancy problem — relevant, but repetitive

Picture a store whose documents include several that all make almost the same point. Here the deep-learning documents are deliberately near-duplicates — three separate sentences that all describe gradient descent:

```python
docs = [
    Document(page_content="Training a deep learning model involves iteratively adjusting weights using gradient descent to minimise the loss.", metadata={"topic": "deep learning"}),
    Document(page_content="Deep learning models are optimised through gradient descent, which updates weights in the direction that reduces the training loss.", metadata={"topic": "deep learning"}),
    Document(page_content="Gradient descent is the core optimisation technique in deep learning, guiding weight updates based on computed gradients of the loss.", metadata={"topic": "deep learning"}),
    Document(page_content="Dropout randomly disables a fraction of neurons during training to prevent overfitting in deep networks.", metadata={"topic": "deep learning"}),
    Document(page_content="Learning rate schedulers dynamically adjust the learning rate during training to improve convergence and avoid overshooting.", metadata={"topic": "deep learning"}),
    # ... plus climate, art, and law documents
]
```

Now ask a plain `similarity` retriever for the top 3 on a query about training and optimisation:

```python
query = "deep learning model training and its optimization techniques"

sim_retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
results = sim_retriever.invoke(query)
```

```
[1] topic=deep learning: Deep learning models are optimised through gradient descent, which updates weights in the direction that reduces the training loss.
[2] topic=deep learning: Training a deep learning model involves iteratively adjusting weights using gradient descent to minimise the loss.
[3] topic=deep learning: Gradient descent is the core optimisation technique in deep learning, guiding weight updates based on computed gradients of the loss.
```

All three results are the **same fact** said three ways. And that is exactly what pure similarity is supposed to do — those three sentences genuinely are the closest to the query. But look at what it costs you downstream.

![[AI-Engineering/07-RAG/05-Retrievers/Images/03-MMR-Redundancy-Problem.png]]

You have a fixed budget of context you can hand the language model — say five slots. Similarity search happily fills the first three (C1, C2, C3) with near-identical chunks. At the back of your mind you feel you have filled the context with **useful information**. You haven't. You have filled three of your precious slots with **duplicate information** — the second and third copies teach the model nothing the first didn't. Worse, the documents about dropout, learning-rate schedulers, and batch normalisation — genuinely different, genuinely useful facets of **training and optimisation** — never made the cut. Redundancy at the top didn't just waste budget; it **narrowed your coverage** of the topic.

> [!danger] Pure similarity retrieval optimises relevance and ignores redundancy.
> Its top-`k` are often near-**duplicates** of each other, so a finite context budget gets spent re-stating one fact instead of covering the topic broadly.

---

## What we actually want — relevance and diversity

Think about what a good set of retrieved chunks should satisfy. Not one property, but two at the same time:

1. **Relevance** — each chunk is useful for the given query. This is still the primary requirement; irrelevant-but-diverse junk is no good.
2. **Diversity** — the chunks are dissimilar **from each other**, so together they cover more ground and carry non-redundant information.

A retriever that chases only the first gives you the redundant pile above. A retriever that balances both is **MMR — Maximal Marginal Relevance**. **Marginal** is the key word: at each step it asks not just **is this document relevant?** but **what new value does this document add on top of what I've already picked?** A document that is highly relevant but nearly identical to one you already selected has little marginal value, so MMR passes it over in favour of something that is a bit less relevant but genuinely new.

---

## How MMR works — step by step

MMR builds its result **one document at a time**, and it starts from a larger pool than it will finally return.

**Step 1 — fetch a candidate pool (`fetch_k`).** Embed the query, run an ordinary similarity search, and pull back `fetch_k` documents — a pool **larger** than the `k` you actually want (in the notebook, `fetch_k=10` to eventually return `k=3`). This first step is pure relevance: the candidate pool is just **the 10 nearest documents.** MMR will only ever choose from within this pool, so `fetch_k` sets how much raw material it has to diversify over.

**Step 2 — seed with the most relevant.** From the candidate pool, take the single document most similar to the query and put it in the **selected** set. The first pick is always just the top relevance hit — there is nothing selected yet to be diverse from.

**Step 3 — iteratively add the best marginal document.** For every remaining candidate `dᵢ`, compute an MMR score and pick the highest, then repeat until you have `k`:

```
MMR(dᵢ) = λ · sim(dᵢ, Q)  −  (1 − λ) · max  sim(dᵢ, dⱼ)
                                       dⱼ ∈ S
```

where `Q` is the query vector and `S` is the set of documents already selected so far. The first term **rewards relevance** to the query. The second term **penalises similarity to what you've already got**. Add the winner to `S`, and go again.

One detail in that penalty term matters a lot: it is a **max**, not an average. You penalise a candidate by its similarity to the **nearest already-selected document**. The reason is that you want the new chunk to be different from **every** document already chosen, not just different on average — averaging would let a candidate that duplicates one selected doc sneak in as long as it's distant from the others. Using `max` means a candidate is only attractive if it stands apart from all of them.

---

## The formula in action — a worked example

Take `λ = 0.5` (an even balance), with `D1` already selected, and two candidates left to choose between:

- **D2** — similarity to the query `0.9` (very relevant), but similarity to the already-selected `D1` is `0.88` (almost a duplicate of it).
- **D3** — similarity to the query `0.75` (less relevant), but similarity to `D1` is only `0.22` (very different from it).

Plug each into the formula. Because `λ = 0.5`, the `(1 − λ)` weight is also `0.5`, so both terms carry the same `0.5`:

![[AI-Engineering/07-RAG/05-Retrievers/Images/04-MMR-Worked-Example-Calc.png]]

```
MMR(D2) = 0.5 × 0.9  − (0.5 × 0.88) = 0.45  − 0.44 = 0.01
MMR(D3) = 0.5 × 0.75 − (0.5 × 0.22) = 0.375 − 0.11 = 0.274
```

**D3 wins**, by a mile — `0.274` against `0.01` — even though D2 is the **more relevant** document to the query. D2's high relevance (`0.9`) is almost entirely cancelled by its high redundancy with D1 (`0.88`): its marginal value is nearly zero. D3 is a little less relevant but brings genuinely new information, so its marginal value is far higher. The final retrieval is `{D1, D3}` — two documents that are both on-topic **and** diverse, D3 carrying the non-redundant coverage that plain similarity would have thrown away.

> [!info] MMR picks the document with the highest **marginal** value: relevant to the query, but **new** relative to what's already selected. A near-duplicate of an existing pick is rejected even when it scores high on raw relevance.

---

## The λ dial — `lambda_mult`

The single number `λ` (passed as `lambda_mult`) slides you along the relevance-versus-diversity spectrum:

```
λ = 1.0   pure relevance     second term vanishes → identical to plain similarity search
λ = 0.5   balanced (default) equal weight to being relevant and being different
λ = 0.0   pure diversity     first term vanishes → ignores the query, just spreads out
```

At `λ = 1.0` MMR **is** similarity search — with no diversity penalty it just takes the nearest documents. At `λ = 0.0` it stops caring whether documents even answer the question and only maximises how spread-out they are. The useful range lives in between, and `0.5` is the sensible default.

---

## Watching λ sweep in code

MMR is just another `search_type`. Its `search_kwargs` add the two parameters we've met — `fetch_k` (candidate-pool size) and `lambda_mult` (the dial) — on top of the final `k`:

```python
query = "deep learning model training and its optimization techniques"

for lm in [1.0, 0.7, 0.5, 0.0]:
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3, "fetch_k": 10, "lambda_mult": lm},
    )
    results = retriever.invoke(query)
    print(f"=== lambda_mult={lm} ===")
    for i, doc in enumerate(results, 1):
        print(f"  [{i}] topic={doc.metadata['topic']}: {doc.page_content}")
```

Reading the output from top to bottom is the entire lesson — the same query, only `λ` changing:

```
=== lambda_mult=1.0 ===   (pure relevance)
  [1] deep learning: ...optimised through gradient descent...
  [2] deep learning: ...iteratively adjusting weights using gradient descent...
  [3] deep learning: Gradient descent is the core optimisation technique...
        ↳ three near-duplicate gradient-descent docs — identical to plain similarity

=== lambda_mult=0.7 ===   (mostly relevance, some diversity)
  [1] deep learning: ...optimised through gradient descent...
  [2] deep learning: Learning rate schedulers dynamically adjust the learning rate...
  [3] deep learning: Dropout randomly disables a fraction of neurons...
        ↳ still all deep learning, but now three DIFFERENT facets — the redundancy is gone

=== lambda_mult=0.5 ===   (balanced)
  [1] deep learning: ...optimised through gradient descent...
  [2] deep learning: Learning rate schedulers dynamically adjust the learning rate...
  [3] climate: Carbon capture technology removes CO2...
        ↳ diversity now strong enough to pull in a different TOPIC

=== lambda_mult=0.0 ===   (pure diversity)
  [1] deep learning: ...optimised through gradient descent...
  [2] art: Abstract expressionism prioritises spontaneous... creation.
  [3] climate: The permafrost in Siberia contains vast amounts of methane...
        ↳ relevance abandoned — results are maximally spread out, mostly off-topic
```

At `1.0` you get the redundant pile. Nudge down to `0.7` and the duplicates are replaced by dropout and learning-rate schedulers — still all about deep-learning training, just the **different** facets of it, which is usually exactly what you want. By `0.5` the diversity pressure is strong enough to reach into other topics (climate). At `0.0` it has stopped answering the question at all, returning an art document and a permafrost document purely because they are far apart. The sweep makes the trade-off tangible: too high and you re-duplicate, too low and you drift off-topic.

---

## What MMR gives you — and what it doesn't

> [!info] **What MMR guarantees**
> - Results that balance **relevance to the query** with **diversity among the results**, tuned by `lambda_mult`.
> - **Non-redundant coverage** — near-duplicates are penalised, so a finite context budget covers more of the topic.
> - Full control via `k` (final count), `fetch_k` (candidate pool), and `lambda_mult` (the relevance–diversity dial).

> [!danger] **What MMR does not do**
> - It is **not free of tuning** — `λ` too high re-introduces redundancy, `λ` too low drifts off-topic; `fetch_k` too small leaves it nothing to diversify over.
> - It **only diversifies within the `fetch_k` pool** — a genuinely different but lower-ranked document that never entered the candidate pool can't be chosen.
> - It does **not measure factual novelty** — **diverse** here means **dissimilar embeddings**, which usually but not always means genuinely new information.

> [!tip] Interview framing
> **MMR — Maximal Marginal Relevance — fixes redundancy in retrieval. Plain similarity ranks only by closeness to the query, so its top-k are often near-duplicates that waste a finite context budget. MMR instead picks documents one at a time to maximise `λ·relevance − (1−λ)·max-similarity-to-already-selected` — it rewards relevance but penalises overlap with what's already chosen, using the max so each new chunk differs from every selected one. It first fetches a larger `fetch_k` pool by relevance, then diversifies down to `k`. `lambda_mult` is the dial: 1.0 is pure relevance (equals similarity search), 0.0 is pure diversity, 0.5 is a balanced default. You reach for MMR when your corpus has lots of near-duplicate chunks and you want broad, non-redundant coverage in the context you hand the LLM.**
