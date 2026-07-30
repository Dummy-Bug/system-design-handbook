# CLAUDE.md — AI-Engineering

Interview preparation for **backend + agentic-AI roles**. Notes, question banks, and Socratic drilling live here.

> Contains employer internals (Repute / Xarvis) and resume-claim audits. Treat as private; consider gitignoring before any public push.

---

## The target

| | |
|---|---|
| **Band** | ~30 LPA (from 10 LPA). Decided 2026-07-29 — *not* 40-50; that's a different, elite-DSA grind. |
| **Timeline** | Interview-ready by **Jan 2027**. ~5 months from now. |
| **Experience** | 2.6 YOE full-time (Repute Network, Jul 2023 intern → Jan 2024 SWE). B.Tech 2020, UoH AI/ML diploma 2021-22. |
| **Lane** | **Backend engineer who owns the AI layer** — not "AI Engineer" competing with ML backgrounds. Java/Spring + Python/FastAPI + LangGraph. Less crowded, well paid, matches the actual resume. |
| **Screening risk** | 2020 grad, first SWE role Jul 2023. Needs a deliberate narrative, not a knowledge fix. |

Live opportunities as of 2026-07-29: **none** (Salesforce and WealthQ both closed). Prep is not blocking any active loop.

---

## Ground truth: Xarvis

`~/Documents/repute/jarvis/xarvis` — 26K LOC Python. Read `CLAUDE.md` there (375 lines) plus the three per-agent ones before answering anything about it. **Never describe Xarvis from memory — check the code.**

### What it actually is

Three **separate** LangGraph agents behind one FastAPI service, routed by role in `server/routes/chat.py`. Gemini 2.5 Flash throughout. Shared checkpointer, isolated by `thread_id`.

- **Employee** — `START → chatbot → tools_condition → tools → route_after_tool_execution → chatbot | access_denied → END`. Canonical ReAct tool-calling loop. 15s timeout, no fallback.
- **Admin** — `START → chatbot → tools_condition → tools → chatbot`. Simpler. 10s primary → 15s hardcoded-flash fallback → hard-fail string. HITL `interrupt()` fires from `get_employee_id_using_name`.
- **Onboarding** — a genuine multi-node pipeline (intent parser → workflow gen/confirm/modify → app-connection & app-enablement subgraphs → execution plan → runner → summary). Not a ReAct agent. Most complex piece in the repo; 564-line CLAUDE.md.

### Claims that need care

Audited against the code on 2026-07-29. Per the resume surface-area rule, each of these either gets fixed on the resume or gets a rehearsed honest answer.

| Resume / skills claim | Code reality |
|---|---|
| "TTL-based **Redis** cache" | Cache is **DynamoDB** (`DynamoEmployeeDomainCache`, per-domain TTLs: Personal 600s, Work 600s, EmployeeList 1000s) or in-memory locally. Redis appears only as `langgraph-checkpoint-redis` in requirements + a `NotImplementedError` stub + "maybe later" architecture docs. |
| "**multi-agent** AI platform" | Three agents that never talk to each other; role-based HTTP routing picks one. Multiple agents ≠ multi-agent system. This is the "honest A2A framing" already flagged in the roadmap. |
| **LangSmith** (skills) | One mention in the entire repo. No tracing instrumentation, no Langfuse. |
| **RAG** (skills) | Zero RAG in Xarvis — it is pure tool-calling over HRMS REST. RAG knowledge is notes + CampusX + AlgoCamp, not shipped. |
| **MCP** (skills) | Zero MCP in Xarvis. MCP was a separate fastmcp test harness built to isolate a failing LangChain agent — a real, defensible story, but it does not power Xarvis. |
| Workflow prediction | `graph_pipeline/` — ingestion, Neo4j, identity resolution, embeddings. **Data machinery only.** No trained model. Never claim next-activity prediction works. |

### Known gaps (these are the work, not the shame)

- **No evals.** 11 test files, "sparse coverage; no integration tests." No golden set, no LLM-judge, no RAGAS, no error analysis.
- **No observability.** No tracing, no cost attribution, no latency breakdown by stage.
- **No numbers anywhere** — no cost/conversation, no p95, no tool-call success rate. The resume's AI bullets are all mechanism nouns while the older verification-platform bullets have 25K→300K, 27%→80%, 60%→85%.
- **Guard + planner are built and disconnected.** `orchestration/employee/guard/` and `planner/` implement a deterministic fast-path; the graph bypasses both. Dead code — but a strong story *if* framed as "built, measured, didn't ship, here's why."
- **Rate-limit key hardcoded** (`middleware/rate_limit.py:18` returns `"EMPLOYEE:1153"`) → the 10 req/min cap is shared globally across every user.

---

## Corpora available

**Mirrored** at `/tmp/ai-eng-corpus/` (re-clone if `/tmp` cleared):

| Repo | Content |
|---|---|
| `ombharatiya/AI-Engineer-Interview-Questions` | The serious one. 952 questions with worked answers (532 topic / 291 across 25 companies / 129 across 10 role guides), 8 system-design case studies, 13 numpy-only coding challenges, `AI-ENGINEER-75.md` checklist, `CHEATSHEET.md`. ~3.4 MB. |
| `amitshekhariitbhu/ai-engineering-interview-questions` | 511 questions in one README; only 159 have answers, all as outbound outcomeschool.com links. Question bank, not content. |
| `aakriti1318/interview_questions` | 40 scenario Q&As across 5 roles (8 for AI Engineer). Shallow but well-structured. |

**AlgoCamp AI cohort** (enrolled, 6 months): 33 modules. Part 1 = modules 1-26, AI engineering. Part 2 = modules 27-33, deep-learning foundations. Covers observability (22), evals (23), security/OWASP/guardrails (24), streaming-retries-fallbacks (19), prompt caching & cost/latency (21), LLM internals (32), fine-tuning/LoRA (33) — i.e. **the syllabus is already a valid topic taxonomy; we do not need to invent one.** 17 build projects, which is a portfolio trap: breadth without a defensible deep one.

---

## Folder layout

**Topic folders are numbered by the learning order** (see below). A folder is created only when its block starts — gaps in the numbering are blocks not yet reached, not missing files.

```
AI-Engineering/
├── CLAUDE.md                 ← this file
├── interview-prep/           ← meta, unnumbered
│   ├── learning-surface-2026.md    ← WHAT to know: tiered must-know list + product scoring rubric
│   ├── xarvis-additions.md         ← HOW: 24 items (A-F) + THE LEARNING ORDER (9 blocks)
│   └── interview-prep-roadmap.md   ← Tracks A-E (DSA / LLD / HLD / AI / behavioral)
├── 00-Python-Async/          ← prerequisite; 7 notes, event loop → gather/TaskGroup
├── 01-Agent-Evals/           ← Block 1 ← CURRENT
│   ├── 00-Syllabus.md              ← 22 generic concepts + the Xarvis mapping (filled after learning)
│   └── 00-Resources.md             ← where to learn each from
├── 02-Observability/         ← Block 2  · 15 concepts
├── 03-LLM-Judge-And-Error-Analysis/  ← Block 3 · 18 concepts
├── 04-AI-Security/           ← Block 4  · 20 concepts
├── 05-Cost-And-Latency/      ← Block 5  · 16 concepts
├── 06-Agent-Reliability/     ← Block 6  · 17 concepts
└── 07-RAG/                   ← Blocks 7-8 · 24 concepts. 00-Fundamentals … 06-Advanced-Retrievers
                                 already written (~5,300 lines); remaining = rerank, query transforms,
                                 freshness, citations, ACL-aware retrieval, RAG evals

Every block folder has `00-Syllabus.md` (generic concept list + an unfilled Xarvis-mapping section).
Concept notes are numbered to match syllabus item numbers — concept 7 → `07-Name.md`.
Each syllabus carries a **currency check** dated at time of writing; re-verify versioned specs
(OWASP lists, OTel GenAI conventions, MCP spec, provider caching mechanics) before relying on them.
```

`07-RAG/` is numbered late because its *remaining* work sits at block 7, not because it's unstarted — it's the most complete folder here. Notes use Obsidian embeds with absolute vault paths (`![[AI-Engineering/07-RAG/…/Images/…]]`), so **any future folder rename must rewrite those links too.**

**The active plan lives in `xarvis-additions.md` → "The learning order."** Nine blocks, each `learn the thing → add it to Xarvis → keep the number`. Blocks 1-6 (~8.5 wks) take Tier 1 to ~70% on the existing production agent; blocks 7-9 (~6 wks) build the public retrieval product that covers what Xarvis structurally can't. Start at Block 1 / item A1.

Related, outside this folder: `~/Desktop/wiki/Xarvis-Archaeology/` (code-verified resume-defense docs), `~/Desktop/wiki/Interview-Prep/` (DSA pattern transcripts).

---

## How to work here

**Derive before writing.** Never create or edit a file until it's explicitly asked for. Discuss and derive in chat first; auto-writing and auto-advancing are the failure mode.

**Socratic by default.** He answers first; I push back, then perturb the assumption to find the load-bearing part. Retrieval, never re-reading — re-reading solutions produces fluency illusion, which is exactly what plateaued the DSA track at 1530.

**One concept at a time, problem before solution.** Motivate a tool by showing the simpler thing suffices on the easy case, then breaking it on a harder one. Justify with scale numbers, not adjectives.

**Plain English in notes.** No jargon before it's introduced — "assistant" not "graph", "fixed list of emails" not "allowlist".

**Coverage lists are accounting, not skill.** A big checked-off question bank tracks coverage; it does not produce interview performance. Keep it out of the head during a drill — same lesson the DSA track already paid for.

**Depth beats breadth for the differentiator.** Every source agrees evals are the sharpest senior/junior signal in 2026 loops, and "we didn't have time for evals" is the fastest seniority downgrade. Xarvis already exists — making it measurable is worth more than memorising a thousand answers.

**Correctness checks are one word** — "correct" or "incorrect", no explanation unless asked.
