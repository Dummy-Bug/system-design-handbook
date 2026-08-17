# Where RAG Fails — Retriever Failures vs Generator Failures

The pipeline notes so far read like a success story: index once, retrieve by meaning, augment, answer. And when RAG works, that **is** the story. But a system's advantages only mean something next to an honest account of its failure points — and RAG has two components that routinely fail in production. Knowing which two, and how they differ, is what separates **I've read about RAG** from **I've operated RAG.**

The two failure points are the **retriever** and the **generator**.

---

## Failure point 1 — Retriever failure

**What happens:** the retriever fails to fetch the proper context from the knowledge base. The similarity search runs, returns its top-k chunks — and they're the wrong ones. Improper chunks come back; the chunks that actually contain the answer stay in the store, unretrieved.

**Where it comes from:** the **knowledge-base side** of the pipeline. The LLM hasn't even entered the picture yet — the defect is upstream, in what got put in front of it.

**Why it's fatal, not just unfortunate:** everything downstream trusts the retrieved context. Augmentation will faithfully assemble the wrong chunks into the prompt, and the LLM will faithfully answer **from** them. The oldest law of computing applies with full force:

> [!danger] **Garbage in, garbage out.** If the added context is garbage, the response is garbage — no matter how good the LLM is. A perfect generator cannot compensate for a failed retriever, because it answers from what it was given, and it was given the wrong material.

The user experience of a retriever failure: the answer sounds fluent, well-formed... and is about the wrong thing, or confidently reports that the information isn't available while it sits on page 12 of the store.

---

## Failure point 2 — Generator failure

**What happens:** retrieval did its job — the right chunks, containing the actual answer, are sitting in the prompt. But the **LLM fails to use them**. It doesn't properly understand the added context, or ignores it, and generates an **irrelevant response** anyway.

**Where it comes from:** the **LLM side** of the pipeline. The knowledge base and retriever are blameless here — the correct material was delivered; the model fumbled it.

The user experience of a generator failure: same symptom, different autopsy — a wrong or irrelevant answer **despite** the right context having been retrieved.

---

## Same symptom, two different diseases

That's the operational trap: from the outside, both failures look identical — **RAG gave a bad answer.** The split matters because the **fix** lives in different places:

| | **Retriever failure** | **Generator failure** |
|---|---|---|
| What broke | Wrong chunks retrieved | Right chunks retrieved, badly used |
| Which side | Knowledge base / retrieval side | LLM side |
| Context in the prompt | Garbage | Correct |
| The response | Garbage — GIGO | Irrelevant despite good context |

So when a RAG system misbehaves, the first diagnostic question is always: **open the prompt — was the retrieved context right?** Context wrong → work on the retrieval side. Context right, answer wrong → work on the generation side. Skipping that question means fixing the wrong half of the system.

> [!tip] Interview framing — **where does RAG fail?**
> **Two places. Retriever failure — the similarity search brings back improper chunks, so it's garbage in, garbage out regardless of the model; that failure lives on the knowledge-base side. And generator failure — retrieval was correct but the LLM doesn't properly use the added context and answers irrelevantly; that lives on the LLM side. Same symptom for the user, so the first debugging step is checking whether the retrieved context was right — it tells you which half to fix.**

---

These are the fault lines at overview depth — **that** they exist and **where** they live. Why retrievers miss (chunking quality, embedding quality, query phrasing) and how each failure is measured and reduced is exactly what the advanced retrieval and evaluation topics dig into — those get their own notes as the deep dives land.
