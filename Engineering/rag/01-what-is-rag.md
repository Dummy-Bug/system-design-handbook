#rag #llm #retrieval #context #private-data

---

# Why Can't You Just Ask an LLM About Your School's Rules?

You ask an LLM "what is the leave policy for class 10 students?" It gives you a confident, well-structured answer. But is it correct?

---

## Where Does an LLM's Answer Come From?

From its training data. The model was trained on text from the internet, books, and public sources. It learned patterns, facts, and language from all of that.

So what's the problem?

---

## Two Problems With Training Data Alone

**Problem 1 — It goes stale.**

Training happens once. After that, the model knows nothing new. Ask it about last week's news — it doesn't know. Ask it about a policy updated last month — it doesn't know.

**Problem 2 — Your private context never existed in training data.**

Even if the model was trained on everything public and updated yesterday, it has never seen:

- The school's internal rulebook
- Student records and report cards
- Class-specific syllabi and notes
- Anything that lives behind a login

> [!danger] An LLM trained on all public data still knows nothing about your school. That knowledge never made it into training.

---

## So What Would a Human Expert Do?

If a new teacher didn't know the leave policy, they wouldn't guess. They'd look it up — open the school handbook, find the relevant page, read it, then answer.

The answer comes from two steps:
1. **Find** the relevant information
2. **Use it** to construct an answer

---

## What If We Gave an LLM the Same Ability?

Instead of relying purely on training, what if the system:
1. Took the user's question
2. Searched a document store for relevant content
3. Handed that content to the LLM alongside the question
4. Let the LLM generate an answer *using that context*

That system has a name.

---

## RAG — Retrieval-Augmented Generation

RAG is not a model. It is a **system** — a pipeline that combines two components:

| Component | What it does |
|---|---|
| Retriever | Finds relevant documents from a store |
| Generator (LLM) | Reads those documents + question, produces an answer |

> [!info] RAG is to an LLM what Google Search is to a student. The student doesn't know everything — but they know how to find what they need and then reason over it.

The LLM alone is just one part. RAG is the whole kitchen, not just the chef.

---

## Mental Model To Remember

> [!info] An LLM answers from memory. RAG answers from memory + a library. The retriever is the librarian — it finds the right pages before the LLM ever starts writing.
