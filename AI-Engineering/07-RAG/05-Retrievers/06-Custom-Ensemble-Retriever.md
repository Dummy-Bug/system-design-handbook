The previous note ended on a warning: the built-in `EnsembleRetriever` that powers hybrid search lives in `langchain_classic`, a module whose support is scheduled to end (around December 2026). Relying on a component that's being deprecated is risky for anything long-lived. The fix is to **build the ensemble retriever yourself** — and the payoff isn't just future-proofing. Writing it by hand forces the Reciprocal Rank Fusion that was a black box in the last note out into the open, so you finally see *exactly* how two ranked lists get merged into one.

---

## Why build your own

Two reasons, one practical and one educational.

**Practical:** any class becomes a first-class LangChain retriever the moment it inherits from the framework's base retriever, `BaseRetriever`. Subclass it, implement one method, and you get a component with the same standard `.invoke()` interface as every built-in retriever — it drops into a pipeline identically, but you own the code, so no deprecation can pull it out from under you.

**Educational:** the built-in ensemble hid the fusion. When you write the fusion yourself, RRF stops being a name and becomes a few lines of arithmetic you fully control — including the `rrf_k` constant we only mentioned before.

---

## Reciprocal Rank Fusion, written out

Here is the rule the custom retriever implements. For a document `d`, its fused score sums a contribution from every retriever that returned it:

```
score(d) = Σ over retrievers i of  [ weight_i × ( 1 / (rank_i(d) + rrf_k) ) ]
```

Three things to read out of that formula:

- **It uses rank, not raw score.** `rank_i(d)` is where retriever `i` placed the document (0 for the top hit, 1 for the next, …). This is what lets you fuse a BM25 keyword score and a cosine distance that were never on the same scale — you throw the raw scores away and keep only the ordering.
- **`rrf_k` is a smoothing constant** (default **60**). It sits in the denominator to *dampen* the advantage of the very top ranks. Without it, rank 0 would score `1/0` and dominate everything; with `rrf_k = 60`, rank 0 scores `1/60` and rank 1 scores `1/61` — close together, so lower-ranked results still meaningfully contribute instead of being crushed by the leader.
- **A document in multiple lists accumulates.** Because the score *sums* across retrievers, a document both retrievers returned gets two contributions and rises to the top. Agreement is rewarded. A document not returned by a given retriever simply contributes 0 for that one.

---

## The custom retriever class

The whole thing is one subclass of `BaseRetriever` with one method to implement, `_get_relevant_documents`:

```python
from typing import List
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun


class MyEnsembleRetriever(BaseRetriever):
    """Fuses results from multiple retrievers using Reciprocal Rank Fusion (RRF)."""

    retrievers: List[BaseRetriever]
    weights: List[float]
    rrf_k: int = 60

    def _get_relevant_documents(
        self, query: str, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        # 1. Run every retriever, collecting each one's ranked list.
        all_results: List[List[Document]] = [
            retriever.invoke(query) for retriever in self.retrievers
        ]

        # 2. Accumulate an RRF score per document, keyed by its text.
        doc_scores: dict[str, tuple[float, Document]] = {}
        for retriever_idx, results in enumerate(all_results):
            weight = self.weights[retriever_idx]
            for rank, doc in enumerate(results):
                rrf_score = weight * (1.0 / (rank + self.rrf_k))
                key = doc.page_content
                if key in doc_scores:
                    prev_score, prev_doc = doc_scores[key]
                    doc_scores[key] = (prev_score + rrf_score, prev_doc)   # seen before → add
                else:
                    doc_scores[key] = (rrf_score, doc)                     # first time → set

        # 3. Sort by fused score, highest first, and return the documents.
        sorted_docs = sorted(doc_scores.values(), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in sorted_docs]
```

Walk the three steps. First it calls `.invoke(query)` on each sub-retriever, gathering their ranked lists — this is why the sub-retrievers can be *anything* with an `.invoke`, dense or sparse. Second, it loops every list with `enumerate`, so `rank` is the 0-indexed position, computes `weight × 1/(rank + rrf_k)`, and folds it into a dictionary keyed by the document's text: if the document was already scored by another retriever, the new contribution is **added** to the old (that's the "reward agreement" step); otherwise it's stored fresh. Third, it sorts by the accumulated score, descending, and returns the documents. That dictionary-keyed-by-`page_content` is how a document appearing in both lists gets merged into a single entry rather than duplicated.

Instantiate it exactly like the built-in — a list of retrievers, matching weights, and the RRF constant:

```python
my_ensemble = MyEnsembleRetriever(
    retrievers=[chroma_retriever, bm25_retriever],
    weights=[0.8, 0.2],
    rrf_k=60,
)
```

---

## Watching the fusion produce the ranking

Run the vaccine query from the last note through it — same dense retriever (`k=4`, weight `0.8`) and BM25 retriever (`k=2`, weight `0.2`) — and it reproduces the built-in ensemble's output exactly:

```
=== MyEnsembleRetriever (custom RRF fusion) ===
  [1] health:      Vaccines work by introducing a weakened or inactivated pathogen...
  [2] health:      The immune system produces antibodies...
  [3] health:      The flu vaccine is reformulated each year...
  [4] health:      White blood cells called B-lymphocytes...
  [5] programming: REST APIs communicate over HTTP...
```

Now that you have the formula, you can see *why* that's the order. Score each document by hand (`rrf_k = 60`):

```
Dense list (weight 0.8):            BM25 list (weight 0.2):
  rank 0  Vaccines      0.8/60      rank 0  Vaccines    0.2/60
  rank 1  immune-system 0.8/61      rank 1  REST APIs   0.2/61
  rank 2  flu vaccine   0.8/62
  rank 3  B-lymphocytes 0.8/63

Fused (sum across lists):
  Vaccines       0.8/60 + 0.2/60 = 0.01333 + 0.00333 = 0.01667   ← in BOTH lists → #1
  immune-system  0.8/61                    = 0.01311                          → #2
  flu vaccine    0.8/62                    = 0.01290                          → #3
  B-lymphocytes  0.8/63                    = 0.01270                          → #4
  REST APIs      0.2/61                    = 0.00328                          → #5
```

The "Vaccines" document wins outright because it's the *only* document both retrievers returned, so RRF adds both contributions — fusion rewarding agreement, made concrete. The three immune-system documents follow in the order the dense retriever ranked them, their `0.8` weight keeping them well clear of anything BM25-only. And "REST APIs," which only the low-weighted BM25 retriever surfaced, lands dead last. Every position in that list is a direct consequence of the one-line RRF score.

---

## What you gain

> [!info] **What the custom ensemble retriever gives you**
> - The **same hybrid behaviour** as the built-in `EnsembleRetriever`, but as code you own — **future-proof** against the `langchain_classic` deprecation.
> - A **fully transparent, tunable fusion** — the RRF formula and its `rrf_k` smoothing constant are yours to adjust, not a black box.
> - A drop-in **`BaseRetriever` subclass** — because it inherits the base class, it has the standard `.invoke()` interface and composes into a pipeline exactly like any built-in retriever.

> [!tip] Interview framing
> "The built-in `EnsembleRetriever` is in the deprecated `langchain_classic` module, so for anything long-lived you subclass `BaseRetriever` and implement `_get_relevant_documents` yourself. Inside, you invoke each sub-retriever, then fuse their ranked lists with Reciprocal Rank Fusion: each document scores `weight × 1/(rank + rrf_k)` summed over the retrievers that returned it, keyed by document text so a document in both lists accumulates and rises. `rrf_k` defaults to 60 and dampens the top ranks so lower results still count. It reproduces the built-in's output but you own and control every line — and writing it is the clearest way to actually understand RRF."
