# AI Engineering — SDE-2 Strong Hire Syllabus

> Goal: build the breadth and depth needed for an **AI Engineer / Applied AI Engineer / LLM Engineer** role at companies like Meta, Google, Amazon, Rippling, Netflix, and similar product or platform teams.
>
> Scope: this is **not** a research-scientist syllabus. It is for software engineers who need to design, build, evaluate, ship, and operate **production AI systems** — especially **LLM apps, RAG systems, copilots, and agentic workflows**.

---

## Phase 1 — Software Foundations for AI Engineers

> Why this phase matters: strong AI engineers are still strong software engineers. Most failures in production AI systems are not caused by "not enough model knowledge" — they are caused by weak APIs, poor async design, bad retries, missing observability, and unclear ownership boundaries.

### 1.1 Python for AI systems
- typing, dataclasses / Pydantic, async/await, generators, context managers
- package management, virtual environments, lockfiles, reproducible dependencies
- FastAPI essentials — request validation, dependency injection, streaming endpoints, background work
- notebooks vs scripts vs production services — when each is appropriate
- testing AI plumbing — mocks for model providers, golden test cases for prompts, contract tests for tools

### 1.2 APIs, networking, and integration plumbing
- HTTP, gRPC, WebSockets, SSE/streaming responses
- request timeouts, retries, exponential backoff, idempotency keys
- auth patterns — API keys, OAuth, service-to-service auth
- webhooks, background jobs, event-driven pipelines
- cancellation propagation, client disconnects, and partial-stream failure handling

### 1.3 Data formats and ingestion basics
- JSON, JSONL, CSV, Parquet, Avro
- PDFs, HTML, Markdown, Office docs, OCR, image text extraction
- text normalization, Unicode pitfalls, newline/whitespace cleanup
- metadata extraction and schema normalization

### 1.4 Databases and queues you actually need in AI systems
- SQL for metadata, runs, prompts, eval results, human feedback
- object storage for raw docs, training corpora, transcripts, artifacts
- Redis for caching, rate limiting, ephemeral state
- queues for async ingestion, tool execution, eval pipelines

### 1.5 Production engineering basics
- feature flags, config management, secret management
- CI/CD for prompts, flows, and model config changes
- reproducibility — prompt version, model version, retrieval version, tool version
- environment promotion — dev vs staging vs prod for prompts, indexes, and tool integrations
- golden-path smoke tests before rollout

---

## Phase 2 — Applied ML Essentials for AI Engineers

> Why this phase matters: you do not need to become an ML researcher, but you do need enough ML intuition to reason about metrics, data quality, embeddings, evaluation, and when a model change actually improved the product.

### 2.1 Core ML concepts
- train / validation / test split
- overfitting vs underfitting
- label leakage and data contamination
- offline metric improvement vs real product improvement
- class imbalance, sampling bias, and distribution shift

### 2.2 Metrics
- classification metrics — precision, recall, F1, ROC-AUC
- ranking metrics — MRR, NDCG, Recall@K, Hit@K
- extraction metrics — exact match, span overlap, structured field accuracy
- calibration and confidence — when scores can and cannot be trusted

### 2.3 Embeddings
- what an embedding is — mapping text / image / code into a dense vector
- cosine similarity vs dot product vs Euclidean distance
- semantic similarity vs lexical similarity
- failure modes — near-duplicates, antonyms, domain mismatch, language mismatch

### 2.4 Data quality and human feedback
- annotation design
- gold set creation
- disagreement between reviewers
- feedback loops — thumbs up/down, edits, human overrides, escalations
- reviewer guidelines, label audits, and segment coverage

---

## Phase 3 — LLM Foundations

> Why this phase matters: if you are building LLM systems, you must understand what the model is and is not good at. Otherwise every architecture decision becomes cargo-culting.

### 3.1 Transformer / LLM basics
- tokenization — why models see tokens, not words
- embeddings, self-attention, positional information
- next-token prediction as the core training objective
- why longer prompts cost more and slow down inference

### 3.2 How models become useful assistants
- pretraining
- instruction tuning / supervised fine-tuning
- preference tuning — RLHF / DPO at a conceptual level
- base model vs instruct model

### 3.3 Inference-time behavior
- temperature, top-p, max output tokens, stop sequences
- deterministic vs creative settings
- streaming responses
- structured output / JSON schema / tool call generation
- context-window budgeting and output truncation failure modes

### 3.4 Model choice
- frontier model vs smaller cheap model
- closed model API vs open model you host yourself
- reasoning model vs low-latency model
- text-only vs multimodal
- when a classifier or rules engine is better than an LLM

### 3.5 Common LLM failure modes
- hallucination
- context dilution in long prompts
- lost-in-the-middle effects
- brittle formatting
- prompt injection
- shallow reasoning on multi-step tasks
- false confidence

---

## Phase 4 — Prompting and Context Engineering

> Why this phase matters: many AI products fail not because the model is weak, but because the instructions, context, examples, and output contracts are sloppy.

### 4.1 Prompt anatomy
- system / developer / user / tool messages
- instruction hierarchy and conflict resolution
- delimiters, explicit task framing, output contracts

### 4.2 Prompting patterns
- zero-shot vs few-shot
- decomposition and step-by-step task breakdown
- extraction prompts
- classification prompts
- grounded answering prompts
- tool-selection prompts

### 4.3 Structured generation
- JSON schema / typed outputs
- defensive prompting for parseable output
- forcing citations and evidence references
- separating reasoning from final answer when needed
- schema validation, repair loops, and when to fail closed instead of guessing

### 4.4 Context engineering
- deciding what belongs in the prompt vs what belongs in retrieval vs what belongs in a tool
- long-context tradeoffs — cost, latency, distraction, recency bias
- prompt templates, reusable context blocks, prompt caching
- context compression and summarization

### 4.5 Prompt quality management
- prompt regression tests
- failure example libraries
- prompt versioning and rollback
- when to stop prompt-tweaking and change the system architecture instead

---

## Phase 5 — Retrieval-Augmented Generation (RAG) and Knowledge Systems

> Why this phase matters: most enterprise AI systems are really retrieval and systems problems wrapped around an LLM.

### 5.1 When to use RAG
- RAG vs fine-tuning vs pure prompting vs deterministic software
- freshness requirements
- domain-specific knowledge
- access control and tenant-aware knowledge

### 5.2 Ingestion pipeline
- document loaders and parsers
- OCR and parsing errors
- deduplication and canonicalization
- metadata extraction
- source-of-truth strategy — full refresh vs incremental sync vs CDC
- document versioning and canonical IDs
- ACL extraction and permission metadata propagation
- delete handling / tombstones
- re-chunking and re-embedding migrations
- freshness SLAs, backfills, repair jobs, and indexing lag
- chunking strategy
  - fixed-size chunking
  - semantic chunking
  - section-aware chunking
  - overlap tradeoffs

### 5.3 Retrieval building blocks
- embedding model choice
- vector databases vs `pgvector` / Elasticsearch / hybrid stacks
- ANN basics — HNSW, IVF/PQ at the reasoning level required for latency/recall tradeoffs
- lexical retrieval — BM25
- hybrid retrieval — vector + lexical
- metadata filters and tenant filters
- multi-tenant index design — per-tenant namespace vs shared index + filters
- index update patterns — append, upsert, rebuild

### 5.4 Retrieval quality improvements
- query classification and routing
- query rewriting
- multi-query retrieval
- decomposition for multi-hop questions
- parent-child retrieval / document expansion
- rerankers / cross-encoders
- score fusion in hybrid retrieval
- citation validation and groundedness checks
- abstain / no-answer behavior when evidence is weak

### 5.5 Beyond document RAG
- SQL retrieval
- API retrieval
- graph retrieval
- codebase retrieval
- tabular retrieval

### 5.6 RAG evaluation
- Recall@K for retrieval
- context precision — did we retrieve useful chunks or junk?
- answer groundedness
- citation correctness
- stale-document detection
- no-answer precision / abstention quality
- permission leakage tests
- retrieval latency and tail behavior

### 5.7 RAG operations in production
- dual-index rollout and shadow evaluation before cutover
- re-embedding after parser or model changes
- monitoring ingest lag, parse failure rate, indexing lag, and delete propagation
- rollback strategy when a new chunking or embedding setup hurts recall
- permission drift detection between source systems and the index

---

## Phase 6 — Tool Use, Function Calling, and Agent Patterns

> Why this phase matters: the jump from "chatbot" to "useful AI system" usually happens when the model can read state, call tools, and act inside a controlled workflow.

### 6.1 Tool use fundamentals
- function calling / tool calling APIs
- tool schema design
- narrow tool contracts vs overly generic tools
- making tool outputs machine-friendly for the next model step
- tool versioning and backwards-compatible schema changes

### 6.2 Workflow vs agent
- deterministic workflow — known steps, fixed routing
- agentic workflow — model decides next action
- when a plain workflow is safer than a free-form agent

### 6.3 Common agent patterns
- ReAct
- planner / executor
- router
- supervisor / worker
- critic / verifier
- toolformer-style "pick the right tool when needed" behavior

### 6.4 Real-world execution concerns
- retries and idempotency
- partial failure and compensating actions
- timeouts and cancellation
- human approval gates for risky actions
- side-effect safety — sending emails, updating payroll, deleting records
- idempotency tokens for write-capable tools

### 6.5 Tool ecosystem design
- MCP-style tool servers and external tool adapters
- auth propagation to tools
- permission-aware tool access
- sandboxed code execution and browser / computer-use controls

---

## Phase 7 — LangGraph and Orchestration for Long-Running AI Workflows

> Why this phase matters: frameworks like LangGraph are useful when you need durable execution, branching, memory, interrupts, human review, and stateful long-running workflows. For SDE-2 strong hire, you should know when to use them and when not to.

### 7.1 Graph mental model
- nodes, edges, state, reducers
- graph execution vs chain execution
- typed state and validation

### 7.2 Control flow
- conditional edges
- loops and recursion limits
- termination criteria
- planner node vs executor node vs verifier node

### 7.3 Persistence and durability
- thread state
- checkpoints
- resumability
- recovery after process crash
- replay and debugging from saved state

### 7.4 Memory
- short-term conversational memory
- long-term memory
- profile memory vs semantic memory vs episodic memory
- when memory helps and when it pollutes the context

### 7.5 Human-in-the-loop
- interrupts
- review / approve / edit / reject
- escalation to manual workflows

### 7.6 Advanced orchestration
- subgraphs
- multi-agent coordination
- background jobs + queues + graph orchestration together
- concurrency and shared-state safety

### 7.7 Framework judgment and comparison
- when LangGraph is the right tool
- when a plain FastAPI service plus task queue is enough
- LangGraph vs Temporal / Step Functions for durable business workflows
- when orchestration should stay outside the model loop
- avoiding over-agentification

---

## Phase 8 — Evaluation, Experimentation, and Observability

> Why this phase matters: if you cannot measure the system, you cannot improve it safely. Strong AI engineers are evaluated heavily on whether they can define and run a real evaluation loop.

### 8.1 Evaluation design
- define the task precisely
- build gold datasets and regression suites
- coverage by user segment, failure mode, and risk class
- slice metrics by tenant, language, query type, and document source

### 8.2 Offline evaluation
- exact-match and rubric-based evaluation
- pairwise comparisons
- LLM-as-judge — where it helps and where it lies
- deterministic checks for schema validity and tool-call validity

### 8.3 RAG and agent-specific evals
- retrieval metrics
- groundedness metrics
- hallucination rate
- citation fidelity
- tool success rate
- task completion rate
- number of steps / tokens per successful task

### 8.4 Online evaluation
- acceptance rate
- edit distance from user-corrected output
- escalation rate to human support
- resolution time
- containment rate
- p50 / p95 latency
- cost per successful task

### 8.5 Observability
- traces per request
- prompt / response / tool-call logging
- retrieval traces — which chunks were fetched and why
- redaction-safe logging
- drift detection across model versions, prompt versions, and index versions
- attach prompt version, tool version, embedding version, and experiment ID to every trace

### 8.6 Experimentation and rollout
- A/B testing
- shadow traffic
- canary rollout
- rollback strategy
- eval gates before promotion

---

## Phase 9 — Serving, Inference, and AI Platform Engineering

> Why this phase matters: product companies care about quality, but they also care about latency, reliability, and unit economics. A model that is 2% better but 8x slower and 10x more expensive is often the wrong production choice.

### 9.1 Model serving choices
- third-party API providers
- hosted foundation model platforms
- self-hosted open models
- tradeoffs: control, privacy, cost, latency, maintenance
- model gateway / unified provider abstraction

### 9.2 Inference systems basics
- prompt length and output length as cost drivers
- token budgeting — system prompt, retrieved context, tool output, response budget
- batching
- streaming
- rate limiting
- provider quotas, concurrency limits, and connection management
- retries and circuit breakers
- fallback models and cascade strategies

### 9.3 Performance optimization
- model routing
- prompt compression
- semantic caching and response caching
- reranker + smaller generator vs one giant model
- fast classifier in front of expensive generation

### 9.4 GPU / inference-engine awareness
- GPU memory as the real bottleneck
- quantization
- KV cache intuition
- vLLM / TGI / Triton-level awareness — not implementation internals, but enough to reason about throughput and latency
- continuous batching intuition

### 9.5 Platform primitives
- model gateway
- model registry
- prompt registry
- eval registry
- feature flags
- tenant quotas and billing controls
- audit logs and run metadata

### 9.6 Reliability patterns
- queue-backed async work
- retries without duplicate side effects
- dead-letter queues
- backpressure
- graceful degradation when the model or vector DB is down

### 9.7 Capacity planning and unit economics
- requests/sec, concurrent requests, and p50 / p95 / p99 latency budgets
- tokens per request, requests per user per day, and monthly cost projection
- corpus size, chunk count, embedding footprint, and index storage growth
- cost per successful task, not just cost per request
- budget guards, rate caps, and kill switches for runaway spend

---

## Phase 10 — Fine-Tuning, Adaptation, and Model Improvement

> Why this phase matters: SDE-2 AI engineers are often not expected to invent new training algorithms, but they are expected to know when fine-tuning is useful, what it costs, and how to evaluate it properly.

### 10.1 When fine-tuning is appropriate
- repeated domain-specific style / format requirements
- classification / extraction tasks with stable labels
- tool-use behavior that prompting alone cannot stabilize
- when RAG is enough and fine-tuning is unnecessary

### 10.2 Fine-tuning methods
- supervised fine-tuning (SFT)
- LoRA / QLoRA
- preference tuning — DPO at a conceptual level
- adapters vs full fine-tune

### 10.3 Training data quality
- synthetic data generation
- deduplication
- contamination risks
- balancing easy and hard examples
- preserving evaluation holdout sets
- mining production traces safely for fine-tuning candidates

### 10.4 Deployment and governance
- model versioning
- eval-before-promote
- rollback
- regression monitoring after launch

### 10.5 Distillation and specialization
- using a large model to produce data for a smaller cheaper model
- task-specialized models vs one general agent

---

## Phase 11 — Safety, Security, and Governance

> Why this phase matters: as soon as an AI system can read internal docs, call business tools, or act on behalf of a user, safety and security stop being optional.

### 11.1 Prompt injection and jailbreaks
- direct prompt injection
- indirect prompt injection via retrieved documents, websites, or emails
- tool-manipulation attacks

### 11.2 Data security
- secret leakage
- tenant isolation
- RBAC / ABAC-aware retrieval
- data residency and retention
- redaction and PII handling
- permission checks at retrieval time vs answer time

### 11.3 Safe tool execution
- sandboxing
- allowlists / deny-lists
- approval workflows for high-risk tools
- read-only vs write-capable tools

### 11.4 Policy and abuse controls
- moderation pipelines
- unsafe content handling
- abuse rate limiting
- audit logs and traceability
- human review queues

### 11.5 Governance and compliance
- model cards and decision logs
- dataset provenance
- legal review for training and retention practices
- change management for prompts, tools, and models

---

## Phase 12 — End-to-End AI System Design Case Studies

> Why this phase matters: this is where interviewers decide whether you can integrate all of the above into a coherent production system.

### 12.1 Enterprise knowledge assistant
- tenant-aware RAG
- ACL-aware retrieval
- citations and groundedness
- fallback to search when confidence is low

### 12.2 Customer support copilot
- retrieval over policies and past tickets
- summarization + suggested reply
- human acceptance / edit loop
- containment and escalation metrics

### 12.3 Workflow automation agent
- payroll / HR / IT / finance actions
- tool permissioning
- human approval gates
- auditability and compensating actions

### 12.4 Meeting / voice assistant
- ASR + transcript cleanup
- retrieval over prior meetings
- action item extraction
- latency budgets for real-time and near-real-time experiences

### 12.5 Codebase assistant / coding agent
- repo retrieval
- tool execution
- patch generation
- test execution
- sandboxing and diff review

### 12.6 Document extraction and back-office automation
- OCR
- structured extraction
- confidence thresholds
- human review for low-confidence fields

### 12.7 Data / SQL analyst assistant
- schema retrieval
- SQL generation
- query validation
- guardrails against destructive queries

### 12.8 AI platform / LLM gateway
- unified model access across providers
- routing, fallback, quotas, and cost controls
- tracing, eval hooks, and prompt / model versioning
- policy enforcement and safe rollout of model changes

For every case study, practice this sequence:
- requirements and risk classification
- workload sizing — users, QPS, token budget, corpus size, freshness SLA
- model choice
- retrieval / tool strategy
- orchestration choice
- evaluation plan
- latency and cost budget
- safety controls
- rollout strategy

---

## Phase 13 — AI Engineering Interview Framework

> Why this phase matters: being good at the work and sounding good in an interview are related, but not identical. You need a repeatable answer structure.

### 13.1 The answer structure
- what is the task?
- what is the scale — users, QPS, documents, tokens, latency target?
- what accuracy / latency / cost / safety bar matters?
- should this be rules, classical ML, RAG, fine-tuning, or an agent?
- what are the core components?
- how do we evaluate quality before and after launch?
- what can fail, and how do we mitigate it?

### 13.2 What interviewers want to hear
- explicit tradeoffs, not buzzwords
- numbers, not adjectives
- why you chose a model, not just the model name
- why a workflow is safer than an agent, or vice versa
- what metric proves success
- how you would roll out safely

### 13.3 Common machine-coding / implementation rounds
- build a retrieval-backed chat endpoint
- add structured output and validation
- add tool calling with retries and logging
- design a LangGraph workflow with approval checkpoints
- add tracing and offline evaluation hooks
- debug a bad RAG pipeline with low recall or hallucinations

### 13.4 Common debugging scenarios
- agent loops forever
- retrieval brings wrong chunks
- citations do not match the answer
- tool schema causes malformed calls
- latency explodes after adding long context
- model upgrade regresses a key user segment
- re-embedding or re-chunking rollout destroys retrieval recall
- permission filter bug exposes the wrong tenant's documents

### 13.5 Numbers you should always estimate
- requests/sec and concurrency
- prompt tokens, retrieved tokens, output tokens
- corpus size, chunk count, and index size
- ingest lag and freshness SLA
- p50 / p95 latency budget by stage
- monthly spend and cost per successful task

---

## Company-Specific Emphasis

- **Meta**
  - product quality, iteration speed, personalization, ranking-aware thinking, online experiments
- **Google**
  - retrieval quality, infra rigor, search / grounding, evaluation discipline, scalable platform thinking
- **Amazon**
  - operational excellence, cost control, service ownership, IAM / permissions, workflow automation
- **Netflix**
  - experimentation culture, platform maturity, personalization, large-scale data pipelines, reliability
- **Rippling**
  - enterprise automation, tool execution correctness, permissions, auditability, human approval flows

---

## What “Strong Hire SDE-2” Means for This Syllabus

- You can build and ship a single-agent or workflow-based LLM application end-to-end.
- You can explain when not to use an agent.
- You can design a RAG system and talk about chunking, indexing, retrieval quality, reranking, citations, freshness, and permissions.
- You can implement LangGraph orchestration with state, persistence, interrupts, and debugging.
- You can define offline and online evals instead of hand-waving about "accuracy."
- You can reason about latency, cost, retries, rate limits, caching, fallbacks, and capacity.
- You can identify prompt injection, data leakage, permission, and tool-safety risks.
- You can explain RAG vs fine-tuning vs deterministic software clearly and defensibly.

---

## Suggested Study Order

1. Phase 1 → 4 first: foundations, ML essentials, LLM basics, prompting
2. Then Phase 5 → 7: RAG, tools, agents, LangGraph
3. Then Phase 8 → 11: evals, serving, fine-tuning, safety
4. Finish with Phase 12 → 13: case studies and interview drills

If your current work is already **LLM apps + LangGraph**, prioritise:
- Phase 5 — Retrieval and knowledge systems
- Phase 6 — Tool use and agent patterns
- Phase 7 — LangGraph orchestration
- Phase 8 — Evaluation and observability
- Phase 9 — Serving, reliability, and cost

---

## Minimum Hands-On Proof That You’re Actually Interview-Ready

- Build a streaming FastAPI chat service with retries, tracing, and structured output validation
- Build a production-style RAG pipeline with ingestion, re-indexing, ACL-aware retrieval, citations, and offline evals
- Build a tool-using workflow with approval gates, idempotent side effects, and failure recovery
- Build one evaluation harness that compares prompt / model / retrieval changes before rollout
- For each project, be able to explain workload estimates, latency budget, failure modes, rollout plan, and cost model
