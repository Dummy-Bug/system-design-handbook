Two architectures in this folder have already fixed real problems with traditional RAG. Corrective RAG checked the documents before generating; Self-RAG checked the answer afterwards. Both made the pipeline better without changing what it fundamentally *is*.

This note is about what remains — and it starts by being fair to the thing being replaced.

---

## Traditional RAG is good at something

Before listing its failures, the honest starting point is that traditional RAG has real advantages, and they are the reason it is still the default.

- **It is simple to implement.** There is no complex decision making anywhere in it, which makes it easy to code, easy to monitor, and easy to reason about when it goes wrong.
- **It is fast.** One retrieval, one generation. Latency is low because there is nothing else in the path.

Every architecture in this folder gives up some of both. That trade should be visible before you make it.

---

## What it cannot do

**It has no control over retrieval.** For every single input, it retrieves. Ask a simple question whose answer the model already knows — the capital of India, what a variable is — and the pipeline still runs a similarity search and still stuffs documents into the prompt.

That is worse than merely wasteful, because of the prompt that traditional RAG uses:

> *Answer the question using only the context below.*

The model **knows** the answer. The prompt forbids it from using what it knows. So it is forced to answer out of a context that was never relevant to the question in the first place.

**It is a dumb pipeline.** The whole flow runs in one fixed sequence, and you cannot change that sequence. Sometimes a query needs rewriting before retrieval. Sometimes a complex query needs breaking into parts, each retrieved separately. Traditional RAG has nowhere to put either. The flow is what it is, for every query, forever.

> [!important] "Dumb" here is a precise claim, not an insult. It means the sequence of steps is **fixed at build time** rather than decided at query time. A pipeline that always does A → B → C is dumb even if A, B and C are each individually sophisticated.

**It never checks its own work.** The response is generated and returned without anything verifying it.

![[AI-Engineering/07-RAG/09-RAG-Architecture/Images/01-Traditional-RAG-Two-Problems.png]]

Two words on that page carry the whole lecture: **control** and **order**. Everything that follows is an attack on one or the other.

---

## What CRAG and Self-RAG already took back

Both earlier architectures bought back a piece of *control*, and neither touched *order*.

| | What it added | Which problem |
|---|---|---|
| [[01-Why-Corrective-RAG]] | an evaluator scoring retrieved documents for relevance, then filtering and refining what survives | control over **inputs** |
| [[08-Why-Self-RAG]] | checks on whether the answer is grounded, and whether it is useful | control over **outputs** |

That is genuine progress. In both, an LLM makes an active decision partway through, and that decision changes what happens next — which is exactly what traditional RAG could not do.

But look at how the decision gets made. In both architectures the branching is **hand-written by you**. You decided there would be a relevance check. You decided what the thresholds were. You wired which node follows which verdict. The LLM fills in a value; the graph was designed in advance and does not change.

---

## The upgrade

The change is a substitution, and it is worth stating in one line:

> **Agentic RAG is what you get when the pipeline is driven by AI agents instead of by LLMs.**

An LLM answers a question you hand it. An agent decides what to do. Give that difference control over a retrieval pipeline and the consequences compound:

- retrieval from **multiple sources**, chosen per query
- pulling only the important information into the context — knowledge refinement, but decided rather than hardcoded
- the **generation** step stops being a static template and gets assembled to fit the situation
- and the shape of the whole run changes with the query, instead of being the same shape every time

> [!info] Agentic RAG is not a replacement for the previous two architectures — it is built **on top of** them. The instructor is explicit about this: you take the good ideas from Corrective RAG and Self-RAG and reuse them, with an agent deciding when each one applies. The relevance check from CRAG and the grounded/useful checks from Self-RAG both reappear later in this module as properties an agentic pipeline should have.

---

## Guarantees

**It guarantees** that no step of the pipeline has to be fixed in advance — retrieval, its source, its parameters, its ordering, and the prompt can all be decided per query.

**It does not guarantee** any of those decisions are correct. Every one is a model choosing, and a wrong choice early misroutes the entire query.

**It gives up both of traditional RAG's advantages.** The simplicity is gone — this is the most complex architecture in the folder — and so is the latency, because decisions cost model calls before any answer gets generated.

---

> [!tip] Interview framing
> "Traditional RAG has two structural problems: no control over whether retrieval happens, and a fixed order of steps. It retrieves for every query, including ones the model could answer directly — and because the prompt says 'answer only from this context', the model is actively prevented from using what it already knows. Corrective RAG and Self-RAG each buy back some control, one over the retrieved documents and one over the generated answer, but neither touches the ordering, and in both the branching logic is hand-written by the developer. Agentic RAG changes what's driving the pipeline: an agent decides, per query, whether to retrieve, from where, how, and in what order. It doesn't replace CRAG or Self-RAG — it reuses both as capabilities an agent can invoke. The honest cost is that you give up exactly what made traditional RAG attractive: it's no longer simple, and it's no longer fast."
