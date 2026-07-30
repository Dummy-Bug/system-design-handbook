#ai-engineering #evals #llm-judge #error-analysis #block-3 #syllabus

# Block 3 · LLM-as-Judge & Error Analysis — Syllabus

18 concepts. **Generic** — the field, not Xarvis. Map afterwards.

> Learn the full surface first, *then* decide what Xarvis can demonstrate. A syllabus derived from the codebase drops whatever the codebase doesn't exercise.

**Why this block matters most.** Every hiring source consulted names the same thing as the sharpest senior/junior discriminator, and it isn't building — it's measuring. *"Is there an actual eval framework here, or is it vibes-based?"* Error analysis is the highest-ROI activity in the entire field.

**Currency check (2026-07-30):** the bias taxonomy has grown to **five named biases** — position, verbosity, self-preference, **format**, and **calibration drift** — each with its own measurement and mitigation. 2026 guidance recommends a **minimum calibration set of ~500 cases** before trusting aggregate judge metrics, and **Cohen's kappa** as the inter-rater standard with **κ < 0.6 meaning the rubric itself is broken**, not the judge.

---

## A · Error analysis — do this before writing a single criterion

**1. Why criteria-first is backwards**
The dominant mistake: crafting elaborate eval criteria before looking at data. The failure modes you *imagine* are not the ones that occur. Consequence: your eval measures the wrong thing precisely and confidently.

**2. Open coding**
Read real traces one at a time and describe what went wrong in a plain sentence, with no taxonomy in hand. Why the absence of a schema is the point.

**3. Axial coding — building the taxonomy from the data**
Grouping open codes into buckets. Naming buckets so they're mutually exclusive enough to count. Ranking buckets by frequency × severity. Where to stop splitting.

**4. The flywheel**
Traces → open code → buckets → evals for the biggest buckets → ship a fix → new traces. Why this loop, not a bigger dataset, is what improves the product.

**5. Sample size and saturation for error analysis**
How many traces before the taxonomy stops changing. What to do when you have no traces at all — bootstrapping from a synthetic set and treating *its* failures as the first corpus.

## B · The judge

**6. What LLM-as-judge is, and when it's the right tool**
Model scores another model's output against a rubric, given input + output and optionally a reference or context. Where it beats code-graded assertions and where it's an expensive way to be wrong.

**7. Pointwise vs pairwise**
Absolute scoring vs "which of these two is better." Why pairwise is more reliable, and what you give up (no absolute threshold, harder to track over time).

**8. The five biases**
**Position** (order of candidates changes the verdict) · **verbosity** (longer reads as better) · **self-preference** (a model favours its own family's output) · **format** (markdown, structure, and formatting artefacts sway the score) · **calibration drift** (the score distribution moves over time even with a fixed rubric). Each with its own detection method and mitigation.

**9. Bias mitigations that actually work**
Position swap and average. Length normalisation or explicit length-blind instructions. Cross-family judging. Rubric anchoring with examples. Which mitigations are cheap and which cost a second inference pass.

**10. Calibration against human labels**
The central operational practice: measuring the gap between judge scores and human expert ratings. Building the calibration set, its target size, and the honest interpretation of the resulting agreement number.

**11. Inter-rater reliability and Cohen's kappa**
Why at least two independent human raters per case. Computing kappa. The threshold that matters: **if kappa between humans is below ~0.6, the rubric is the problem** — refine the rubric before touching the judge. What to do when annotators legitimately disagree.

**12. Rubric design**
When rubrics help (open-ended tasks) and when they add noise. Explicit, criterion-separated, calibrated. Binary pass/fail vs graded scales, and why binary is usually more reliable. Where chain-of-thought belongs in a judge prompt.

**13. Judge drift and versioning**
A minor judge-model version bump can shift the mean by several points and narrow the distribution — the metric silently stops meaning what it meant. Pinning the judge, versioning the rubric, and keeping scores comparable across a forced judge migration.

**14. When is a judge production-ready?**
The checklist: locked rubric · measured kappa against human labels · position and verbosity controls in place · a cross-family check against a frontier judge. Anything less is a number you shouldn't quote.

## C · Trusting the number

**15. Statistical significance**
Why 78% vs 74% on 100 examples may be noise. Sizing an eval set to detect a real N-point delta. Paired comparison to cut variance. When to stop adding examples.

**16. Segment analysis**
Aggregate up 3 points, one customer segment down 8. Why the mean hides the regression that gets you a support ticket, and how to slice before shipping.

**17. Goodhart's law in evaluation**
What happens when the eval becomes the target. Overfitting to your own set. Holdout discipline. Concrete examples of teams optimising a metric while the product got worse.

## D · Closing the loop

**18. From findings to durable assets**
Turning an error-analysis pass into: new eval cases, a regression suite, a rubric change, a prompt fix, or a code fix — and knowing which of those five the finding actually calls for. Building a human review queue: what gets reviewed, by whom, how much.

---

## Notes to write

```
03-LLM-Judge-And-Error-Analysis/
├── 00-Syllabus.md      ← this file
├── 00-Resources.md
├── 01-Why-Criteria-First-Is-Backwards.md
│   … through …
└── 18-From-Findings-To-Durable-Assets.md
```

## Deferred

| Topic | Goes to |
|---|---|
| Golden set construction, trajectory evals, pass@k/pass^k | Block 1 |
| Tracing, spans, cost/latency attribution | Block 2 |
| RAG triad, RAGAS, retrieval metrics | Blocks 7-8 |
| Red teaming as a programme | Block 4 |

## Xarvis mapping

*Filled after learning.* **applicable** / **theory-only** / **parked**.

Going in: concepts 1-5 depend entirely on whether Xarvis retains production traces. If it does, this block becomes an afternoon with real data instead of a thought experiment — settle that question early. Concept 11 (two human raters) is awkward as a solo engineer; the honest version is rating twice, separated by days, and saying so.

## Sources to verify against

- [LLM-as-judge best practices 2026 — calibration, bias, cost](https://futureagi.com/blog/llm-as-judge-best-practices-2026)
- [LLM-judge bias mitigation 2026 — detect, measure, fix](https://futureagi.com/blog/evaluating-llm-judge-bias-mitigation-2026/)
- [Judge patterns for agent evaluation — calibration, bias, trajectory](https://zylos.ai/research/2026-05-26-llm-as-judge-agent-evaluation-patterns/)
- [Rubric-based evals — methodologies and empirical validation](https://medium.com/@adnanmasood/rubric-based-evals-llm-as-a-judge-methodologies-and-empirical-validation-in-domain-context-71936b989e80)
- Hamel Husain — [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/) · [error analysis method](https://www.lennysnewsletter.com/p/evals-error-analysis-and-better-prompts)
- Corpus: `07-evaluation-and-observability/` Q5, Q14-Q17, Q26-Q30, Q34-Q36, Q39, Q42, Q45, Q50
