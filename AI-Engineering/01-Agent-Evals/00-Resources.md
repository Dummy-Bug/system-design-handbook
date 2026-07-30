#ai-engineering #evals #agents #block-1

# Block 1 · Agent Evals — Resources

**Goal:** build the first eval harness on Xarvis and produce three numbers it has never had — tool-selection accuracy, param-extraction accuracy, access-control enforcement rate.

**Builds:** `xarvis-additions.md` items A1, A2, A3. **Needs no LLM judge and no new infrastructure** — you read the message list off the graph and compare strings.

---

## Read this first — it changes the order

The instinct is: write 50 golden questions → run them → see what fails. The people who do this professionally say that's backwards.

> *"Many teams make the mistake of crafting elaborate eval criteria without first looking at the data."* — Hamel Husain

The actual loop is **error analysis first**: look at real traces → open-code what went wrong in plain sentences → group those into buckets (axial coding) → *then* build evals for the biggest buckets. The dataset grows out of observed failure, not out of imagination.

**So Block 1 has two entry points depending on one fact:**

- **If Xarvis has production conversation logs** → start with error analysis on ~50 real traces. The golden set is then *derived*, and it targets failures that actually happen.
- **If it doesn't** → bootstrap a synthetic golden set across the tool surface, run it, and treat *its* failures as your first error-analysis corpus. Same loop, seeded differently.

Either way the flywheel is the same. Knowing why the first version is better is itself an interview answer.

---

## Primary sources — highest depth per minute

**1. Corpus crash course** — `/tmp/ai-eng-corpus/AI-Engineer-Interview-Questions/07-evaluation-and-observability/README.md`
Fifteen sections and it is almost exactly this block's syllabus: *Evals are the moat · The eval taxonomy · Building an eval set · LLM-as-judge properly · pass@k · Application-specific evals · Regression testing and CI · Guardrail vs quality metrics · Online evaluation · Error analysis: the highest-ROI activity · The maturity path.* Read the whole thing before anything else.

**2. Corpus worked answers** — same folder, `questions.md`. Answer each out loud *before* opening the collapsible answer.

| Q | Topic |
|---|---|
| Q1 | Why "evals are the moat" — evals as the core engineering artifact |
| Q2 | The taxonomy of evaluation methods, and when to use each |
| Q3 | Code-graded assertions, and where they break down |
| Q4 | **Building evals from scratch — how many examples, and where they come from** |
| Q6 | **pass@k — why the naive computation is wrong and what the fix is** |
| Q7 | Guardrail metrics vs quality metrics |
| Q11 | *"Your eval reports 82% pass on 100 examples. What does that number not tell you?"* |
| Q12 | Why you version an eval dataset, and what belongs in the version |

**3. Agent-specific** — `06-agents-and-tool-use/questions.md`. These three are the actual core of this block:

- **Q27 — trajectory evals vs final-outcome evals** (line 566)
- **Q28 — pass@k vs pass^k, and why the distinction matters for production agents** (line 582)
- Q33 — testing an agent in CI, on every PR, in under five minutes

**4. Hamel Husain** — the canonical practitioner source on error analysis.
- [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/) — the foundational post
- [Evals, error analysis, and better prompts](https://www.lennysnewsletter.com/p/evals-error-analysis-and-better-prompts) — the systematic method, interview format
- [How to Build an AI Evals Dataset from Scratch](https://www.decodingai.com/p/build-an-ai-evals-dataset-with-error-analysis) — the error-analysis-first flywheel, concretely
- His Maven course *AI Evals for Engineers & PMs* exists and is well regarded. **Don't buy it now** — your own rule: no new course purchase until the active one has shipped an artifact.

**5. [A pragmatic guide to LLM evals for devs](https://newsletter.pragmaticengineer.com/p/evals)** — Pragmatic Engineer. Engineer-framed rather than PM-framed; good counterweight.

---

## Directly applicable to Xarvis

**[langchain-ai/agentevals](https://github.com/langchain-ai/agentevals)** — readymade trajectory evaluators. `create_trajectory_match_evaluator` takes trajectories **as a list of LangChain `BaseMessage` objects**, which is exactly what Xarvis's graph already produces. This is the shortest path from zero to a trajectory number. Read the source, not just the README — it's small, and understanding it is more useful than importing it.

**[Evaluate a complex agent](https://docs.langchain.com/langsmith/evaluate-complex-agent)** — LangChain docs, the official walkthrough.

**[LangSmith cookbook — evaluating agents](https://github.com/langchain-ai/langsmith-cookbook/blob/main/testing-examples/agent_steps/evaluating_agents.ipynb)** — scoring an agent on its decision-making process, i.e. the sequence of tools selected. Notebook, runnable.

> Tooling note: LangSmith is the path of least resistance with LangGraph, but it's hosted. Langfuse is self-hostable if sending production HR traces to a third party is a problem — which for an HRMS it probably is. Decide this before wiring anything.

---

## Runnable

**`/tmp/ai-eng-corpus/AI-Engineer-Interview-Questions/12-coding-challenges/12_eval_metrics.py`** — numpy + stdlib only, implement then run. Three pieces:

1. `pass_at_k(n, c, k)` — the unbiased estimator from Chen et al. 2021 (the Codex paper), in the numerically stable product form `1 - Π(1 - k/i)` rather than materialising binomials. The notes explain *why* the naive estimator is biased for `k < n`, and that `C(2000,1000) ≈ 2e600` overflows float64.
2. SQuAD-style `normalize_answer` / `exact_match` / `token_f1`.
3. A minimal pairwise LLM-judge harness **with position swap** — which is the standard mitigation for judge position bias, so this doubles as Block 3 prep.

Do this one by hand. It's the difference between saying "pass@k" and understanding it.

---

## Video

[CampusX — LLM Evaluation](https://www.youtube.com/playlist?list=PLEneLIDJFpcA), videos 2–4 only for this block:

- #2 `cNF_MO82Qew` — Introduction: model evals vs application evals
- #3 `Pv4mkG2K_s8` — How to evaluate LLM applications: the complete workflow
- #4 `DcZ-XCk-O_M` — Why your AI application needs multiple eval pipelines

Videos 5–6 belong to Block 3. Videos 7–10 are model evals, benchmarks and leaderboards — lowest priority for an applied backend role; skim later or skip.

---

## Notes to write

Same pattern as `RAG/` — own words, plain English, problem before solution.

```
Agent-Evals/
├── 00-Resources.md                          ← this file
├── 01-Why-Evals-Not-Vibes.md
├── 02-Model-Evals-Vs-Application-Evals.md
├── 03-The-Eval-Taxonomy.md
├── 04-Trajectory-Vs-Outcome-Evals.md        ← the core of this block
├── 05-Error-Analysis-First.md               ← the ordering insight above
├── 06-Building-The-Golden-Set.md            ← how many, sourced from where
├── 07-passk-And-passhatk.md                 ← incl. the biased-estimator trap
└── 08-Reading-A-LangGraph-Trace.md          ← implementation: messages → assertions
```

---

## Definition of done

A note isn't finished when it's written — it's finished when the matching Xarvis item produces its number. That's the rule that keeps this from becoming re-reading with extra steps.

- [ ] `01`–`08` written
- [ ] `12_eval_metrics.py` implemented from the docstring alone and passing
- [ ] **A1** — golden set exists (~50 cases: one per registered tool, multi-tool chains, access-control denials, ambiguous-name HITL cases, out-of-scope questions, PARTIAL-result cases)
- [ ] **A2** — trajectory eval running → *tool-selection accuracy %*, *param-extraction accuracy %*
- [ ] **A3** — access-control eval running → *enforcement rate %*
- [ ] Three numbers recorded, with the date and the commit they were measured at

> Expect A3 to crash on the first run. `orchestration/employee/nodes/access_denied.py:12` calls `json.loads(last.content)` with no try/except, so any non-JSON tool content takes the node down. Finding that *is* a result — write it down as your first error-analysis entry.
