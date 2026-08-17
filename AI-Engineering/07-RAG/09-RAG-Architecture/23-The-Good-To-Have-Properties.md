The eight properties in [[20-Deciding-About-The-Query]] and [[22-Retries-Relevance-And-Verification]] are what an agentic RAG pipeline needs to **function**. Three more are worth having but are not load-bearing. The lecture is explicit that many such properties exist and it discusses three.

---

## 1. Memory, and the context window

The scenario: a user asks a question. Earlier in the same session, in the same conversation, they asked something similar — and when that first query ran, documents were retrieved for it.

If the pipeline maintains **conversational history**, those documents are still there. Recall from [[17-What-Is-An-AI-Agent]] that retrieved documents are part of conversational history, and recall from [[21-Retrieval-As-A-Tool]] that the retriever is a tool — so what is being kept is the **tool results**.

So the agent can decide it does not need to retrieve at all. Retrieving again would only produce **redundant results**: the same documents, fetched a second time, at full cost.

Instead it goes into memory, pulls the documents retrieved earlier, and uses those.

![[AI-Engineering/07-RAG/09-RAG-Architecture/Images/10-Memory-Context-Window.png]]

### Why this is worth doing

The benefit is the **context window** — the size of the context measured in tokens, the maximum amount of context the agent has available.

> [!important] The lecture's phrase for it is that the context window is **very precious**, and you want to save it.
>
> That is the whole argument. Not latency, not the price of an embedding call — the scarce resource is room in the prompt. Every document you fetch redundantly occupies space that something else needed, and unlike money you cannot buy more of it mid-request.

So: use the agent's memory capability to reuse previously retrieved documents in cases where you know the results would be redundant.

---

## 2. Static versus dynamic prompt construction

This one is about the **augmentation** step — where context and query get assembled into the prompt that generation runs on.

Until now that prompt has been a **static template**. Slot in the context, slot in the query, generate.

The alternative: do not build the prompt template in advance. Make building it the agent's job, and have it built **dynamically, based on the current scenario**.

![[AI-Engineering/07-RAG/09-RAG-Architecture/Images/11-Static-Vs-Dynamic.png]]

The lecture's example uses two retrievers — one reading a vector store, one doing web search. A dynamically constructed prompt can then carry two labelled sections:

```
Context from vector store:
  ...

Context from web search:
  ...
```

And once the sections are separate, the prompt can say something about them — for instance instructing the model to **prioritise one source over the other**, which a static template cannot do because it does not know which sources were used.

The same trick applies to the query itself. If the query was rewritten back in [[20-Deciding-About-The-Query]], the prompt can carry both:

```
Original query:
  ...

Rephrased query:
  ...
```

> [!info] The instructor's own summary is that **the combinations here are endless**, which is honest — this is a capability rather than a recipe. The general principle is that a static template has to be written for the worst case and then used for every case, whereas a constructed prompt can describe what actually happened on this particular run.

---

## 3. Graceful fallback

The third good-to-have is a **graceful fallback mechanism**, and its primary purpose is protecting the model from **hallucinations**.

![[AI-Engineering/07-RAG/09-RAG-Architecture/Images/12-Graceful-Fallback.png]]

Consider how retries can go wrong. The pipeline has retry logic, so it performs multiple retries. If you never prompted it for what to do when the retries are exhausted without success, the final response may simply be generated from whatever retrieved documents happen to be lying around — regardless of whether they answer anything.

The mechanism has three named parts:

| Part | What it does |
|---|---|
| **Upper limit** on retry logic | retries must stop somewhere |
| **Guardrails** | constraints on what the pipeline is allowed to produce |
| **Robust error handling** | failures get handled rather than propagated |

On the last: you might retrieve from a particular source and keep getting errors from it, or get no retrieved results at all. Both need handling gracefully rather than being allowed to flow downstream into a confident-sounding answer.

> [!important] Every cyclic architecture in this folder has needed the same brake. `MAX_RETRIES` and `MAX_REWRITE_TRIES` in [[15-The-Retrieval-Rewrite-Loop]] exist for exactly this reason.
>
> What is different here is severity. In Self-RAG the loops were hand-wired, so you knew precisely where they were and could count them. When an **agent** decides how many times to retry and which source to try next, there is no fixed loop to bound — which makes the upper limit more necessary and harder to place.

This is what makes the pipeline **production-ready** and robust. It is filed as good-to-have because a pipeline without it still works; it just does not survive contact with real traffic.

---

## The three, together

| Property | What it protects |
|---|---|
| Memory / context-window management | the context window, by not re-retrieving redundantly |
| Dynamic prompt construction | answer quality, by describing what actually happened |
| Graceful fallback | production behaviour, by bounding retries and handling errors |

---

## Guarantees

**It guarantees** nothing about correctness — none of the three makes an answer more likely to be right. They protect a scarce resource, an opportunity, and a failure mode respectively.

**Memory reuse can be wrong.** Deciding that a new query is similar enough to an old one to reuse its documents is itself a judgement, and reusing stale documents is a failure that looks exactly like a successful retrieval.

**A dynamic prompt is harder to debug.** When the prompt differs per query, a bad answer no longer has a fixed prompt you can inspect — you have to log the prompt that was actually constructed.

---

> [!tip] Interview framing
> **Three good-to-haves. First, memory for context-window management: retrieved documents live in conversational history, and since the retriever is a tool, its results are tool results the agent can go back to — so on a similar follow-up query it reuses them instead of re-retrieving redundant results. The argument is specifically about the context window being a precious, fixed resource, not about latency or cost. Second, dynamic prompt construction — instead of a static augmentation template, the agent builds the prompt for the current scenario, so with two retrievers you get separate labelled sections for vector-store context and web context and can tell the model to prioritise one, which a static template can't because it doesn't know what ran. Third, graceful fallback: an upper limit on retry logic, guardrails, and real error handling, because if retries exhaust without success and you never prompted for that case, the model generates a confident answer from whatever documents are lying around. That last one is more necessary in an agentic pipeline than in Self-RAG, because when the agent decides how many times to retry there's no hand-wired loop left to bound.**
