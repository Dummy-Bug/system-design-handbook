#ai-engineering #cost #latency #caching #routing #block-5 #syllabus

# Block 5 · Cost & Latency Engineering — Syllabus

16 concepts. **Generic** — the field, not Xarvis. Map afterwards.

> Learn the full surface first, *then* decide what Xarvis can demonstrate. Xarvis is single-model and single-provider today, so several concepts here will land as costed proposals rather than shipped systems — which is a legitimate interview answer if framed honestly.

**Currency check (2026-07-30) — the defining paradox:** token prices fell roughly **80% between 2025 and 2026**, and enterprise LLM API spend still passed **$8.4B in 2025** and is on track to double again. Prices collapsing while bills explode. The lesson: unit-cost improvements get consumed by volume growth, so cost engineering is a permanent discipline, not a one-time cleanup.

Current headline numbers to know: **prompt caching cuts cached input cost by ~90%** · **batch APIs are ~50% cheaper** (availability and discount vary by provider — verify against current docs) · **confidence-gated routing delivers ~95% of frontier quality at a 75-85% cost cut**.

---

## A · Where the money and the milliseconds go

**1. Token economics**
Input vs output pricing and why output costs multiples more. Tokens as the unit of both cost and latency. Back-of-envelope: requests/day × tokens/request × $/token. Why an unattributed bill is unfixable.

**2. Prefill vs decode**
The asymmetry that drives nearly every serving decision: prefill is compute-bound and parallel over the prompt; decode is memory-bandwidth-bound and strictly sequential. What follows for cost, for latency, and for what batching can and cannot fix.

**3. The latency vocabulary**
TTFT, TPOT/ITL, tokens/sec, total latency ≈ TTFT + TPOT × output_tokens. What drives each. Why p99 rather than mean, and what causes tail latency specifically in LLM serving.

**4. Perceived vs actual latency**
Streaming changes the felt experience without changing total time. Where streaming helps, where it's a lie, and what the honest targets are for a chat product versus an agent loop.

**5. Per-request P&L**
Costing a single request end to end — model calls, tool calls, retrieval, retries. Attribution by feature, tenant, and user. Establishing the number *before* optimising anything.

## B · The five levers

**6. Prompt / prefix caching**
How it works: the processed representation of a stable prefix is stored, so subsequent requests skip reprocessing. Cache-friendly prompt ordering — fixed instructions first, volatile content last. TTL, minimum cacheable length, and cache-hit-rate as the metric that decides whether it's working.

**7. Semantic caching**
Application-level: return a stored response for a semantically *similar* query without touching the model. How it differs from prefix caching. Its failure modes — near-miss collisions, staleness, and personalised answers served to the wrong person.

**8. Model routing and tiering**
Cheap default with escalation to a frontier model. Routing by classifier, heuristic, task type, or confidence. Measuring the quality delta per tier so the saving is defensible. The usual single biggest cost lever.

**9. Prompt compression and context management**
Cutting input tokens: trimming history, summarising, dropping low-value retrieved chunks, compacting tool outputs. Where compression costs more in quality than it saves in tokens.

**10. Output length control**
Often the cheapest win available, since output tokens cost most. Max tokens, instruction-level brevity, structured output as a length constraint, and stop sequences.

**11. Batch APIs and async patterns**
When latency doesn't matter, pay less. Designing a pipeline around a batch endpoint. Queue-backed async processing for work that isn't user-facing.

## C · Serving-side levers

**12. Serving internals worth the vocabulary**
Continuous batching, PagedAttention, KV cache and its memory formula, quantization, speculative decoding. **Know these as vocabulary, not as an implementation project** — for an API-consuming role you need to speak them, not build them.

**13. Self-host vs API — the decision**
Walking the tradeoff properly: data sensitivity, scale economics and the break-even volume, latency control, ops burden, and the fine-tune serving question. When the answer flips.

## D · Governance

**14. Budgets, quotas, and rate limits**
Per-user, per-tenant, per-feature caps. Handling provider 429s properly. Why an agent needs a per-task token budget and what happens without one — a single runaway loop rewriting your monthly bill.

**15. Cost observability and anomaly detection**
Dashboards that attribute rather than aggregate. Alerting on cost per request rather than total spend, so a 5× regression is visible at 3pm and not in next month's invoice.

**16. Running a cost-engineering programme**
Sequencing the levers by return per unit effort. Which are quality-neutral (caching, batching) and which trade quality (routing, compression, smaller models) — and why you exhaust the neutral ones first. Capacity planning: from a peak-QPS target to a fleet estimate.

---

## Notes to write

```
05-Cost-And-Latency/
├── 00-Syllabus.md      ← this file
├── 00-Resources.md
├── 01-Token-Economics.md
│   … through …
└── 16-Running-A-Cost-Programme.md
```

## Deferred

| Topic | Goes to |
|---|---|
| Cost attribution *plumbing* — spans, token capture | Block 2 |
| Denial-of-wallet as a security control | Block 4 |
| Compounding-error and step-count economics of agents | Block 6 |
| Retrieval-side cost — embedding, index, rerank | Blocks 7-8 |

## Xarvis mapping

*Filled after learning.* **applicable** / **theory-only** / **parked**.

Going in — this block has real money attached and one obvious win:

- **Applicable and high-value:** prefix caching (6). Xarvis rebuilds a large system prompt every turn — persona + shared system content + time context — and caches none of it. That is textbook. Also output length control (10), token budgets (14), TTFT/TPOT measurement (3), per-request P&L (5).
- **Costed proposal, not shipped:** routing (8) — Xarvis is single-model Gemini Flash, so this becomes "here's the frontier I measured and what I'd have chosen."
- **Theory-only:** serving internals (12), self-host economics (13) — it's an API consumer.
- **Parked:** semantic caching (7) makes far more sense over the retrieval product.

## Sources to verify against

- [Prompt caching in 2026 — engineering guide](https://www.digitalapplied.com/blog/prompt-caching-2026-cut-llm-costs-engineering-guide)
- [LLM cost optimization 2026 — routing, caching, batching](https://www.maviklabs.com/blog/llm-cost-optimization-2026)
- [Cutting token costs — routing, caching, compression, model choice](https://wavect.io/blog/reduce-llm-token-costs-2026/)
- [Token optimization guide](https://neuraltrust.ai/blog/ai-token-optimization-guide)
- Provider docs are the only authority on caching mechanics and batch discounts — check Anthropic, OpenAI, and Gemini directly rather than trusting a blog
- Corpus: `08-inference-and-production/` Q1-Q3, Q6, Q9, Q14-Q15, Q21, Q24-Q26, Q35-Q36, Q42
