Every retriever so far — plain `similarity`, `similarity_score_threshold`, and MMR — rests on the same foundation: embeddings. You embed the query, embed the documents, and compare *meaning*. BM25 is the odd one out. It uses no embedding model, no vector store, and it does not understand meaning at all. It matches **words**. That sounds like a step backwards after all the work on semantic search — but it is a genuinely different tool with its own strengths, and it is the missing half of the hybrid search we build next.

---

## BM25 = Best Match 25 — keyword matching, no embeddings

The name is oddly specific. **BM25 stands for "Best Match 25"** — researchers refined the algorithm over many iterations, and the 25th is the one that gave the best results and stuck. What it does is **keyword matching**: it builds an *inverted index* from the raw text of your documents (a map of which word appears in which document, and how often) and scores documents by how well their words overlap with the query's words. There is no deep-learning model anywhere in the pipeline.

BM25 is built on an older, mature technique you may have met before: **TF-IDF**, which stands for **Term Frequency – Inverse Document Frequency**. BM25 is essentially a refined, better-behaved version of TF-IDF. There is a formula underneath, but we deliberately won't derive it — from an interview and intuition standpoint, what matters is *why* each piece exists, not the algebra. So let's build the intuition from its two halves.

```python
from langchain_community.retrievers import BM25Retriever
# BM25 is keyword-based — no embeddings or vector store required.
# It scores documents by term frequency and inverse document frequency (a TF-IDF variant).
```

---

## Dense vs sparse — the fundamental split

To see what makes BM25 different, contrast the two kinds of representation in play.

An **embedding model** is a deep-learning model whose whole purpose is to capture the **semantic meaning** of text and pack it into numbers. The vector it produces is **dense** — a few hundred to a few thousand numbers, almost all non-zero, every dimension carrying a shard of meaning. That is what every retriever until now has used.

BM25's representation is **sparse**. It doesn't encode meaning; it encodes *word occurrence*. Picture a vector with one slot for every word in the vocabulary — mostly zeros, with non-zero entries only where the document actually contains that word. No neural network, no meaning — just "which words are here, and how often."

```
Dense  (embeddings) → [0.02, -0.41, 0.88, 0.13, ...]  every slot filled, encodes MEANING
Sparse (BM25)       → [0, 0, 3, 0, 0, ..., 1, 0]      mostly zeros, encodes WORD COUNTS
```

This dense-versus-sparse distinction is the whole story: semantic retrieval is dense, keyword retrieval is sparse.

---

## TF — term frequency

The first half of the score asks a simple question: **how often does a query word appear in this document?**

Say an important word in your query is "AI agents." A document in which "AI agents" appears many times is probably *about* AI agents, so it is probably relevant. A document where it never appears probably isn't. So the more often a query term shows up in a document, the higher that document scores. That is term frequency — reward documents that contain the query's words, in proportion to how often they contain them.

---

## IDF — inverse document frequency

Term frequency alone is naive, and here's why. The words that appear *most* often across text are words like "the," "is," "and," "a" — stopwords that carry no meaning. If you scored purely on frequency, every document would win on "the," and matching would be worthless. You need to discount words that are common everywhere and reward words that are **rare**.

That's what **document frequency** measures: how many documents in the whole corpus a word appears in. A word in almost every document (like "the") has high document frequency; a distinctive word appears in only a few. BM25 takes the **inverse** — so rare words get *boosted* and ubiquitous words get *crushed*.

The intuition is that rarity means information. Imagine 100 balls of various colours, and one particular colour appears on only 3 of them. That rare colour is **novel, unique, distinctive** — if a query mentions it, it's a strong, meaningful signal, precisely because so few things have it. A word that appears everywhere tells you nothing about which document to pick; a word that appears in only a handful of documents points sharply at them.

So the BM25 score combines the two: **TF** asks "is this word frequent *here*?" and **IDF** asks "is this word rare *overall*?" A document scores highly when it contains query words that are both frequent in it and rare across the corpus.

> [!info] **BM25 score ≈ TF × IDF.**
> **TF (term frequency)** rewards documents that contain the query's words often. **IDF (inverse document frequency)** rewards words that are *rare* across the whole corpus (distinctive, informative) and discounts words that are common everywhere (stopwords). Together: reward frequent, distinctive words; ignore common ones.

---

## The two refinements BM25 adds over raw TF-IDF

Plain TF-IDF has two flaws that BM25 fixes, and these fixes are the reason it's "BM25" and not just "TF-IDF."

**Term-frequency saturation.** With raw TF, a word appearing 20 times would score four times as high as one appearing 5 times — a straight line. But that's wrong: past a point, repetition stops signalling relevance. A document that says "AI agents" 20 times isn't four times more about AI agents than one that says it 5 times. So BM25 makes term frequency **saturate** — its impact rises at first, then flattens to a hard ceiling beyond which more repetitions add nothing.

![[AI-Engineering/07-RAG/05-Retrievers/Images/05-BM25-TF-Saturation.png]]

On the graph, the x-axis is term frequency and the y-axis is its impact on the score. We explicitly do *not* want linear behaviour. Instead, as term frequency climbs from zero the impact rises steeply, then — somewhere around a modest count — it **stabilises and plateaus**. After that limit, whether the word appears 20 times or 100 times, the impact is the same: *no additional impact*. This is what stops a document from gaming its way to the top by simply repeating a keyword (keyword stuffing).

**Length normalisation.** A long document has higher raw word counts just by being long. If one document is 500 pages, almost any word will appear in it many times, purely because there's more text — not because it's more relevant. Comparing a word that appears 5 times in a short paragraph against 20 times in a 500-page book isn't fair. So BM25 **normalises by document length**, dividing out the advantage that long documents would otherwise get. The final score shouldn't depend on how long the document happens to be.

> [!important] BM25 = TF-IDF + two corrections: **saturation** (term-frequency impact plateaus, so repetition can't run away) and **length normalisation** (long documents don't win just for being long).

---

## BM25's blind spot — it has no idea what words mean

Now the critical weakness, and the reason we didn't stop building retrievers at BM25. Because BM25 matches *words*, it is completely blind to *meaning*.

Take a document about "automobile service" and a query about "car service." A dense embedding retriever handles this effortlessly — "automobile" and "car" sit close in the embedding space because they *mean* the same thing, so the document is retrieved. BM25 sees two different tokens, "automobile" ≠ "car," finds zero overlap, and **fails to retrieve the document at all**. The two are obviously related to a human and to an embedding model, but to keyword matching they are simply different strings. Any time the query and the relevant document express the same idea in *different words* — synonyms, paraphrases, rewordings — BM25 can miss it entirely.

```
query: "car service"        doc: "automobile service"
  dense  → close in meaning     → retrieved ✓
  BM25   → "car" ≠ "automobile" → missed ✗
```

---

## In code — BM25 on three queries

The retriever couldn't be simpler to build: hand it documents and a `k`, no embeddings involved.

```python
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

docs = [
    Document(page_content="Antibiotics inhibit bacterial cell wall synthesis or protein production to stop infection.", metadata={"topic": "medicine"}),
    Document(page_content="Gothic cathedrals use flying buttresses to transfer roof weight outward, enabling tall stained glass windows.", metadata={"topic": "architecture"}),
    Document(page_content="Compound interest calculates returns on both the initial principal and previously earned interest.", metadata={"topic": "finance"}),
    Document(page_content="A stock represents partial ownership in a company and entitles the holder to a share of its profits.", metadata={"topic": "finance"}),
    Document(page_content="Shakespeare wrote 37 plays and 154 sonnets, exploring themes of power, love, and betrayal.", metadata={"topic": "literature"}),
    # ... 12 documents across medicine, architecture, finance, and literature
]

retriever = BM25Retriever.from_documents(docs, k=2)
```

**Query 1 — an exact keyword match, where BM25 shines (and stumbles).** The words "antibiotic" and "bacterial" appear directly in the medicine document:

```python
results1 = retriever.invoke("antibiotic bacterial infection treatment and killing pathogens")
```

```
[1] topic=medicine:    Antibiotics inhibit bacterial cell wall synthesis... to stop infection.   ✓
[2] topic=literature:  Shakespeare wrote 37 plays and 154 sonnets...                             ✗
```

The top hit is exactly right — direct keyword overlap on rare, distinctive words ("antibiotic," "bacterial") nails it. But look at the second result: Shakespeare, which has nothing to do with the query. Because BM25 was asked for `k=2` and only *one* document genuinely shares keywords, it fills the second slot with whatever had the next-highest token overlap (a stray shared common word), even though it's irrelevant. Keyword matching has no notion of "there simply isn't a good second answer."

**Query 2 — keyword overlap across a topic, where BM25 does well.** Words like "compound," "interest," "partial," "company" sit right in the finance documents:

```python
results2 = retriever.invoke("compound interest vs Simple interest and what gives a person partial stakes in a company")
```

```
[1] topic=finance: A stock represents partial ownership in a company...       ✓
[2] topic=finance: Compound interest calculates returns on both the principal... ✓
```

Both finance documents surface, because the query literally contains their distinctive words. When the query and the answer share vocabulary, BM25 is precise and fast.

**Query 3 — a semantic query with no shared keywords, where BM25 fails.** The ideal answer is the Gothic-cathedral document (stained glass windows, an airy structure), but the query describes the *idea* without using the document's *words*:

```python
results3 = retriever.invoke("a structure that feels light and with windows")
```

```
[1] topic=finance:    A stock represents partial ownership in a company...   ✗
[2] topic=literature: Shakespeare wrote 37 plays and 154 sonnets...          ✗
```

BM25 completely misses the cathedral. "Light," "airy," "structure" never literally appear in that document, so there's no keyword overlap to score on, and BM25 returns unrelated documents instead. A dense embedding retriever would have understood that "a structure that feels light with windows" *means* a Gothic cathedral. This is the blind spot made concrete.

---

## Why learn BM25 at all — it's half of hybrid search

If BM25 misses semantic matches, why teach it? Because keyword matching and semantic matching fail in *opposite* situations, and that makes them complementary. BM25 is unbeatable on exact terms — names, product codes, rare technical jargon, identifiers — the very cases where embeddings sometimes blur distinct-but-similar tokens together. Dense retrieval is unbeatable on meaning — synonyms, paraphrases, fuzzy intent — the very cases where BM25 sees no overlap. Neither alone is enough.

The whole reason for covering BM25 now is that the **next technique, hybrid search, combines the two** — running BM25 and a dense embedding retriever together and fusing their results, so you get keyword precision *and* semantic recall. BM25 is a building block; hybrid search is where it pays off.

> [!info] **What BM25 guarantees**
> - Fast, model-free **keyword matching** via an inverted index — no embeddings, no vector store, nothing to train.
> - Strong precision on **exact and rare terms** (names, codes, jargon), with sensible weighting: frequent-here (TF) × rare-overall (IDF), plus saturation and length normalisation.

> [!danger] **What BM25 does *not* do**
> - It has **no understanding of meaning** — synonyms and paraphrases ("car" vs "automobile") are invisible to it, so semantic queries can miss entirely.
> - It will still return `k` documents even when there's no good match, padding with weak keyword overlaps.
> - It is best used **not alone** but as the keyword half of **hybrid search**.

> [!tip] Interview framing
> "BM25 — Best Match 25 — is a keyword retriever, not a semantic one. No embeddings or vector store: it builds an inverted index and scores documents on TF-IDF — term frequency (is the word frequent in this document?) times inverse document frequency (is the word rare across the corpus, hence distinctive?). BM25 adds two refinements over plain TF-IDF: term-frequency saturation, so repeating a word stops helping past a limit, and length normalisation, so long documents don't win just for being long. Its strength is exact and rare terms; its weakness is that it's blind to meaning — 'car' and 'automobile' are different tokens to it, so paraphrased queries fail. That's exactly why it's paired with dense retrieval in hybrid search: keyword precision plus semantic recall."
