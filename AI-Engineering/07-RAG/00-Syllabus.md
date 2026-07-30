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
**7. Contextual compression and parent-document retrieval** → `06-Advanced-Retrievers` *(in progress)*

**Gaps remaining in Part A:** IVF and product quantization (only HNSW is covered); the recall/latency/memory tradeoff across index types; metadata filtering and how pre- vs post-filtering interacts with an ANN index.

## B · Retrieval quality — Block 7

**8. Cross-encoder reranking**
Bi-encoder vs cross-encoder vs late interaction (ColBERT). The retrieve-wide-then-rerank-narrow pattern — typically top-50 down to top-5. Why this is called the secret sauce of production RAG, and when its latency isn't worth it. LLMs as rerankers as the newer variant.

**9. Contextual retrieval**
Prepending chunk-level context before embedding, so a chunk carries its document's meaning. The highest-return single upgrade in current practice. Its cost: an extra generation pass per chunk at index time.

**10. Late chunking**
Embedding all tokens with a long-context model *first*, then chunking, so chunk embeddings retain full context. The honest comparison: more efficient than contextual retrieval, but tends to sacrifice relevance and completeness.

**11. Query transforms**
HyDE, multi-query expansion, step-back prompting, and sub-question decomposition. What each fixes. Where each makes things worse — and decomposition specifically can.

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

**18. Agentic RAG**
Replacing the linear pipeline with a loop: retrieve, evaluate sufficiency, re-retrieve. Retrieval-as-a-tool. Self-RAG and corrective RAG — and whether they earn their complexity in production.

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
├── 07-Reranking-And-Query-Transforms/            ← concepts 8-13
├── 08-Hard-Content-And-Freshness/                ← concepts 14-17
├── 09-RAG-Architecture/                          ← concepts 18-20
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
