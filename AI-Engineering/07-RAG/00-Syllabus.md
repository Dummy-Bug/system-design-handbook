#ai-engineering #rag #retrieval #evals #block-7 #block-8 #syllabus

# Blocks 7-8 · RAG & Retrieval — Syllabus

24 concepts. **Generic** — the field, not Xarvis or the CampusX track. Map afterwards.

**This folder is different from the others: most of Part A is already written.** The 40 existing notes across `00-Fundamentals` … `06-Advanced-Retrievers` (~5,300 lines) cover the ingestion and retrieval mechanics. What's missing is the *production* half — reranking, query transforms, evaluation, authorization, freshness. That's blocks 7-8, and it's where the public retrieval product gets built.

**Currency check (2026-07-30) — sobering baselines.** State-of-the-art RAG answers only **63%** of factual questions correctly; naive RAG manages **44%**. So "we built RAG" is not a claim of working; the gap between those two numbers is the entire engineering discipline. **Contextual retrieval cuts retrieval failure rates by up to 67%** — the single highest-value upgrade available. And the practical rule every source repeats: **add hybrid retrieval and a reranker before reaching for anything more complex.**

RAG evaluation has settled on four core metrics — **faithfulness, answer relevance, context precision, context recall** — with RAGAS the most adopted implementation. Faithfulness above **0.85** is generally good; below **0.70** indicates significant hallucination.

---

## A · Foundations — mostly already written

**1. Why RAG exists, and what it actually solves** → `00-Fundamentals`
**2. Document loading and parsing** → `01-Document-Loaders`
**3. Chunking strategies** — fixed, recursive, structure-aware, semantic, LLM-based → `02-Text-Splitters`
**4. Embeddings, the embedding space, distance metrics, dimensionality** → `03-Embeddings`
**5. Vector stores and ANN indexing — HNSW** → `04-Vector-Stores`
**6. Retrievers** — similarity, score-threshold, MMR, BM25, hybrid/ensemble → `05-Retrievers`
**7. Advanced retrievers** — contextual compression, parent-document, **self-query**, **multi-query** → `06-Advanced-Retrievers` *(**complete** — 6 notes, 12 images)*

*Broadened 2026-07-30 — originally scoped to just contextual compression and parent-document. The course teaches all four as one unit, each with a built-in and a from-scratch implementation, so the module stays intact here rather than sending multi-query to concept 11. **Self-query is the one that reaches past retrieval quality into query understanding** — it is the first retriever in the course to put an LLM *inside* the retrieval path, which makes it the natural bridge to concepts 11-12.*

**Gaps remaining in Part A:** IVF and product quantization (only HNSW is covered); the recall/latency/memory tradeoff across index types; metadata filtering and how pre- vs post-filtering interacts with an ANN index.

## B · Retrieval quality — Block 7

**8. Cross-encoder reranking** → `07-Reranking-And-Query-Transforms` *(**partly done** — 4 notes, 11 images)*
Bi-encoder vs cross-encoder vs late interaction (ColBERT). The retrieve-wide-then-rerank-narrow pattern — typically top-50 down to top-5. Why this is called the secret sauce of production RAG, and when its latency isn't worth it. LLMs as rerankers as the newer variant.

*Written 2026-07-31 from the CampusX reranking lecture: why embeddings make similarity approximate (lossy compression on both sides), bi-encoder vs cross-encoder and the static/dynamic split that explains it, the two-stage filter-then-refine pattern, cross-encoder internals (`[CLS] q [SEP] d [SEP]`, bidirectional self-attention, CLS → linear → sigmoid), and both rerankers in code via `ContextualCompressionRetriever`.*
**Still open on this concept:** **late interaction / ColBERT** and **LLMs as rerankers** — neither appears in the course. Cover separately.

**9. Contextual retrieval**
Prepending chunk-level context before embedding, so a chunk carries its document's meaning. The highest-return single upgrade in current practice. Its cost: an extra generation pass per chunk at index time.

**10. Late chunking**
Embedding all tokens with a long-context model *first*, then chunking, so chunk embeddings retain full context. The honest comparison: more efficient than contextual retrieval, but tends to sacrifice relevance and completeness.

**11. Query transforms** → `07-Reranking-And-Query-Transforms` *(**partly done** — 7 notes, 17 images)*
HyDE, multi-query expansion, step-back prompting, and sub-question decomposition. What each fixes. Where each makes things worse — and decomposition specifically can.

*Written 2026-07-31 from the CampusX RAG Fusion lecture: the user-phrasing dependency, why multi-query's deduplication throws away the rank information, **RRF** in full (`Σ 1/(rank + 60)`, worked example, consistency-over-rank, the constant as a damping dial), the end-to-end pipeline and its unconditional LLM-call/latency/cost, and a from-scratch `RAGFusion` class.*
*Also written 2026-07-31 from the HyDE lecture: the query/document **form asymmetry** (not a word-choice problem — a short question and a long passage embed differently regardless), the query vector landing outside every cluster, the LLM's NLU+NLG writing a hypothetical document as a **search probe**, the fake-document objection and why factual errors are tolerable but topical errors are not, the 2022 paper (Contriever, multiple documents + averaged embeddings), and `CustomHypotheticalDocumentEmbedder`.*
**Still open on this concept:** **step-back prompting**, **sub-question decomposition** as its own technique.

**12. Query understanding and routing**
Classifying intent before retrieving. Routing across multiple distinct corpora — docs, tickets, code, structured tables. When a query shouldn't hit retrieval at all.

**13. Learned sparse retrieval**
SPLADE-style. When to pick it over BM25 or a dense retriever.

**14. Handling hard content**
Tables and charts. Multi-column and scanned PDFs. Code, which retrieves differently from prose. Multilingual corpora. Visual retrieval over page images (ColPali-style) as the escape hatch when parsing loses.

**15. Citations and attribution**
Making citations trustworthy rather than decorative. Span-level grounding. Verifying that a cited source actually supports the claim.

**16. Freshness and index lifecycle**
Updates, deletes, and tombstones. Superseded and versioned documents. Temporal queries — "latest", "as of last year". Re-embedding migration when a better model ships and you have hundreds of millions of vectors indexed.

**17. Deduplication**
Near-duplicates, document versions, boilerplate, quoted email threads. Why duplicates poison both retrieval and evaluation.

## C · Architecture — Block 7

**18. Agentic RAG** → `09-RAG-Architecture` *(**partly done** — 15 notes, corrective RAG + Self-RAG)*
Replacing the linear pipeline with a loop: retrieve, evaluate sufficiency, re-retrieve. Retrieval-as-a-tool. Self-RAG and corrective RAG — and whether they earn their complexity in production.

*Written 2026-07-31 from the CampusX Corrective RAG lecture (**YouTube transcript, no local recording** — so no screenshots in this module): the blind-trust prompt and the retriever that always returns `k`, the parametric-knowledge leak demonstrated live (transformer question answered fluently from four chunks about MLPs/CNNs/regularization/index pages), the **retrieval evaluator** and its three verdicts, **knowledge refinement** (decompose → filter → recompose; T5-large 770M, checkpoint never released), the 0.7/0.3 thresholds and the easily-missed rule that even a **correct** verdict drops documents below the lower threshold, **web search as the incorrect-path fallback** with web docs refined identically so `refine`/`generate` are reused, **query rewriting** before search (and the lecture's honest verdict that it rarely helps), and the **ambiguous path collapsed out of the graph entirely** — two routes, merged via `good_docs + web_docs` inside `refine`, because state persists.*
*Also written 2026-07-31 from the CampusX Self-RAG lecture (again a **YouTube transcript, no recording**): the three problems traditional RAG has — **indiscriminate retrieval** (the "how many seconds in a minute" hedge, where extra context makes a known answer *less* confident), blind trust (semantic similarity matches the **topic**, not the **question type** — "what causes diabetes" retrieving a chunk about effects), and no self-verification; the **four reflection questions** and why grounded ≠ useful; the three support levels including hallucination-as-**invented-correlation** and hallucination-as-**editorialising** (the prompt bans "generous", "culture", "employee-first"); the quote-only reviser as deliberate over-correction; **two nested loops** with independent counters (`MAX_RETRIES=10` inner, `MAX_REWRITE_TRIES=3` outer) plus a raised `recursion_limit`; and the relevance filter deliberately **loosened** across the build once later checks existed.*

**Still open on this concept:** **retrieval-as-a-tool / true agentic RAG** (where an LLM holds the controller role rather than a hand-written router) — a separate lecture. Also: the papers' actual mechanisms, since both course implementations replace fine-tuned models with prompted LLM judges.

**19. GraphRAG and structured knowledge**
When graph structure beats chunks. The cost of building and maintaining it. Where plain RAG structurally fails — aggregation and multi-entity questions.

**20. RAG vs fine-tuning vs long context**
The decision framework. Why "long-context models made RAG obsolete" is wrong, and the precise conditions under which it's right.

## D · Authorization and multi-tenancy — Block 8

**21. Permission-aware retrieval**
ACLs enforced **at the ANN layer**, not after. Why post-filtering a top-k can filter away everything relevant, and why authorization must never be left to the model to "decide". This is the single concept that most separates enterprise RAG from tutorial RAG.

**22. Multi-tenant isolation**
Namespaces vs separate indexes vs metadata filters. Blast radius of a filtering bug. Right-to-erasure inside a vector index. Corpus-poisoning defence when users can add documents.

## E · Evaluation — Block 8

**23. Retrieval metrics**
precision@k, recall@k, MRR, nDCG — what each actually tells you and where each misleads. Building a golden retrieval set without months of labelling. Turning click and thumbs data into retrieval improvements.

**24. Generation metrics and the RAG triad**
Faithfulness, answer relevance, context precision, context recall. RAGAS and the alternatives (DeepEval, TruLens, ARES). The interpretation thresholds. Why component-level evaluation must be separate from end-to-end — the first triage question in any RAG bug is *retrieval miss or generation miss?* Benchmarks worth knowing: RAGBench, CRAG, LegalBench-RAG.

---

## Notes to write

Part A continues in the existing numbered subfolders. Parts B-E get a new subfolder each:

```
07-RAG/
├── 00-Syllabus.md          ← this file
├── 00-Resources.md
├── 00-Fundamentals/ … 06-Advanced-Retrievers/    ← existing, ~5,300 lines
├── 07-Reranking-And-Query-Transforms/            ← concepts 8-13  *(started: reranking done)*
├── 08-Hard-Content-And-Freshness/                ← concepts 14-17
├── 09-RAG-Architecture/                          ← concepts 18-20  *(started: corrective RAG done)*
├── 10-Permission-Aware-Retrieval/                ← concepts 21-22
└── 11-RAG-Evaluation/                            ← concepts 23-24
```

## Deferred

| Topic | Goes to |
|---|---|
| Golden sets, trajectory evals, pass@k | Block 1 |
| Retrieval spans and tracing plumbing | Block 2 |
| LLM-judge mechanics behind RAGAS — biases, calibration | Block 3 |
| Indirect injection via retrieved documents, vector-store weaknesses | Block 4 |
| Embedding and index cost, semantic caching | Block 5 |

## Xarvis mapping

*Filled after learning.* Expect a different split here from every other block: **most of this is parked for the public retrieval product, not applicable to Xarvis.** Xarvis has zero RAG.

The exception is workstream F — if the company-policy RAG feature gets sign-off, concepts 8-11, 15-16, 21 become applicable inside Xarvis too, and concepts 18 and 20 become genuinely interesting there because Xarvis already has the *tool* half. Tool-vs-retrieval routing (concept 12) is the one thing neither a pure-RAG project nor a pure-tool agent can demonstrate.

## Sources to verify against

- [12 advanced RAG techniques beyond naive retrieval, 2026](https://atlan.com/know/advanced-rag-techniques/)
- [RAG is not dead — retrieval patterns that work in 2026](https://dev.to/young_gao/rag-is-not-dead-advanced-retrieval-patterns-that-actually-work-in-2026-2gbo)
- [RAG chunking strategies — 2026 retrieval playbook](https://www.digitalapplied.com/blog/rag-chunking-strategies-2026-retrieval-quality-playbook)
- [RAG evaluation — metrics, tools, and the context gap](https://atlan.com/know/how-to-evaluate-rag-systems-explained/)
- [RAG evaluation 2026 — methods, metrics, frameworks](https://datavlab.ai/post/rag-evaluation-methods-metrics-2026-guide)
- Anthropic — *Contextual Retrieval* (the numbers behind concept 9)
- [Reconstructing Context: evaluating advanced chunking strategies](https://arxiv.org/pdf/2504.19754)
- Corpus: `04-rag-and-retrieval/` all 55 questions — the densest single source for this block
