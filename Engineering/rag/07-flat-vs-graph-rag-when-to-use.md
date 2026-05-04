#rag #graph-rag #decision #tradeoffs #architecture

---

# Flat RAG or Graph RAG — How Do You Decide?

Graph RAG sounds smarter. But it's also slower and costlier to build. So when is it actually worth it, and when is flat RAG the right call?

---

## What Is the Dominant Signal in Your Queries?

Every retrieval problem has a dominant signal — the thing that most determines what counts as a "good" answer.

**Content similarity** — *"What does the school's leave policy say?"* The answer is in a document. Find the document. Done.

**Entity relationships** — *"Which teachers does the principal supervise?"* The answer isn't in any one document. It lives in the *connections between* records.

If most queries are content-driven → flat RAG.
If most queries are relationship-driven → graph RAG.
If both → hybrid.

---

## The Decision Heuristic

| Signal | Choose |
|---|---|
| Queries are *"what does X say about Y?"* | Flat RAG |
| Queries are *"who is connected to X?"* or *"what does X's team do?"* | Graph RAG |
| Multi-hop reasoning needed (A → B → C) | Graph RAG |
| Entities are large, distinct, clearly bounded (people, teams, projects) | Graph RAG |
| Knowledge base is mostly free-form prose with few entities | Flat RAG |
| You need both | Hybrid |

> [!info] Don't pick the architecture you find interesting. Pick the architecture your queries demand.

---

## Why Not Always Use Graph RAG?

Three real costs:

**1. Index-time expense.** One LLM call per chunk to extract entities. For a large knowledge base this can mean thousands of dollars and hours of indexing.

**2. Entity resolution complexity.** Duplicate or fragmented nodes silently break traversal. Maintaining a clean graph requires ongoing engineering.

**3. Operational complexity.** You're now running a graph store *and* a vector store, keeping them in sync, and writing hybrid queries that combine traversal + similarity.

For small knowledge bases or content-dominant queries, the upgrade is pure overhead.

> [!warning] Graph RAG is not a free upgrade. It is a more powerful retrieval tool that costs more to build and operate. Use it where the power is needed.

---

## A Concrete Example — School Assistant MVP vs. School District Scale

**Scenario A — Single school, MVP.**

You have a school handbook, a teacher directory, and class schedules. The assistant answers questions like:
- *"What is the leave policy?"* (content)
- *"What are the school timings?"* (content)
- *"Who is the head of science?"* (lookup, but in one document)

A small number of entities. Most queries are content-driven. Flat RAG with last-N retrieval (or simple similarity) is enough.

**Scenario B — School district, 50 schools, 5,000 staff.**

The assistant answers things like:
- *"List all the science teachers in north zone schools."*
- *"For schools where Ms. Kapoor previously worked, what curriculum did she introduce?"*
- *"Which principals supervised the same teachers as Mr. Sharma?"*

These are multi-hop, relationship-heavy queries. Flat RAG would either return the wrong documents or stuff thousands of irrelevant chunks into the prompt.

> [!important] Scale changes the answer. At single-school scale, "engineer" means one toolkit. At district scale, *which school* and *which zone* matter more than *which subject* — and that's structural information a graph captures and embeddings flatten.

---

## The Migration Path

You don't have to choose forever. A common path:

1. **Start flat.** Most products don't need a graph until they outgrow it.
2. **Watch the failure modes.** When users start asking relationship questions and getting bad answers, that's the signal.
3. **Add a graph layer later.** Begin with the highest-value entities and relationships. You don't need to graph everything — just the parts where queries care about structure.

> [!info] Premature Graph RAG is a tax. Late Graph RAG is a refactor. The middle path — flat now, graph when you feel the pain — is almost always the right call.

---

## Mental Model To Remember

> [!info] Flat RAG is a search engine. Graph RAG is a search engine *plus* an org chart. Use the search engine when you need to find content. Add the org chart only when "who is connected to whom" is the question your users actually ask.
