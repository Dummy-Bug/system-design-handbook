#ai-engineering #observability #tracing #otel #block-2 #syllabus

# Block 2 · Observability and Tracing — Syllabus

**15 notes, 153 rungs.** Generic — the field and its failure modes, not Xarvis's implementation, which is mapped at the bottom.

> A rung is the **smallest thing that has to be understood before the next thing makes sense** — the request took 9 seconds, therefore you sum the spans, therefore they come to 4, therefore 5 seconds happened somewhere you did not instrument, therefore the gap is the finding. Rungs are not topics and not section headings. Seven to fourteen of them build one note.
>
> They are ordered so that **each rung either breaks the previous one or is forced by it.** That ordering is the whole design. A list of true statements about tracing teaches nothing; a chain where every step is the answer to a problem the last step created is what sticks.

**Why generic first.** If the syllabus is derived from the codebase, every concept the codebase happens not to exercise gets silently dropped — and those are exactly the ones an interviewer asks about. So: learn the full surface, **then** map.

**Why this block sits second.** Error analysis in Block 1 note 13 is trace-by-hand, and you cannot bucket failures you cannot see. Block 1 note 22 names the capture stage as the one that fails first in an untraced system. Everything downstream — cost attribution, latency budgets, judge inputs — reads from traces.

**Two halves, trained differently.** Notes 1 to 8 and 12, 13, 15 are mechanism — what a trace is and where it lies — and respond to retrieval practice, so the rungs are the recall unit. Notes 9, 10, 11 and 14 are **decisions**: which instrumentation style, which platform, hosted or not, and what is allowed to wake someone at 3am. Those are worked as positions defended against changed constraints, not recalled, because the facts underneath them rot in weeks.

**Currency check (2026-09-06):** The previous check on this file said v1.37+ was the stable baseline for GenAI semantic conventions. **That was wrong and the correction matters**: as of mid-2026 **no GenAI span, event, metric or attribute is marked Stable** — nearly every `gen_ai.*` attribute carries a Development stability badge, which means **attribute names can change without a major version bump**. Anything you hard-code against them is a maintenance liability, and saying so is the right answer when asked.

Two structural changes landed since: with **semantic-conventions v1.42.0 on 12 June 2026**, all GenAI conventions were **deprecated in the main repo and moved to a dedicated one**, `open-telemetry/semantic-conventions-genai` — and the **MCP conventions moved into that same repo**, so an MCP tool call now shares a trace vocabulary with the agent issuing it. The conventions also now model a whole agent run as a span tree rather than isolated model calls: **`invoke_agent`** containing **`chat`** per model call and **`execute_tool`** per tool invocation. **v1.36 is the transition baseline** — existing instrumentation defaults to the old attribute format, and `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` opts into the current one.

OpenTelemetry itself graduated from the CNCF on 2026-05-21, which is why the vendor-neutral bet is the safe one even while the GenAI layer is unsettled. Re-verify before relying on: any specific attribute name, the current stability badges, and free-tier retention on whichever platform you pick — the numbers move and they decide whether you have a corpus or a rolling window.

---

## How to teach from this

**One note per session, rungs in order, never skipping.** A skipped rung breaks the chain — the next one stops being a discovery and becomes a fact to memorise.

**Where a rung says break, it is run, not read.** Summing the spans of a real request and finding five unaccounted seconds produces a problem the fix attaches to. Reading that traces have gaps produces a fact that decays.

**Recall is per note, from memory, file closed.** Recognising an answer does not count.

**Notes 9 to 11 and 14 are not recall material.** Re-argue them when a constraint changes — a new data-residency rule, a bill that doubled, a platform that changed its free tier. A position you can only recite is not a position.

**Three rabbit holes are marked and binding** — collector configuration depth in note 5, the distributed-tracing research lineage in note 2, and vendor feature matrices in note 10. All three are deep, and the third rots faster than you can learn it.

**Spacing:** re-test notes 1 to 4 after finishing note 8, and 5 to 13 once something is actually instrumented. Same-day re-testing is close to wasted, because retrieval works when forgetting has started.

**The syllabus governs the numbering — never the source material.** A lecture, video or article covering concept 7 becomes `07-*.md`, even if it was the fourth video in its playlist. Gaps in the numbering are concepts not yet reached, not missing files.

---

# A · Why Logs Are Not Enough

## Note 1 · What Breaks When You Debug An Agent With Logs

10 rungs. **Break:** take one failed agent request and try to answer why it chose that tool, using only grep against the log file.

1. A log line is a **point event** — a timestamp, a level, a message, written where somebody thought to write one.
2. That is sufficient when the failure is also a point: this call threw, this field was null, this query timed out.
3. **Break it** — an agent failure is not a point, it is a **shape**: a path through nodes, model calls, tool calls and retries, where every individual step succeeded.
4. Grep can find the steps and cannot reconstruct the path, because a log line does not know what called it.
5. So the missing thing is **structure**, specifically parentage — which call happened inside which other call.
6. The second missing thing is **duration**: a log line records that something happened, not how long it took, so latency has to be reconstructed by subtracting timestamps of lines that may not be adjacent.
7. The third is **correlation**: with concurrent requests interleaved in one file, the lines belonging to one conversation are not contiguous and often not distinguishable.
8. A request id in every line fixes correlation only, which is why teams add one, feel better, and still cannot answer the original question.
9. So the unit of observation has to change from the line to the **request tree**, and that is what a trace is.
10. Which reframes the whole block: tracing is not better logging, it is a different data model, and the reason to adopt it is that agent failures are shaped like trees.

> **Recall:** What kind of failure are logs correctly sufficient for? · Name the three things a log line lacks, and which one a request id fixes. · State in one sentence why an agent forces the change.

## Note 2 · Traces, Spans, And The Trace Tree

11 rungs. **Break:** create one span, then create a second inside it, and look at what links them.

1. A **span** is one unit of work with a start time, an end time, and a name.
2. A span carries a **span id**, and a **trace id** shared by every span in the same request.
3. It also carries a **parent span id**, and that single field is what turns a list into a tree.
4. **Break it** — omit the parent id and you have a flat pile of timed events, which is logs with durations.
5. The span with no parent is the **root**, and it represents the whole request.
6. Spans carry **attributes**, which are key-value facts about the work — model name, token counts, tool name, tenant.
7. They also carry **events**, which are timestamped points inside a span, for things that happen without lasting.
8. And a **status** — unset, ok, or error — which is what makes a trace filterable to the failures.
9. Nesting is by wall-clock containment, so a child that outlives its parent is a bug in your instrumentation, not an interesting finding.
10. **Context propagation** is the mechanism that carries the trace id and current span across function calls, threads, and network hops.
11. Which is the part that breaks in practice: an async boundary, a queue, or a service hop where context is not propagated silently starts a **new trace**, and the tree quietly becomes two.

> **Recall:** Which single field turns a list of spans into a tree? · What is the difference between an attribute and an event? · What is the visible symptom of broken context propagation?
>
> **Stop:** No Dapper lineage, sampling algorithm derivations, or distributed-tracing research history. Rabbit hole, marked, binding.

## Note 3 · What A Good Agent Trace Looks Like

12 rungs. **Break:** open a trace of your own system and write down three questions it cannot answer.

1. Given a tree, the design question is where the span boundaries go.
2. The rule is one span per unit you would want to time, blame, or price **independently**.
3. Which produces the standard set for an agent: one span per graph node, per model call, per tool call, per retrieval, per external API hop.
4. **Break it** — put the whole agent in one span and you can see it was slow and nothing about why, which is where most first instrumentation lands.
5. **Break it the other way** — a span per function call and the tree is unreadable and the storage bill is real.
6. Each model call span needs: model name **and version**, prompt version, input and output token counts, latency, cost, finish reason.
7. Model version matters more than it looks, because a provider can change what sits behind a version string and this attribute is how you later prove it.
8. Prompt version only exists if prompts are versioned artifacts, which is why prompt templating is a prerequisite rather than a nicety.
9. Each tool call span needs: tool name, arguments, outcome, error class if it failed, and whether a retry followed.
10. Error **class** rather than error message, because you will group by it and free-text messages do not group.
11. Cache hit or miss belongs on any span that can be served from cache, and it is the attribute people omit and then cannot explain a cost drop.
12. The test of a trace is not whether it renders, it is whether you can answer why did this cost that much and why did it take that long without opening the code.

> **Recall:** State the span-boundary rule. · Name the two opposite failure modes of span granularity. · Why error class rather than error message? · What is the test of a good trace?

## Note 4 · Observability Versus Evals

8 rungs. No break — this is placement.

1. Observability and evals are sold as one product and answer different questions.
2. **Observability** answers what happened, in production, after the fact, on traffic you did not choose.
3. **Evals** answer whether a change is safe to ship, before the fact, on cases you did choose.
4. Which means one is descriptive and the other is comparative, and neither substitutes.
5. **Break the assumption that observability is enough** — a dashboard showing everything green cannot tell you whether the prompt change you are about to merge makes things worse, because the change has not run yet.
6. **Break the reverse** — a green eval suite cannot tell you what is failing right now on an input nobody imagined.
7. The connection is directional and worth stating precisely: **traces are the raw material for eval sets**. Error analysis reads traces, buckets them, and the buckets become cases.
8. So this block is not parallel to Block 1, it is upstream of it, and that is the entire reason for the ordering.

> **Recall:** State the two questions in one sentence each. · What can each one not do? · Which direction does the dependency run, and why?

---

# B · The Standard

## Note 5 · OpenTelemetry Fundamentals

11 rungs. **Break:** emit spans to one backend, then change backend without touching application code.

1. Every observability vendor would like to define its own wire format.
2. **Break it** — you will change vendors at least twice, and a proprietary format means re-instrumenting the application each time.
3. OpenTelemetry is the vendor-neutral answer: one instrumentation, many backends.
4. It graduated from the CNCF on 2026-05-21, which is the signal that this bet is safe at the infrastructure layer.
5. Its data model has three signals — **traces**, **metrics**, **logs** — and they are correlated by shared ids rather than merged.
6. Three components, and confusing them is the usual beginner error. The **SDK** runs inside your application and produces telemetry.
7. The **collector** is a separate process that receives, batches, filters, transforms and forwards it.
8. The **backend** stores and queries it, and is the only piece that is vendor-specific.
9. Which is what makes the swap in the break cheap: the application talks to the collector, and the collector's configuration is the only thing that changes.
10. The collector is also where redaction belongs, for the reason note 8 gives — it is the last place you control before data leaves.
11. **Auto-instrumentation** covers common libraries with no code changes and gets you HTTP and database spans free; it does not know what a tool call is, so the agent-shaped part is always manual.

> **Recall:** Name the three components and which one is vendor-specific. · Why does the collector make a vendor swap cheap? · What does auto-instrumentation not give you, and why?
>
> **Stop:** No collector pipeline configuration, processor tuning, or deployment topologies. Ops-owned, deep, and not what an interview asks. Rabbit hole, marked, binding.

## Note 6 · GenAI Semantic Conventions

12 rungs. **Break:** look up the stability badge on any `gen_ai.*` attribute yourself before writing it into code.

1. A span's attributes are free-form strings, so two teams instrumenting the same thing produce incompatible traces.
2. Which makes cross-tool dashboards, shared queries and vendor portability impossible even with a shared wire format.
3. Semantic conventions are the agreed attribute schema that fixes that — agreed names for agreed concepts.
4. The GenAI conventions cover four areas: **LLM client spans** for direct API calls, **agent spans** for multi-step workflows, **events** for prompt and completion content, and **metrics** for aggregates.
5. **Break the assumption that agreed means settled** — as of mid-2026 nothing in the GenAI conventions is marked Stable; nearly every attribute carries a **Development** badge.
6. Development stability means the name can change **without a major version bump**, which is a stronger warning than experimental normally implies.
7. So code that hard-codes these names is a maintenance liability, and the practical defence is to write them once, in one adapter, rather than scattered through the application.
8. The conventions also moved: with **v1.42.0 on 12 June 2026** they were deprecated in the main semantic-conventions repo and relocated to `open-telemetry/semantic-conventions-genai`.
9. Which means search results and blog posts predating June point at a deprecated location, and this is the single most common way to get current-looking wrong information here.
10. **v1.36 is the transition baseline** — existing instrumentation keeps emitting the old attribute format by default.
11. Opting in is an environment variable, `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`, which exists precisely because the maintainers expect breakage.
12. The honest position, and a good interview answer: adopt the conventions for portability, isolate them behind one layer, and expect to update.

> **Recall:** What problem do semantic conventions solve that a wire format does not? · What does a Development badge permit that experimental usually does not? · Where did the conventions move, and why does that break your search results?

## Note 7 · Agent Spans And MCP Conventions

9 rungs. No break — this is the current shape of the standard.

1. Early GenAI instrumentation traced **model calls**, because that is where the money and latency obviously were.
2. **Break it** — an agent's interesting failures happen between model calls: the wrong tool, the wrong argument, the loop that never terminates.
3. So the conventions now model a whole agent run as a span tree rather than a series of isolated calls.
4. The shape is three nested span kinds: **`invoke_agent`** for the agent run, containing **`chat`** for each model call, containing or beside **`execute_tool`** for each tool invocation.
5. Which makes the trajectory from Block 1 note 8 directly readable off the trace, and this is the concrete link between the two blocks.
6. The second addition addresses a different break: a tool served over **MCP** runs in another process, so the trace ended at the boundary and resumed as an unrelated trace on the other side.
7. With the v1.42.0 move, the MCP conventions live in the same GenAI repo, so an MCP tool call shares the trace vocabulary of the agent issuing it.
8. That only helps if **context propagates across the MCP call**, which is note 2's failure mode arriving in a new place.
9. So the two additions together are aimed at two named problems: black-box agent reasoning, and traces that break at a process boundary.

> **Recall:** Name the three nested span kinds and what each represents. · Which Block 1 concept becomes readable from the trace, and why? · What breaks at an MCP boundary, and what does the convention not fix on its own?

## Note 8 · Content Capture And The Privacy Problem

11 rungs. **Break:** look at the captured prompts of your own system and count how many contain a real person's data.

1. A trace with token counts and latencies tells you a call was slow and expensive.
2. **Break it** — it cannot tell you why the model chose wrongly, because the prompt and the completion are not there.
3. So debugging quality requires capturing content, and content capture is a separate decision from tracing.
4. **Break that** — prompts in an HR assistant contain salaries, leave records, and named employees, so capturing them turns your observability backend into a store of personal data.
5. Which changes the legal shape of the vendor relationship: they become a data processor, and where their servers are becomes a compliance question rather than a latency one.
6. Three mitigations exist and each costs something. **Redaction** removes or masks fields before export.
7. Its cost is that over-redaction destroys the debuggability you captured content for — a prompt with every name replaced cannot explain a name-disambiguation failure.
8. So redaction is designed per field, not globally: mask the salary, keep the structure, hash the identifier so traces remain joinable without being readable.
9. **Sampling** captures content for a fraction of traffic, which reduces exposure proportionally and is the cheapest lever.
10. Its cost is that rare failures are exactly what you want content for, so uniform sampling drops the interesting cases — the stratified argument from Block 1 note 6 applies unchanged.
11. **Retention limits** are the third, and they interact with everything downstream: a short retention window means error analysis cannot be deferred, which makes this an eval-schedule decision rather than a storage setting.

> **Recall:** Why is content capture a separate decision from tracing? · What does over-redaction cost, and what is the per-field alternative? · Why does uniform sampling defeat the purpose here?

---

# C · The Tooling Landscape

## Note 9 · Instrumentation Styles — Proxy Versus SDK

9 rungs. **Break:** point your base URL at a proxy, then try to see which graph node made the call. This is a decision, not recall.

1. Two ways to get telemetry out of an LLM application, and they differ in what they can see.
2. **Proxy** — change the base URL so calls route through a service that logs them.
3. Its advantage is real and worth respecting: zero code change, works across languages, and running before lunch.
4. **Break it** — a proxy sees HTTP requests to the model provider, so it can tell you the call happened and cannot tell you which node made it, what tool ran between two calls, or why.
5. Because everything a proxy knows arrives in the request, and the request does not carry your application's structure.
6. **SDK** — instrument in code, creating spans where the work is, so parentage and application concepts are available.
7. Its cost is code changes in every path, per language, and ongoing maintenance as the application changes.
8. So the honest rule is about what you are debugging: cost and rate questions are answerable by a proxy, and behaviour questions are not.
9. The common real answer is both — a proxy first for immediate coverage, SDK spans added where a real question demanded them.

> **Position to defend:** Which would you start with in a system with two weeks of access left, and what changes your answer?

## Note 10 · The Platform Landscape

10 rungs. Orientation. Facts here rot fastest in the block.

1. Six platforms anchor the field in 2026, and their differences are about **fit**, not features.
2. **LangSmith** — LangChain and LangGraph native, close to zero setup inside that ecosystem, meaningful overhead outside it.
3. Its free Developer tier is small and the retention is short, which is a fact with consequences rather than a pricing detail — see note 8.
4. **Langfuse** — the open-source leader, MIT licensed, genuinely self-hostable with no usage ceiling when you run it, and strong prompt management.
5. **Arize Phoenix** — OpenTelemetry-native from the ground up and fully open source, which makes it the strongest bet when OTel compatibility is a hard requirement.
6. **Braintrust** — the eval-gated CI/CD workflow, with eval scores native to the trace view rather than bolted beside it.
7. **Helicone** — the drop-in proxy, which is note 9's proxy row made concrete.
8. **Datadog and Honeycomb** — the correct answer when the organisation already lives there, because a second observability tool nobody opens is worse than a worse tool everybody does.
9. Two open-source alternatives worth knowing by name: **Opik** and **MLflow**, both Apache 2.0.
10. The only durable statement in this note is that the ranking changes every few months, so learn the **axes** — ecosystem fit, OTel nativeness, self-hostability, eval integration, retention — and re-read the numbers when you need them.

> **Position to defend:** Name the axis that decides each of the six. · Which two are interchangeable for your use case, and what would separate them?
>
> **Stop:** No feature matrices, pricing tables, or version-by-version comparisons. They rot faster than you can learn them. Rabbit hole, marked, binding.

## Note 11 · Choosing One — The Decision That Is Not About Features

8 rungs. Decision note.

1. The obvious way to choose is to compare features, and it is the wrong way.
2. **Break it** — the feature lists converge within two releases, and the thing that does not converge is where the data lives.
3. So the first question is legal, not technical: **can this data lawfully leave our infrastructure?**
4. If prompts contain personal data and the answer is no, the entire hosted column is eliminated and the comparison is over.
5. Which is why self-hostability is the axis that actually decides, and why the MIT and Apache-licensed options matter disproportionately.
6. The second question is **lock-in**, and it is subtler: a proprietary span format means your history does not come with you when you leave.
7. OpenTelemetry-native platforms reduce that to a re-point rather than a re-instrumentation, which is the practical value of note 5's neutrality.
8. The third is retention, which is a cost question dressed as a storage setting, and which decides whether traces are an asset or a rolling window.

> **Position to defend:** State the three questions in order. · Why does feature comparison mislead? · What exactly is lost to lock-in, given you can always re-instrument?

---

# D · What You Attribute

## Note 12 · Cost Attribution

11 rungs. **Break:** compute the cost of one conversation from its trace, then try to compute it per tenant.

1. A provider bill is one number per month, which tells you what you spent and nothing about what to change.
2. **Break it** — an unattributed bill is an unfixable bill, because every optimisation needs to know which part to optimise.
3. Attribution starts at the span: input and output token counts on every model call.
4. Times the model's per-token price, which means model name and version have to be on the span too, and prices change.
5. Summing to the trace gives **cost per conversation**, which is the first genuinely useful number and the one most systems cannot produce.
6. Summing by attribute gives the ones that drive decisions: cost per feature, per tenant, per user, per tool.
7. **Per tenant is the one that breaks** — it requires a tenant attribute on every span, which requires it to be propagated through the context, which is note 2's mechanism doing real work.
8. Report **p50 and p95**, not the mean, because LLM cost distributions have long tails and the mean describes nobody.
9. The p95 conversation is also the one worth reading, since expensive usually means looping.
10. Cached and uncached calls must be distinguished or savings are invisible and regressions in cache hit rate look like nothing.
11. The output of this note is a number per unit that someone can act on, and the reason it belongs to a resume is that most engineers have never produced one.

> **Recall:** Why is the mean the wrong statistic here? · What has to be true for per-tenant attribution to work? · What does the p95 conversation usually turn out to be?

## Note 13 · Latency Attribution

11 rungs. **Break:** time a request end to end, sum its spans, and account for the difference.

1. A slow request has a total duration, which localises nothing.
2. Spans decompose it: queueing, model call, tool execution, external API, cache lookup.
3. **Break it** — sum the spans and the total is smaller than the wall-clock time, and the gap is the finding.
4. Gaps are unattributed work: serialisation, framework overhead, waiting on a lock, an await nobody instrumented.
5. Which makes the gap the most useful thing in a latency trace and the thing dashboards hide by charting only what was measured.
6. Streaming systems need different numbers than request-response ones, because the user's experience starts before the response ends.
7. **Time to first token** is what the user perceives as responsive, and it is a different measurement from total latency.
8. **Time per output token** governs how fast the answer reads once it starts.
9. Total latency still matters for cost and capacity, so all three are reported and none substitutes.
10. Report **p99**, because tail latency is what users complain about and averages conceal it entirely.
11. In LLM serving the tail is usually queueing under load, a retry, or a long tool call — not the model being slow — which is exactly the distinction spans exist to make.

> **Recall:** What does a gap between wall-clock and summed spans mean? · Name the three latency numbers a streaming system needs and what each governs. · What actually causes tail latency here?

## Note 14 · Metrics, Dashboards, And Alerting

10 rungs. **Break:** describe an outage where every span is 200 and latency is normal. Decision note.

1. Traces are per-request and too numerous to watch, so aggregates are computed from them.
2. Which aggregates is a design decision: request rate, error rate, p50/p95/p99 latency, cost per hour, tool-call mix, cache hit rate.
3. A dashboard is for a human already asking a question; an alert is for a human who is not.
4. **Break it** — alert on everything and the alerts get muted, at which point the system is unmonitored and everyone believes it is monitored.
5. So the rule is that an alert must name an action, and anything without one belongs on a dashboard.
6. Which splits pages by time: hard failures and cost spikes page at 3am, quality drift waits for morning.
7. **The hard case** — every span returns 200, latency is normal, cost is normal, and the answers have quietly become worse.
8. Nothing in the operational metric set fires, because nothing operational is wrong.
9. So the alertable signal has to be a **proxy for quality**, and the candidates come from Block 1 note 6: retry rate, rephrasing rate, escalation rate, abandonment, thumbs-down rate, refusal rate.
10. Which is the honest answer to the hard case — you cannot alert on quality directly, you alert on the distribution of user behaviour and treat a shift as a symptom.

> **Position to defend:** State the rule that separates an alert from a dashboard. · Answer the hard case in one sentence. · Which proxy would you pick first for a chat assistant, and why that one?

---

# E · Using It

## Note 15 · Drift And Silent Regression Detection

10 rungs. **Break:** compare this week's output-length distribution against last month's, having changed nothing.

1. A system that passed every eval at launch degrades without anyone changing it.
2. Four things drift, and they have different causes. **Input distribution** — users start asking different things.
3. **Output distribution** — the same inputs start producing different answers.
4. **Tool-usage mix** — the agent starts reaching for different tools, which is often the earliest visible sign.
5. **Cost per request** — usually drift in disguise, because more steps means more tokens.
6. The cause that surprises people is **provider-side**: a model behind a stable version string is updated, rerouted, or served differently, and you were not told.
7. **Break the assumption you would notice** — nothing in your system changed, no deploy happened, and every operational metric is normal, so there is no event to correlate against.
8. Which is why the model version attribute from note 3 matters: it is how you later prove the change was theirs.
9. Detection is distribution comparison over time against a baseline, which is note 14's aggregates read as a series rather than a snapshot.
10. And the loop closes back to Block 1: a detected drift produces traces, the traces produce cases, and the cases join the golden set — so the golden set grows from production rather than from imagination.

> **Recall:** Name the four kinds of drift and which is usually a symptom of another. · Why is a provider-side change hard to detect specifically? · What closes the loop back to Block 1?

---

## Deferred, deliberately

| Topic | Goes to |
|---|---|
| Golden sets, trajectory evals, pass@k | Block 1 |
| LLM-as-judge, calibration, error analysis method | Block 3 |
| Prompt caching mechanics, routing economics | Block 5 |
| Retrieval-specific spans and RAG metrics | Blocks 7-8 |

---

## Xarvis mapping

**Filled after learning, not before.** Each concept lands in **applicable**, **theory-only**, or **parked**.

Going in: Xarvis is unusually strong here — real traffic, real multi-step traces, and a genuine the-logs-did-not-tell-us story. Expect most of this block to be applicable. The known gap is retrieval spans in note 3, since there is no retrieval to trace yet. The known risk is note 8: tracing is currently one LangChain flag pointed at a hosted backend on a personal token, which makes the retention question and the data-residency question in note 11 live rather than academic.

---

## Sources to verify against

- [OpenTelemetry GenAI semantic conventions — status and coverage](https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions)
- [What actually shipped in 2026, and why nothing is stable](https://dev.to/azena-ai/opentelemetrys-genai-semantic-conventions-are-not-stable-yet-heres-what-actually-shipped-in-2026-3mke)
- [State of the GenAI semantic conventions, July 2026](https://john-hodge.com/blog/opentelemetry-genai-semantic-conventions/)
- [Agent observability platform comparison 2026](https://www.digitalapplied.com/blog/agent-observability-platforms-langsmith-langfuse-arize-2026)
- [Platform comparison including self-hosting and free tiers](https://www.marktechpost.com/2026/08/09/top-llm-observability-and-evaluation-platforms-in-2026-langfuse-langsmith-braintrust-arize-and-more-compared/)
- Corpus: `07-evaluation-and-observability/` Q8, Q9, Q13, Q32, Q33, Q40, Q41
