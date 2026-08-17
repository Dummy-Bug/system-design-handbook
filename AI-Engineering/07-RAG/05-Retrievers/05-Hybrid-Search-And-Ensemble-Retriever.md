The previous note ended on a cliffhanger: BM25 is precise on exact keywords but blind to meaning, while dense embedding retrieval understands meaning but can blur distinct rare terms together. They fail in opposite situations. The obvious move is to run **both** and combine their results — and that is exactly what **hybrid search** does. The tool that makes it possible is a new kind of retriever, the **ensemble retriever**, so this note covers two things at once: the ensemble retriever (the component) and hybrid search (the technique you build with it).

---

## The ensemble retriever — combining retrievers

The word **ensemble** should ring a bell from machine learning. An **ensemble** combines several models' predictions into one final prediction — a voting ensemble, for instance, runs several classifiers and picks the answer the majority voted for. The intuition is that many imperfect predictors, pooled, beat any single one.

An **ensemble retriever** applies that same idea to retrieval: instead of one retriever, you run **several** and merge their results. You configure it with just two things:

1. **A list of retrievers** — which retrievers to run (say, a dense semantic retriever and a BM25 keyword retriever).
2. **A weight per retriever** — how much to trust each one's results. Give a strong semantic retriever a weight of `0.6` and an MMR retriever `0.4`, and the first one's rankings count for more when the results are merged.

Each retriever runs independently and returns its own ranked list; the ensemble then fuses those lists into a single ranking, letting the weights decide whose opinion carries more.

---

## The fusion problem — different retrievers, different ranks

Merging isn't as trivial as it sounds, and it's worth seeing why. Each retriever scores documents its **own** way — BM25 produces keyword scores, a dense retriever produces distance scores — so the same document can sit at a different **rank** in each list. Worse, the two lists only partly overlap: some documents are unique to one retriever, and some appear in both.

![[AI-Engineering/07-RAG/05-Retrievers/Images/06-Hybrid-Rank-Fusion.png]]

Picture the two result lists laid side by side. One document, `D5`, is ranked 2nd by one retriever; `D6` is 3rd; some documents show up in only one list. Your final retrieval needs to be a **single** ranked list — `D1, D5, D6, D8, …` — so the question is: **how do you fuse two differently-scored, partly-overlapping ranked lists into one?** You can't just compare the raw scores, because a BM25 score and a cosine distance aren't on the same scale.

The technique that solves this is **rank fusion** — specifically **Reciprocal Rank Fusion (RRF)**. The key idea is that it ignores the raw scores and looks only at each document's **rank position** in each list. A document scores higher the nearer the top it appears, and a document that appears in **multiple** lists accumulates score from each — so items both retrievers agree on rise to the top. There's a small constant in the formula (often written `k`, default **60**) that softens how much the very top ranks dominate. The full RRF mathematics belongs to the later **RAG Fusion** topic; for now the intuition is enough: **fuse by rank, reward agreement, don't compare raw scores directly.**

---

## Hybrid search — dense and sparse, together

Hybrid search is simply the ensemble retriever put to its most useful purpose: **an ensemble of a dense (semantic) retriever and a sparse (BM25 keyword) retriever.** You get the recall of semantic search — it finds documents that **mean** the right thing even with different words — and the precision of keyword search — it nails exact, rare terms. The vaccine example below makes the complementarity concrete.

---

## In code — building a hybrid retriever

The imports bring together everything from the last few notes — Chroma and embeddings for the dense side, `BM25Retriever` for the sparse side, and `EnsembleRetriever` to fuse them:

```python
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
```

The document set is designed to expose the difference between keyword and semantic retrieval. Two documents literally contain the word **vaccine**; three more are about the immune system — **semantically** about vaccination but never using that exact word; the remaining seven are unrelated (programming, history, nature):

```python
docs = [
    Document(page_content="Vaccines work by introducing a weakened or inactivated pathogen to trigger an immune response.", metadata={"topic": "health"}),          # 1 — has "vaccine"
    Document(page_content="The flu vaccine is reformulated each year to match the most prevalent circulating virus strains.", metadata={"topic": "health"}),             # 2 — has "vaccine"
    Document(page_content="The immune system produces antibodies that recognise and neutralise foreign pathogens in the body.", metadata={"topic": "health"}),          # 3 — immune, no "vaccine"
    Document(page_content="Herd immunity occurs when enough of a population becomes resistant to a disease, slowing its spread.", metadata={"topic": "health"}),           # 4 — immune, no "vaccine"
    Document(page_content="White blood cells called B-lymphocytes produce proteins that bind to and destroy specific antigens.", metadata={"topic": "health"}),         # 5 — immune, no "vaccine"
    Document(page_content="Docker containers package applications with their dependencies for consistent deployment.", metadata={"topic": "programming"}),               # 6–12 — unrelated
    # ... programming, history, and nature documents
]
```

Now build the two retrievers. The **dense** side is an ordinary Chroma similarity retriever fetching the top 4:

```python
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings, collection_name="hybrid_search")

chroma_retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4},
)
```

The **sparse** side is a BM25 retriever fetching the top 2. Note the `bm25_variant="plus"` — because these documents are very short, the **plus** variant of BM25 gives better results on them:

```python
bm25_retriever = BM25Retriever.from_documents(docs, k=2, bm25_variant="plus")
```

Finally, fuse them with the ensemble, weighting the dense retriever more heavily than the keyword one:

```python
ensemble_retriever = EnsembleRetriever(
    retrievers=[chroma_retriever, bm25_retriever],
    weights=[0.8, 0.2],
)
```

---

## What each retriever returns — and why hybrid wins

Run the same query through all three and the division of labour is unmistakable:

```python
query = "How do vaccines work to protect against diseases?"
```

**BM25 alone (keyword)** — it matches the literal word **vaccine,** so it finds document 1, but its second slot is noise, and crucially it **misses every immune-system document** because those never contain the word **vaccine**:

```
=== BM25 Only (keyword match) ===
  [1] health:      Vaccines work by introducing a weakened or inactivated pathogen...   ✓
  [2] programming: REST APIs communicate over HTTP using standard methods like GET...   ✗ (noise)
```

**Chroma alone (semantic)** — it understands that antibodies, herd immunity, and B-lymphocytes are **about** how vaccines work, so it pulls back all four health documents, including the immune-system ones BM25 couldn't see:

```
=== ChromaDB Only (semantic match) ===
  [1] health: Vaccines work by introducing a weakened or inactivated pathogen...        ✓
  [2] health: The immune system produces antibodies that recognise and neutralise...    ✓ (BM25 missed this)
  [3] health: The flu vaccine is reformulated each year...                              ✓
  [4] health: White blood cells called B-lymphocytes produce proteins...               ✓ (BM25 missed this)
```

**The ensemble (hybrid)** — RRF fuses the two lists into one, giving the **union** of what each found: the four semantic documents on top (the dense retriever's weight is `0.8`, so its rankings dominate), plus the one document BM25 uniquely contributed appended at the end:

```
=== Ensemble / Hybrid (keyword + semantic) ===
  [1] health:      Vaccines work by introducing a weakened or inactivated pathogen...   ✓
  [2] health:      The immune system produces antibodies...                             ✓
  [3] health:      The flu vaccine is reformulated each year...                         ✓
  [4] health:      White blood cells called B-lymphocytes...                            ✓
  [5] programming: REST APIs communicate over HTTP...                                   ← BM25's unique add
```

The **weights** control the balance. At `[0.8, 0.2]` the semantic side dominates and BM25's contribution lands last, at position 5. Shift the weights toward BM25 — say `[0.6, 0.4]` — and the documents BM25 favours climb higher up the fused list. Tuning those two numbers is how you dial between **trust meaning** and **trust exact words** for your particular data and queries.

---

## The catch — `EnsembleRetriever` is on its way out

There's an important practical caveat. The `EnsembleRetriever` has one clear upside and one real downside.

**The good:** it's a ready-made component. You get hybrid search and RRF fusion out of the box, with no need to write fiddly merging code yourself — just hand it a list of retrievers and their weights.

**The bad:** it lives in LangChain's `langchain_classic` module, and that module's support is scheduled to end (around December 2026). Code that depends on it today may break tomorrow. That is precisely why you can rebuild the same behaviour as a **custom ensemble retriever** — by inheriting from LangChain's base retriever class, you get a component with the same standard `.invoke()` interface that plugs into a pipeline exactly like the built-in one, but which you own and control. Any class becomes a first-class LangChain retriever the moment it inherits from that base retriever; the custom version is future-proof where the classic one isn't. Building it by hand also drags the Reciprocal Rank Fusion out into the open — the companion note **Custom Ensemble Retriever** writes the whole class out and works the RRF scores by hand.

> [!info] **What hybrid search gives you**
> - **The strengths of both** keyword and semantic retrieval at once — BM25's exact-term precision plus dense retrieval's semantic recall, via an `EnsembleRetriever`.
> - **Tunable balance** through per-retriever `weights`, fused by **Reciprocal Rank Fusion** so differently-scored lists merge sensibly by rank.

> [!danger] **What to watch out for**
> - The built-in `EnsembleRetriever` is in **`langchain_classic`**, whose support is ending (~Dec 2026) — prefer a **custom ensemble retriever** for anything long-lived.
> - Hybrid can still surface a retriever's noise (BM25's stray keyword match rode along into the fused results) — the weights damp this but don't erase it.
> - It runs **two retrievers per query**, so it costs more than either alone.

> [!tip] Interview framing
> **Hybrid search combines keyword and semantic retrieval to get the best of both — BM25's precision on exact, rare terms and dense embeddings' recall on meaning. You implement it with an ensemble retriever: you give it a list of retrievers and a weight for each, it runs them all, and it fuses their ranked lists with Reciprocal Rank Fusion — which merges by rank position rather than raw score and rewards documents both retrievers agree on. The classic example is a query about 'how vaccines work': BM25 catches the documents literally containing 'vaccine' but misses the immune-system ones, dense retrieval catches all the semantically related ones, and the hybrid gives you the union. One caveat: LangChain's built-in `EnsembleRetriever` is in the deprecated `langchain_classic` module, so for production you'd build a custom ensemble retriever by subclassing the base retriever.**
