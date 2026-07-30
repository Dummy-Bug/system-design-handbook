#ai-engineering #evals #agents #block-1 #syllabus

# Block 1 · Agent Evals — Syllabus

22 concepts. **This list is generic** — it describes the field, not Xarvis.

> **Why generic first.** If the syllabus is derived from the codebase, every concept the codebase happens not to exercise gets silently dropped — and those are exactly the ones an interviewer asks about. So: learn the full surface, *then* map. Concepts that Xarvis can't demonstrate become theory-only, deliberately, rather than by accident.

**Order of work:** learn all 22 → map each to Xarvis (applicable / theory-only / parked for the retrieval product) → implement the applicable ones as items A1-A3.

**Ends with three numbers Xarvis has never had:** tool-selection accuracy · param-extraction accuracy · access-control enforcement rate.

---

## A · Foundations

**1. Why evals, not vibes**
What problem an eval solves. Where spot-checking is *correctly* sufficient and where it breaks. What an eval actually is. Guardrail metrics vs quality metrics. The maturity path: vibes → spot checks → golden set → CI gate → online monitoring.

**2. Model evals vs application evals**
"Is this model good?" and "is my system good?" are different questions with different owners. Why MMLU/GSM8K scores don't tell you whether your app works. Benchmark saturation and contamination. What you cannot outsource.

**3. Eval-driven development**
Where evals sit in the development loop. The TDD analogy — and precisely where it breaks down, since you cannot make a probabilistic system green.

## B · The taxonomy — how you grade

**4. Grading methods**
Code-graded assertions, model-graded (LLM-as-judge), human evaluation. The cost/reliability tradeoff between them, and the rule for which to reach for. *Judge depth is Block 3 — here it's only placed in the taxonomy.*

**5. Reference-based vs reference-free**
When a gold answer exists and when it can't. Why exact-match, BLEU and ROUGE fail on generated text.

**6. Offline vs online**
Pre-ship measurement vs production signal. **Offline** — its three jobs: release gating via CI, version comparison on a level field, regression testing. **What breaks after deploy** that offline cannot reach: unanticipated inputs, emergent/systemic failures visible only at scale, and drift silently obsoleting the golden dataset. **Online** — evaluating live traffic with **no answer key**: *correctness* vs *normality*, baseline-and-distribution comparison, implicit feedback (thumbs, retries, escalations, abandonment) as a quality proxy, inherently reference-free metrics. **The online pipeline**: logging (and its four engineering properties) → captured vs computed signals → stratified sampling → evaluator → dashboard → alerting. And the loop that joins them: online failures become offline test cases.

*Broadened 2026-07-30 — originally one line about pre-ship vs production. The online pipeline is substantial enough to carry the concept. Logging, dashboarding, and alerting get their depth in **Block 2 (Observability)**; here they appear only as the eval pipeline's plumbing.*

## C · What you measure in an agent

**7. The failure taxonomy — levels and risk categories**
**Where** a system fails: three levels — **component**, **workflow**, **entire application** — and why green at one level implies nothing about the level above. **What kind** of failure it is: three risk categories — **application quality**, **safety**, **operational**. Then the agent-specific failure modes: tool-call hallucination, wrong tool selected, right tool with wrong params, infinite loops, premature termination, giving up too early, context pollution, goal drift.

*Broadened 2026-07-30 — originally scoped as "the agent failure taxonomy", which was too narrow. This is the concept that determines **how many** evals a system needs and **where** each one goes, so it has to cover non-agent systems too.*

**8. Trajectory vs outcome**
Right *path* vs right *answer*. Why each can pass while the other fails, and why a right answer via a wrong path is a latent bug rather than a pass. Tool-selection and param-extraction accuracy. Exact-match vs subset vs order-insensitive trajectory matching.

**9. Evaluating the tool layer itself**
When the tool *description* is the bug rather than the model. A/B-ing tool schemas, names, and error messages. Why tool design is an eval target, not a constant.

**10. Should-refuse and negative cases**
The agent correctly declining is a *passing case*, not the absence of one. Refusal, access denial, out-of-scope, and unanswerable questions as first-class eval categories.

**11. Multi-turn and conversational evaluation**
Evaluating a conversation rather than a turn. Users who change their mind mid-thread. Whether the agent asks a clarifying question when it should. Simulated users as an eval technique.

**12. Long-horizon and multi-agent evaluation**
Partial credit across 20-50 steps. Checkpoint-based scoring. Attributing a failure to the right agent when work crosses a handoff.

## D · The dataset

**13. Error analysis first**
The counterintuitive ordering: look at real traces *before* writing eval criteria. Open coding → axial coding → buckets → evals for the biggest buckets. Why the failure modes you imagine are the wrong ones. What to do when you have no traces yet.

**14. Building the golden set**
How many cases, and why 20-50 genuinely hard real ones beat 500 easy synthetic ones. Where cases come from. What a single case record contains. Coverage design across capabilities.

**15. Synthetic eval data**
Generating cases with an LLM, and the central failure mode: the generator's blind spots become your blind spots.

**16. Splits, versioning, and overfitting**
Dev set vs held-out set. Why an eval dataset gets versioned and what belongs in the version. How an eval set rots, and how you notice.

## E · Making the number trustworthy

**17. Nondeterminism and determinism controls**
Why temperature 0 does not give you determinism. Seeds, batching effects, provider-side variance. Why the same suite returns a different number twice.

**18. pass@k and pass^k**
Why a single run is not a measurement. pass@k as "at least one of k succeeds" — the biased naive estimator and the unbiased form, computed stably. pass^k as "all k succeed." Why pass@k flatters agents and pass^k is what production cares about.

**19. Regression vs progression**
Catching what you broke vs verifying what you fixed. Why these want different sets and different thresholds.

**20. The cost of evaluating**
Evals cost real money and wall-clock time. Tiered suites — a fast smoke set per PR, the full suite nightly. Sampling strategies.

## F · The landscape

**21. Agent benchmarks**
τ-bench, SWE-bench, WebArena, GAIA, AgentBench — what each actually measures, and why you still cannot use them to decide anything about your own system.

## G · Implementation

**22. Building a harness**
The generic shape, framework-agnostic: case → run → extract trajectory → assert → report. Then the concrete binding to whatever framework is in front of you.

---

## Notes to write

One file per concept, **numbered to match the concept number above**. Own words, plain English, problem before solution.

> **The syllabus governs the numbering — never the source material.** A lecture, video, or article that covers concept 7 becomes `07-*.md`, even if it was the 4th video in its playlist. One video may also feed several notes, or several videos one note. Gaps in the numbering are concepts not yet reached, not missing files.

```
01-Agent-Evals/
├── 00-Syllabus.md      ← this file
├── 00-Resources.md     ← where to learn each of these from
├── 01-Why-Evals-Not-Vibes.md
├── 02-Model-Evals-Vs-Application-Evals.md
│   … through …
└── 22-Building-A-Harness.md
```

---

## Deferred, deliberately

| Topic | Goes to |
|---|---|
| LLM-as-judge depth, judge biases, calibration, rubric design | Block 3 |
| Inter-annotator agreement, handling human disagreement | Block 3 |
| Statistical significance, sizing an eval set for a real delta | Block 3 |
| Tracing, spans, cost/latency attribution | Block 2 |
| RAG-specific evals — the triad, RAGAS, recall@k / MRR / nDCG | Blocks 7-8 |

Block 1 is first precisely because it needs **no LLM judge and no new infrastructure.**

---

## Xarvis mapping

*To be filled after the concepts are learned — not before.* Each of the 22 lands in one of:

- **Applicable** → implement it in Xarvis, produce a number
- **Theory-only** → Xarvis can't exercise it; learn it, be able to discuss it, don't fake having built it
- **Parked** → belongs to the retrieval product (blocks 7-9)

Rough expectation going in: several of 11, 12, 15, 21 will land in theory-only, and that is the correct outcome — not a gap.
