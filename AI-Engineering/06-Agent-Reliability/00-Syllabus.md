#ai-engineering #agents #reliability #context-engineering #block-6 #syllabus

# Block 6 · Agent Reliability — Syllabus

17 concepts. **Generic** — the field, not Xarvis. Map afterwards.

> Learn the full surface first, **then** decide what Xarvis can demonstrate. Xarvis is a short-horizon agent (2-4 steps), so the long-horizon half of this block will land as theory — and that half is exactly what 2026 interviews probe.

**Currency check (2026-07-30) — this is the fastest-moving block.** The consensus finding is blunt: **token accumulation is the primary failure mode of long-horizon agents**, and it hits frontier models as hard as small ones. A model scoring **98.1 on a clean single-prompt eval drops to 64.1** when the same information is distributed across a multi-turn agent run. Two more numbers worth memorising: agent success rates begin declining after roughly **35 minutes of human-time-equivalent work**, and **doubling task duration quadruples the failure rate** rather than doubling it. Checkpointing every step cuts wasted processing by **60%+** on multi-step workflows.

The organising framework that emerged in 2026 is **write / select / compress / isolate** — four context levers against four named failure modes.

---

## A · Why agents fail

**1. The reliability arithmetic**
Per-step success compounds multiplicatively: `p^n`. 0.95 per step over 20 steps ≈ 0.36 end to end. Why **the model got better** doesn't rescue a long chain, and why this single equation dictates architecture.

**2. Workflow vs agent — and when not to build one**
An agent directs its own loop; a workflow is a fixed sequence with a model as one step. The default should be the workflow. Agent maximalism as the most common design failure.

**3. The failure taxonomy**
Wrong tool selected · right tool with wrong params · tool-call hallucination · infinite loops · premature termination · giving up too early · goal drift over long horizons · cascading failure across steps. Vocabulary for everything downstream.

**4. Context rot and the four failure modes**
**Context confusion** from tool overload · **context distraction** from accumulated history · **context clash** from merged contradictory information · **context poisoning** from hallucinated state persisting into later steps. Why these are distinct problems with distinct fixes.

## B · Context engineering — the four levers

**5. Write** — externalising state
Scratchpads, files, and structured external storage instead of carrying everything in the window. Why writing hallucinated state to durable storage is the poisoning risk.

**6. Select** — just-in-time retrieval of context
Loading tools and information only when needed, instead of front-loading 130 tool schemas. The counter to context confusion.

**7. Compress** — summarisation and compaction
Compacting history when the window fills. And the sharp new caveat: **compaction can fabricate.** Recent work documents agents reporting confirmed results from processes that were actually killed, because the compaction step invented a plausible summary. Compaction needs validation, not trust.

**8. Isolate** — subagents and context boundaries
Giving a subagent a clean window and returning only its result. What crosses the boundary in each direction. The counter to context clash, and its cost in coordination overhead.

## C · Durability and recovery

**9. Checkpointing and durable execution**
Persisting state before each step so a crash resumes rather than restarts. The 2026 production pattern: a durable-state layer (Temporal, LangGraph checkpointers, event-sourced state) plus reliable compute. Why this is the highest-return reliability investment.

**10. Idempotency**
Making a retried step safe. Idempotency keys. The canonical failure: an agent charging a card twice while the trace shows one tool call.

**11. Retries, timeouts, backoff, and circuit breakers**
Per-call and per-task. Which errors are retryable and which are terminal. Exponential backoff with jitter and why jitter matters. Retry budgets, so recovery doesn't become the outage.

**12. Fallbacks and graceful degradation**
Model fallback, provider fallback, cheaper-model fallback, read-only fallback, cached response, and honest failure. Designing the degradation ladder before it's needed.

**13. Loop detection and stop conditions**
Max iterations, repeated-state detection, no-progress detection, budget exhaustion. Diagnosing both failure directions — stuck in a loop, and quitting too early.

## D · Long-horizon and multi-agent

**14. Long-horizon task architecture**
Goal decomposition, sub-goal tracking, partial credit, cross-session continuity, resuming a multi-day task. Why success decays with duration and what arrests the decay.

**15. Memory that survives the session**
Working vs persistent memory. Summarisation vs vector retrieval for recall, and how to choose. Memory decay and staleness. Evaluating whether the memory layer actually helps.

**16. Multi-agent reliability**
Orchestrator-worker and supervisor patterns. Handoffs vs orchestration. Where multi-agent helps (parallel, read-heavy work) and where it actively hurts (write-heavy shared state). Attributing a failure to the right agent after the fact.

## E · Verification

**17. Reproducibility and post-hoc debugging**
**A customer says the agent did something wrong three days ago.** Can you reproduce it? Deterministic replay harnesses, trace-based reconstruction, and what must be captured at runtime for the answer to be yes. Defining SLOs for an agent when every span returns 200 and latency looks fine.

---

## Notes to write

```
06-Agent-Reliability/
├── 00-Syllabus.md      ← this file
├── 00-Resources.md
├── 01-The-Reliability-Arithmetic.md
│   … through …
└── 17-Reproducibility-And-Replay.md
```

## Deferred

| Topic | Goes to |
|---|---|
| Trajectory evals, pass@k vs pass^k as reliability metrics | Block 1 |
| Tracing plumbing, span design | Block 2 |
| Cascading failure as a **security** concern (`ASI08`) | Block 4 |
| Token budgets as a **cost** lever | Block 5 |

## Xarvis mapping

**Filled after learning.** **applicable** / **theory-only** / **parked**.

Going in — this is the block where Xarvis is strongest on paper and least measured in practice:

- **Already built, never measured:** checkpointing (9), retries/timeouts/backoff (11), model fallback (12 — the 10s→15s admin path). The work is quantifying what exists, not building it.
- **Applicable:** reliability arithmetic on real trajectories (1), failure taxonomy against real traces (3), loop detection (13), reproducibility (17).
- **The dead-code decision:** the disconnected `guard/` + `planner/` fast-path belongs to concept 2 — a workflow that would replace an agent call. Wire it behind a flag, measure, decide honestly. Good story either way.
- **Theory-only:** long-horizon architecture (14), multi-agent reliability (16), the compaction-fabrication problem (7). Xarvis runs 2-4 steps and its three agents never coordinate. Learn these; don't claim them.

## Sources to verify against

- [Context engineering — agent reliability playbook 2026](https://www.digitalapplied.com/blog/context-engineering-agent-reliability-playbook-2026) — the write/select/compress/isolate framework
- [Durable agent execution in production 2026 — Temporal, LangGraph, event-sourced state](https://agentmarketcap.ai/blog/2026/04/10/durable-agent-execution-production-temporal-modal-event-sourced)
- [Long-horizon agent goal persistence and multi-day tasks](https://zylos.ai/research/2026-05-15-long-horizon-agent-goal-persistence/)
- [Compaction as Epistemic Failure](https://arxiv.org/html/2607.13071) — agents fabricating confirmed results from killed processes
- [Beyond the Leaderboard: tool-use, planning, and reasoning failures in LLM agents](https://arxiv.org/pdf/2607.05775)
- Anthropic — **Building Effective Agents** (the workflows-before-agents argument)
- Corpus: `06-agents-and-tool-use/` Q1-Q3, Q14-Q22, Q29, Q38, Q43-Q50, Q53 · `08-inference-and-production/` Q39-Q40
