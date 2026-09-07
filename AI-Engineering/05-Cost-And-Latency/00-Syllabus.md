#ai-engineering #cost #latency #caching #routing #metering #block-5 #syllabus

# Block 5 · Cost and Latency Engineering — Syllabus

**16 notes, 162 rungs.** Generic — the economics and its failure modes, not Xarvis's implementation, which is mapped at the bottom.

> A rung is the **smallest thing that has to be understood before the next thing makes sense** — the cache read costs 10% of input, therefore caching looks free, therefore you check the write price, therefore the write costs a premium, therefore one read loses money and two break even. Rungs are not topics and not section headings. Seven to fourteen of them build one note.
>
> They are ordered so that **each rung either breaks the previous one or is forced by it.** That ordering is the whole design. A list of true statements about cost teaches nothing; a chain where every step is the answer to a problem the last step created is what sticks.

**Why generic first.** Xarvis is single-model and single-provider today, so several concepts here land as **costed proposals** rather than shipped systems. That is a legitimate interview answer when framed honestly, and it is only available if the concept was learned rather than skipped for being inapplicable.

**Three modes, trained differently.** Notes 1 to 3, 5, 6, 10, 11 and 14 are **mechanism** — where the money goes and how the measurement lies — and respond to retrieval, so the rungs are the recall unit. Notes 8, 9, 13 and 16 are **decisions** defended against changed constraints, because their inputs move. Note 12 is **vocabulary only**: you need to speak it in an interview, not build it, and treating it as a project is the trap.

**Currency check (2026-09-06):** The defining paradox holds — token prices fell roughly 80% between 2025 and 2026 while enterprise API spend kept climbing, because unit-cost improvements are consumed by volume growth. So cost engineering is a permanent discipline rather than a cleanup.

The important reframe added this cycle: **BCG puts token cost at only 30 to 40% of total AI implementation spend**, with the other 60 to 70% in integration, engineering and governance. Everything in this block optimises the smaller share, and knowing that is what separates a cost answer from a cost narrative.

Current headline numbers, all provider-verifiable and all worth restating as ranges rather than constants. **Prompt caching is now supported by all three major providers** and bills cached reads at roughly **0.1× the input rate**, so 90% off on a hit — but the cache **write** carries a premium, which makes **break-even two reads**, and that is the number people omit. **Batch APIs run about 50% cheaper** on a 24-hour completion window. **Model routing is the highest-ROI single lever at 40 to 60%**, and the three combined typically reach 60 to 80% for a production application.

Re-verify before relying on any of it: caching mechanics and minimum cacheable length differ per provider, batch availability and window differ per provider, and provider docs are the only authority. A blog restating a discount is not a source.

---

## How to teach from this

**One note per session, rungs in order, never skipping.** A skipped rung breaks the chain — the next one stops being a discovery and becomes a fact to memorise.

**Where a rung says break, it is run, not read.** Sending the same prefix twice and reading the two bills produces a problem the fix attaches to. Reading that caching saves 90% produces a number you will quote wrongly.

**Recall is per note, from memory, file closed.** Recognising an answer does not count.

**Notes 8, 9, 13 and 16 are not recall material.** Re-argue them when a price changes, a model ships, or the volume moves an order of magnitude. A position you can only recite is not a position.

**Measure before optimising, and note 5 is the gate.** Every lever below it is worthless without a per-request number to compare against, and the most common failure in this whole block is optimising an unmeasured system and reporting the saving from a spreadsheet.

**Three rabbit holes are marked and binding** — serving-engine implementation in note 12, tokenizer and BPE internals in note 1, and GPU capacity mathematics in note 13. All three are deep and none is asked of an API consumer.

**Spacing:** re-test notes 1 to 5 after finishing note 11, and the levers once one is actually shipped and its saving measured.

**The syllabus governs the numbering — never the source material.** A lecture covering concept 7 becomes `07-*.md`, whatever order it appeared in. Gaps are concepts not yet reached, not missing files.

---

# A · Where The Money And The Milliseconds Go

## Note 1 · Token Economics

11 rungs. **Break:** count the tokens in one real request of yours, then multiply by requests per day.

1. Models are billed per token, and a token is roughly three-quarters of a word for English prose.
2. Input and output are priced **separately**, and output costs several times more.
3. The asymmetry is not arbitrary pricing — it follows from note 2's mechanics, and it is the single most useful thing to know before optimising anything.
4. Which means a request producing 200 tokens from a 5,000-token prompt and one producing 5,000 from 200 are not comparably priced, even though both move 5,200 tokens.
5. **Break the instinct to shorten prompts first** — for a chat product the output side is usually the cheaper thing to cut, and it is cut with an instruction rather than an engineering project.
6. The back-of-envelope is requests per day × tokens per request × price per token, and doing it once changes what you work on.
7. Because the result is usually either trivially small, in which case stop, or dominated by one endpoint, in which case go there.
8. Tokens are also the unit of **latency**, not only cost, which is why this block pairs the two rather than splitting them.
9. **An unattributed bill is an unfixable bill** — a single monthly number names no endpoint, no tenant, and no change to make.
10. So attribution is a prerequisite rather than a refinement, and it is built in Block 2 rather than here.
11. Reasoning models add a third category, tokens generated and discarded before the answer, billed as output and invisible in the response — so the count you are charged for is not the count you can see.

> **Recall:** Why does output cost more, and where is the mechanism explained? · State the back-of-envelope and what its two typical outcomes are. · What is billed but not visible in a reasoning model's response?
>
> **Stop:** No tokenizer internals or BPE derivations. Rabbit hole, marked, binding.

## Note 2 · Prefill Versus Decode

10 rungs. **Break:** send a 10,000-token prompt asking for 10 tokens out, then a 100-token prompt asking for 1,000 out. Compare cost and wall-clock time.

1. Generating a response has two phases with different physics, and nearly every serving decision follows from the difference.
2. **Prefill** processes the whole prompt to build internal state, and it is **parallel** — all input tokens are handled together.
3. That makes prefill **compute-bound**: it is limited by arithmetic throughput, and it scales well with better hardware.
4. **Decode** produces the answer one token at a time, each conditioned on the last, so it is **strictly sequential** and cannot be parallelised within one request.
5. It is also **memory-bandwidth-bound**: each token requires reading the model weights and the growing cache, so the limit is moving bytes rather than doing arithmetic.
6. **Which explains the price asymmetry from note 1** — an output token consumes a full pass over the weights, an input token shares one.
7. It also explains what batching can and cannot do: batching many requests amortises the weight read across them, so it helps decode enormously and prefill much less.
8. **Break the assumption that a faster GPU fixes slow generation** — decode is waiting on memory bandwidth, so more compute does close to nothing.
9. The two phases also map cleanly onto the two latency numbers: prefill governs time to first token, decode governs the rest.
10. Which is why a long prompt hurts responsiveness and a long answer hurts throughput, and they are fixed by different levers.

> **Recall:** Which phase is parallel and which is sequential, and what is each bound by? · Why does batching help one phase far more than the other? · Map each phase onto a latency metric.

## Note 3 · The Latency Vocabulary

9 rungs. **Break:** measure time to first token and total time on the same call, and compare their ratio at two output lengths.

1. Total latency is one number and it hides the thing users actually feel.
2. **Time to first token** is the wait before anything appears, governed by prefill plus queueing.
3. **Time per output token**, also called inter-token latency, is how fast the answer reads once it starts.
4. Which gives the working model: total is roughly time to first token plus time per output token times output length.
5. **Break the single-number habit** — two systems with identical totals feel completely different if one has a 300ms first token and the other a 6-second one.
6. So a chat product optimises time to first token, and a batch pipeline optimises tokens per second, and they are different systems.
7. Report **p99** rather than the mean, because tail latency is what generates complaints and averages conceal it entirely.
8. In LLM serving the tail is usually queueing under load, a retry, or a slow tool call — not the model being slow.
9. Which is the practical point of the vocabulary: naming the stage tells you which of those it was.

> **Recall:** State the total-latency decomposition. · Which metric does a chat product optimise and which does a batch pipeline? · What actually causes the tail?

## Note 4 · Perceived Versus Actual Latency

8 rungs. No break — this is framing, and Block 8 runs the experiments.

1. Streaming sends the answer as it is produced rather than at the end.
2. It does not reduce total time by a single millisecond.
3. What changes is time to first token as **experienced**, which drops from the whole generation to a few hundred milliseconds.
4. That is a genuine improvement, because the user's question is am I being ignored, and the first token answers it.
5. **Break it** — streaming is a lie in exactly one place: when the system is thinking before it has anything to say, which for an agent is the tool-calling stretch.
6. During that stretch nothing streams, and the user is back to the blank spinner with a longer wait than a non-agentic product would have had.
7. Which is why progress events exist and why they are a cost concept rather than only a UX one: they are what makes a multi-second tool call survivable.
8. Honest targets differ by product — a chat product needs a first token under a second; an agent loop needs visible progress at least every few seconds, which is a weaker and more achievable promise.

> **Recall:** What does streaming change and what does it not? · Where exactly is streaming a lie? · Why is the agent target stated as progress rather than latency?

## Note 5 · Per-Request P&L

12 rungs. **Break:** cancel a stream mid-answer, then check whether those tokens were billed to anyone. This is the gate for the whole block.

1. Optimising without a per-request number means comparing a guess to a guess.
2. So the first deliverable is the cost of one request, end to end.
3. End to end means every model call in the loop, not the last one — an agent that thinks four times is billed four times.
4. Plus tool calls that themselves call models, plus retrieval, plus embeddings.
5. **Plus retries**, which are the line people omit and which multiply everything above them.
6. Summing gives cost per conversation, and grouping by attribute gives cost per feature, per tenant, per user.
7. **Break it** — a client that disconnects mid-answer has already spent the tokens, and if metering happens at the end of the response, that spend is never recorded.
8. Which makes cancellation a **billing** problem rather than only a stream-lifecycle one: the tokens are owed whether or not anyone is listening.
9. And it has a specific engineering shape, because the usual place to write usage is a request-scoped database session that dies with the cancelled request.
10. So the write needs a fresh session and has to be shielded from the cancellation, or you get lost billing data and idle transactions holding row locks.
11. That is the highest-value story in this block, because it sits exactly where streaming, cancellation and persistence meet, and almost nobody has hit it.
12. The output of the note is one number per request that someone can act on, and every lever below is measured against it.

> **Recall:** Name the five components of an end-to-end request cost, and which is usually omitted. · Why does a cancelled stream still owe tokens? · What breaks if you write usage on the request-scoped session?

---

# B · The Levers

## Note 6 · Prompt And Prefix Caching

13 rungs. **Break:** send the same 3,000-token prefix twice and compare the bills. Then change one character at the very front and send it again.

1. Every request reprocesses the whole prompt from scratch, including the parts that never change.
2. For an agent that is a large fixed block — persona, instructions, tool definitions, examples — rebuilt on every single turn.
3. Prefix caching stores the **processed internal state** of a stable prefix so subsequent requests skip the work.
4. All three major providers support it in 2026, so this is a portable technique rather than a vendor feature.
5. A cache read costs roughly **0.1× the input rate**, which is the 90% figure everyone quotes.
6. **Break the conclusion that it is free money** — writing to the cache costs a **premium** over normal input, so a prefix cached and read once **loses**.
7. Break-even is **two reads**, and every read beyond that is 90% off. That is the number to quote, and quoting only the 90% is how people get caught.
8. Which means the technique fits repeated-prefix workloads and not one-shot ones, and knowing which you have is the whole decision.
9. Caching is **prefix-matched from the very start of the prompt**, so a single changed character at position zero invalidates everything after it.
10. Which forces prompt **ordering** as a design constraint: fixed instructions first, volatile content last.
11. And it makes a timestamp near the top of a system prompt one of the most expensive characters in a codebase.
12. Two provider-specific mechanics that must be checked rather than assumed: the **minimum cacheable length**, below which nothing is cached silently, and the **time to live**, after which the entry is gone.
13. The metric that says whether it is working is **cache hit rate**, which means it has to be on the span, which is Block 2 note 3 doing real work.

> **Recall:** Why is break-even two reads rather than one? · What does prefix matching force about prompt ordering? · Name the two provider-specific mechanics that must be verified. · Which metric tells you it is working?

## Note 7 · Semantic Caching

9 rungs. **Break:** query the cache with a paraphrase that means the opposite, and see what comes back.

1. Prefix caching saves reprocessing; the model still runs.
2. Semantic caching skips the model entirely by returning a stored answer for a **similar** question.
3. Similar rather than identical is the whole idea and the whole danger.
4. Implementation is an embedding of the query, a vector search over past queries, and a similarity threshold.
5. **Break it** — set the threshold loosely and what is my leave balance matches what is his leave balance, and the wrong person's answer is served.
6. Which is not a cache miss, it is a **data breach**, and it is why semantic caching in a multi-tenant system must be keyed by identity as well as meaning.
7. Set the threshold tightly instead and the hit rate collapses to near zero, which is the honest common outcome.
8. **Staleness** is the second failure: a cached answer about a record that has since changed is confidently wrong with no error anywhere.
9. So the technique fits stable, non-personalised, high-repetition content — documentation and policy questions — and fits a personalised data assistant badly.

> **Recall:** How does it differ from prefix caching in what it skips? · Why is a loose threshold a security problem rather than a quality one? · What shape of workload does it actually fit?

## Note 8 · Model Routing And Tiering

11 rungs. **Break:** take 50 real requests, run them on the cheap model and the frontier model, and count how many differ in a way anyone would notice. Decision note.

1. Most requests do not need the best model, and paying frontier prices for all of them is the usual largest single overspend.
2. Routing sends a cheap model first and escalates only when needed, and it is the highest-ROI single lever at roughly 40 to 60%.
3. The design question is entirely **what triggers escalation**, and there are four answers.
4. **Heuristic** — request length, presence of tool calls, endpoint. Free, crude, and often enough.
5. **Task type** — a classifier over intent, which requires knowing your intents and is a natural fit where a router already exists.
6. **Confidence** — run the cheap model, judge whether the answer is good enough, escalate if not.
7. **Break it** — confidence routing pays for the cheap call **plus** the judge **plus** sometimes the expensive call, so on a hard workload it costs more than always using the frontier model.
8. Which makes the escalation rate the number that decides viability, and it has to be measured rather than assumed.
9. **Cascade** — cheap, then better, then best, which compounds the same risk across more stages.
10. Whatever the trigger, the saving is only defensible with a measured **quality delta per tier**, and producing that delta is a Block 1 job.
11. So routing is not a cost project that touches evals, it is an eval project that produces a cost saving, and running it the other way around is how quality regressions ship as wins.

> **Position to defend:** Name the four triggers and the failure mode of the third. · What number decides whether confidence routing is viable? · Why is routing an eval project?

## Note 9 · Prompt Compression And Context Management

10 rungs. **Break:** trim conversation history to the last three turns and count what the agent forgets. Decision note.

1. Input tokens are the other half of the bill, and in a long conversation they grow without bound.
2. Because every turn resends the whole history, so turn twenty pays for turns one through nineteen again.
3. Which makes context growth quadratic in a conversation, and it is the reason long chats get expensive rather than the model getting slower.
4. Four levers, in ascending order of risk. **Trimming** — drop the oldest turns.
5. **Summarising** — replace old turns with a generated summary, which costs a model call to save model calls.
6. **Dropping low-value retrieved chunks** — send five instead of twenty, which is where retrieval quality and cost meet.
7. **Compacting tool outputs** — a tool returning a 4,000-token JSON blob when the model needs three fields is pure waste, and this is usually the cheapest real win.
8. **Break it** — compress the wrong thing and the agent loses the constraint stated in turn two, then confidently violates it in turn twenty.
9. That failure is invisible in aggregate metrics and shows up as a quality complaint nobody can reproduce, which is why compression is a decision note rather than a mechanism note.
10. The rule that survives: compress **machine-generated** context aggressively and **user-stated** context reluctantly, because the user said it once and will not say it again.

> **Position to defend:** Why does conversation cost grow quadratically? · Order the four levers by risk and say why. · State the rule for what is safe to compress.

## Note 10 · Output Length Control

8 rungs. **Break:** ask the same question with and without a brevity instruction, and compare tokens and quality.

1. Output tokens cost several times input tokens, so the output side has the best ratio of saving to effort.
2. And it is usually reachable with an instruction rather than an engineering change, which makes it the first thing to try.
3. **Max tokens** is the hard stop, and it is a truncation rather than a summary — the answer stops mid-sentence.
4. So it is a safety net against runaway generation, not a length strategy.
5. Instruction-level brevity is the actual lever, and it works better when it names a form than when it names a number.
6. **Break it** — asking for under 100 words is followed unreliably, while asking for three bullet points is followed well, because form is checkable by the model and word count is not.
7. **Structured output** is the strongest version of the same idea: a schema constrains length as a side effect of constraining shape.
8. **Stop sequences** handle the tail case where the model would continue past the useful answer into commentary nobody reads.

> **Recall:** Why is output the best ratio of saving to effort? · What is max tokens actually for? · Why does naming a form beat naming a word count?

## Note 11 · Batch APIs And Async Patterns

8 rungs. **Break:** find one workload of yours where nobody is waiting, and price it both ways.

1. Interactive pricing pays for capacity held ready to answer immediately.
2. Not all work is interactive: evaluation runs, backfills, summarising yesterday's conversations, generating embeddings.
3. Batch endpoints trade latency for price — roughly **50% cheaper** on a 24-hour completion window at the major providers.
4. **Break the assumption that this is a niche** — an eval suite from Block 1 is exactly this shape, and running it interactively is paying double for a wait nobody experiences.
5. The design consequence is a queue: submit, poll or receive a callback, store results, and handle partial failure across a batch.
6. Which means batch is an architectural choice made early rather than a flag flipped late.
7. **Break it the other way** — anything a user is waiting on cannot be batched regardless of price, and the discount tempts people to try.
8. So the decision rule is one question with no middle ground: is a human waiting for this response.

> **Recall:** What is being traded for the discount? · Name one workload from an earlier block that is exactly this shape. · State the decision rule.

---

# C · Serving-Side Levers

## Note 12 · Serving Internals Worth The Vocabulary

10 rungs. No break. **Vocabulary only — you need to speak this, not build it.**

1. Everything so far treats the model as a priced black box, which is correct for an API consumer.
2. Five terms come up in interviews anyway, and being unable to define them reads as never having thought about serving.
3. **Continuous batching** — new requests join an in-flight batch between token steps rather than waiting for it to finish, which is what makes throughput acceptable given note 2's sequential decode.
4. **KV cache** — the per-request store of attention state that makes each new token cheap; it grows with sequence length and is the real memory constraint on concurrency.
5. Which is the link back to pricing: a long context occupies memory for the whole generation, so context length is a capacity cost and not only a token cost.
6. **PagedAttention** — allocating that cache in fixed pages rather than contiguously, borrowing virtual-memory paging, which removes the fragmentation that otherwise wastes most of the memory.
7. **Quantization** — serving weights at lower precision to fit more model in less memory and move fewer bytes, trading some accuracy for throughput and cost.
8. **Speculative decoding** — a small model drafts several tokens and the large model verifies them in one pass, exploiting that verification is parallel while generation is not.
9. Which is the same prefill-versus-decode asymmetry from note 2 turned into a speedup, and is worth saying that way.
10. The trap is treating this list as a project: for an API-consuming role it earns nothing built and costs a week.

> **Recall:** Define each of the five in one sentence. · Why is KV cache a capacity cost as well as a memory detail? · Which note's asymmetry does speculative decoding exploit?
>
> **Stop:** No engine internals, no vLLM source, no benchmarking. Rabbit hole, marked, binding.

## Note 13 · Self-Host Versus API — The Decision

10 rungs. Decision note. **Break:** compute your break-even volume before arguing either side.

1. The instinct at scale is that hosting your own model must be cheaper.
2. Sometimes it is, and the honest version requires five inputs rather than one.
3. **Volume** — self-hosting is a fixed cost against a per-token one, so there is a break-even and it is usually higher than people expect.
4. Below it the API wins outright; above it the comparison becomes real.
5. **Utilisation** is the input that decides whether the break-even is even meaningful — a GPU idle at night is billed all night, so bursty traffic pushes break-even much higher.
6. **Data sensitivity** — if prompts cannot leave your infrastructure, this stops being an economics question and the answer is decided.
7. Which is the same first-question logic as Block 2 note 11, and worth noticing as a pattern rather than a coincidence.
8. **Latency control** — your own hardware means no shared queue and no provider-side rerouting, which matters for a strict tail target.
9. **Ops burden** — someone now owns capacity, upgrades, incidents and a scaling story, and that person's time is the cost nobody puts in the spreadsheet.
10. **Fine-tuning** flips it hardest: serving a fine-tuned model is where self-hosting stops being an optimisation and becomes the only option.

> **Position to defend:** Name the five inputs. · Which one can make the economics irrelevant, and why? · What flips the decision hardest?
>
> **Stop:** No GPU capacity mathematics or fleet sizing. Rabbit hole, marked, binding.

---

# D · Governance

## Note 14 · Budgets, Quotas, And Rate Limits

14 rungs. **Break:** send two concurrent requests against one counter and watch both pass a limit of one.

1. Optimising average cost does nothing about the request that costs a thousand times the average.
2. An agent loop with no cap can call a model until something stops it, and the thing that stops it should not be the invoice.
3. So every agent needs a **per-task token budget**, which is a different control from a per-user rate limit and is the one usually missing.
4. Rate limiting has three standard algorithms and the differences matter.
5. **Fixed window** — count requests per calendar minute, reset at the boundary. Trivial to implement.
6. **Break it** — a user can spend the whole allowance at 10:59:59 and the whole next one at 11:00:00, delivering double the limit in two seconds.
7. **Sliding window** — count over the trailing period rather than a calendar block, which removes the boundary burst at the cost of storing timestamps.
8. **Token bucket** — a bucket refills at a steady rate and each request removes one; empty means rejected.
9. Which is the one that permits a deliberate **burst** up to the bucket size while bounding the sustained rate, and that is usually what you actually want.
10. **The counter is where it breaks in production** — read, compare, increment is three operations, and two concurrent requests interleave them and both pass.
11. So the operation has to be **atomic**, which is why these counters live in Redis rather than in a process dictionary once there is more than one worker.
12. An in-process counter is correct only on a single process, and the failure is silent: the limit simply becomes per-worker.
13. Quota **windows** are a separate concept from rate limits — weekly and monthly caps with resets, measured in tokens or money rather than requests.
14. And the hard case is a quota crossed **mid-stream**: the response has already returned 200, so there is no status code left to reject with, and the only honest options are to finish the turn and bill it or to terminate with an in-band error frame.

> **Recall:** Name the three rate-limit algorithms and the specific attack on the first. · What does a token bucket permit that a sliding window does not? · Why must the counter be atomic, and what is the silent failure? · What are the two options when a quota is crossed mid-stream?

## Note 15 · Cost Observability And Anomaly Detection

9 rungs. **Break:** find the last time cost per request changed by more than 20%, and how you would have known.

1. A monthly invoice is a lagging indicator by up to thirty days.
2. Which means a regression shipped on the 2nd is discovered on the 1st of the following month, after it has been paid for.
3. So the metric to watch is **cost per request**, not total spend.
4. Because total spend rises with traffic, and a rising bill on rising traffic is not a problem while a rising bill on flat traffic is.
5. **Break it** — alerting on total spend produces a page every time marketing runs a campaign, and the alert gets muted before it ever catches a real regression.
6. The regressions worth catching are specific and each has a shape: a prompt that grew, a retry loop that started firing, a cache hit rate that collapsed, a routing rule that stopped escalating correctly.
7. Cache hit rate deserves its own alert, because it can fall to zero from a one-character prompt edit and nothing else changes.
8. Attribution has to be by tenant and by feature, or the alert says costs went up and names nothing to fix.
9. Which is Block 2's plumbing again — none of this exists without the token counts on the span.

> **Recall:** Why cost per request rather than total spend? · What happens to a total-spend alert over time? · Name the four regression shapes and which one has an obvious single cause.

## Note 16 · Running A Cost-Engineering Programme

10 rungs. Decision note. No break — this is sequencing.

1. Having many levers is not a plan, and applying them in the wrong order wastes the cheap ones.
2. The first cut is **quality-neutral versus quality-trading**.
3. Quality-neutral: prefix caching, batching, output-length control by form, compacting tool outputs. These cost only engineering time.
4. Quality-trading: routing, compression, smaller models, aggressive history trimming. These buy money with accuracy.
5. **Exhaust the neutral ones first**, always, because a neutral saving needs no eval to defend and a trading one does.
6. Which also means the eval suite from Block 1 is a **prerequisite** for the second half of the list rather than a nice companion to it.
7. Sequence within each group by return per unit effort, and the honest ranking usually puts caching and output control above everything.
8. Measure each lever against the note 5 baseline **individually**, because shipping three at once produces one number and no attribution.
9. **Break the assumption that the programme ends** — prices change, traffic grows, models ship, and a system optimised in March is unoptimised by September.
10. Capacity planning closes it: from a peak requests-per-second target and a per-request cost, to a monthly figure someone can approve before it is spent rather than after.

> **Position to defend:** State the first cut and why it decides the order. · Which block becomes a prerequisite, and for which half? · Why measure levers individually?

---

## Deferred, deliberately

| Topic | Goes to |
|---|---|
| Cost attribution **plumbing** — spans, token capture, per-tenant propagation | Block 2 |
| Retries, timeouts, backoff, and circuit breakers | Block 6 note 11 |
| Denial-of-wallet as a security control | Block 4 |
| Compounding-error and step-count economics of agents | Block 6 |
| Retrieval-side cost — embedding, index, rerank | Blocks 7-8 |

The circuit breaker is deliberately **not** here. It solves a different failure from a rate limit — a limit protects you from a caller, a breaker protects you from a dependency — and conflating them is a common interview stumble. Learn them apart, then note that a 429 is not a 500 and that retry and breaker answer opposite problems.

---

## Xarvis mapping

**Filled after learning, not before.** Each concept lands in **applicable**, **theory-only**, or **parked**.

Going in — this block has real money attached and one obvious win:

- **Applicable and high-value:** prefix caching (6). A large system prompt — persona, shared system content, time context — is rebuilt every turn and cached nowhere. Check where the volatile part sits in the ordering before estimating the saving, per rung 9. Also output-length control (10), token budgets and quota windows (14), latency measurement (3), and per-request P&L (5).
- **The story worth having:** the cancellation-billing case in note 5. It sits where streaming, cancellation and persistence meet, it is real in this system, and almost nobody has hit it.
- **Costed proposal, not shipped:** routing (8) — single-model today, so this becomes here is the frontier I measured and what I would have chosen.
- **Theory-only:** serving internals (12) and self-host economics (13) — this is an API consumer.
- **Parked:** semantic caching (7), which fits the retrieval product and fits a personalised HR assistant badly, for the reason in rung 6.

---

## Sources to verify against

- [Prompt caching in 2026 — mechanics and break-even](https://devtoollab.com/blog/prompt-caching-guide)
- [LLM cost optimization 2026 — routing, caching, batching](https://www.maviklabs.com/blog/llm-cost-optimization-2026)
- [Five levers and their measured ranges](https://www.morphllm.com/llm-cost-optimization)
- [LLM API pricing comparison, September 2026](https://costgoat.com/compare/llm-api)
- Provider docs are the only authority on caching mechanics, minimum cacheable length, time to live, and batch discounts. A blog restating a percentage is not a source.
- Corpus: `08-inference-and-production/` Q1-Q3, Q6, Q9, Q14-Q15, Q21, Q24-Q26, Q35-Q36, Q42
