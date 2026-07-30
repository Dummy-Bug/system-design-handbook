#ai-engineering #observability #tracing #otel #block-2 #syllabus

# Block 2 · Observability & Tracing — Syllabus

15 concepts. **Generic** — the field, not Xarvis. Map afterwards.

> Learn the full surface first, *then* decide what Xarvis can demonstrate. Deriving a syllabus from the codebase silently drops every concept the codebase happens not to exercise — and those are the ones interviewers ask about.

**Why this block sits second:** error analysis (Block 3) is trace-by-hand. You cannot bucket failures you cannot see. Everything downstream — cost attribution, latency budgets, judge inputs — reads from traces.

**Currency check (2026-07-30):** OpenTelemetry graduated CNCF on 2026-05-21, formalising it as the default observability standard. The **GenAI semantic conventions are still mostly experimental**, with v1.37+ as the stable baseline and v1.41.0 adding reasoning tokens and enhanced agent attributes. **Agent Spans and MCP conventions are the two newest pieces** and are likely to set the pattern for how the ecosystem instruments agents. Re-check before relying on any specific attribute name.

---

## A · Why logs aren't enough

**1. What breaks when you debug an agent with logs**
A log line is a point event; an agent failure is a *shape* — a path through nodes, tools, and retries. Why grep cannot answer "why did it pick that tool," and why the request/response pair is the wrong unit of observation.

**2. Traces, spans, and the trace tree**
Span, parent/child, root span, trace ID, span ID, attributes, events, status. The one mental model everything else hangs off.

**3. What a *good* agent trace looks like**
One span per node, per model call, per tool call, per retrieval, per external API hop. What must be attached to each: model version, prompt version, token counts, latency, cost, cache hit/miss, error class.

**4. Observability vs evals**
Two different jobs that vendors sell as one product. Observability tells you what happened in production; evals tell you whether a change is safe to ship. Traces are the *raw material* for eval sets — that's the connection.

## B · The standard

**5. OpenTelemetry fundamentals**
The data model — traces, metrics, logs. SDK vs collector vs backend. Why a vendor-neutral wire format matters when you'll change observability vendors twice.

**6. GenAI semantic conventions**
Why an agreed attribute schema exists at all. The four coverage areas: **LLM client spans** (direct API calls), **agent spans** (multi-step workflows), **events** (prompt/completion content capture), **metrics** (aggregates). Current stability status and what "experimental" means for you.

**7. Agent spans and MCP conventions**
The two newest additions, aimed at two concrete problems: black-box agent reasoning, and traces that break at the MCP boundary. What they standardise and why it matters for tool-calling systems.

**8. Content capture and the privacy problem**
Prompts and completions contain user data. Capturing them makes debugging possible and makes you a data processor. Redaction strategies, sampling, and how to redact without destroying your ability to debug.

## C · The tooling landscape

**9. Instrumentation styles: proxy vs SDK**
Proxy (swap the base URL, instant logging, shallow) vs SDK (instrument the code, deeper span-level control, more work). When each is the right call.

**10. The platform landscape**
Six anchor the field in 2026: **LangSmith** (LangChain/LangGraph-native, near-zero setup inside that ecosystem, significant overhead outside it), **Langfuse** (open-source leader, genuinely self-hostable, no usage limits self-hosted), **Arize Phoenix** (ML-grade rigor, fully open-source, strongest bet if OTel compatibility is a hard requirement), **Braintrust** (best eval-gated CI/CD workflow), **Helicone** (drop-in proxy, simplest install), **Datadog / Honeycomb** (enterprise-default if you already live there).

**11. Choosing one — the decision that isn't about features**
Hosted vs self-hosted as a *data-residency* decision, not a convenience one. Vendor lock-in via proprietary span formats. The question that settles it: can this data legally leave your infrastructure?

## D · What you attribute

**12. Cost attribution**
Tokens in/out per span → cost per node → cost per conversation. p50 and p95, not just mean. Attribution by feature, by tenant, by user. Why an unattributed bill is an unfixable bill.

**13. Latency attribution**
Per-stage breakdown: queueing, model call, tool execution, external API, cache hit vs miss. TTFT vs TPOT vs total. Why p99 rather than average, and what actually causes tail latency in LLM serving.

**14. Metrics, dashboards, and alerting**
Which aggregates are worth computing. What pages someone at 3am vs what waits for morning. The specific hard case: every span returns 200, latency is fine, and quality has silently degraded — what do you alert on?

## E · Using it

**15. Drift and silent regression detection**
Kinds of drift — input distribution, output distribution, tool-usage mix, cost per request. Detecting a provider-side model update you were never told about. Turning production traces into the next eval set.

---

## Notes to write

```
02-Observability/
├── 00-Syllabus.md      ← this file
├── 00-Resources.md
├── 01-Why-Logs-Arent-Enough.md
│   … through …
└── 15-Drift-And-Silent-Regression.md
```

## Deferred

| Topic | Goes to |
|---|---|
| Golden sets, trajectory evals, pass@k | Block 1 |
| LLM-as-judge, calibration, error analysis method | Block 3 |
| Prompt caching mechanics, routing economics | Block 5 |
| Retrieval-specific spans and RAG metrics | Blocks 7-8 |

## Xarvis mapping

*Filled after learning, not before.* Each concept lands in **applicable** / **theory-only** / **parked**.

Going in: Xarvis is unusually strong here — real traffic, real multi-step traces, and a genuine "the logs didn't tell us" story. Expect most of this block to be applicable. The known gap is retrieval spans (concept 3), since there is no retrieval to trace yet.

## Sources to verify against

- [OpenTelemetry GenAI semantic conventions — status and coverage](https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions)
- [OTel for AI systems: LLM and agent observability 2026](https://uptrace.dev/blog/opentelemetry-ai-systems)
- [Agent observability platform comparison 2026](https://www.digitalapplied.com/blog/agent-observability-platforms-langsmith-langfuse-arize-2026)
- [Self-hosting and OSS options compared](https://latitude.so/blog/best-llm-observability-tools-agents-latitude-vs-langfuse-langsmith)
- Corpus: `07-evaluation-and-observability/` Q8, Q9, Q13, Q32, Q33, Q40, Q41
