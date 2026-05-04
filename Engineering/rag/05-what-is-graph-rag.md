#rag #graph-rag #knowledge-graph #relationships #retrieval

---

# When Does Flat RAG Stop Being Enough?

You have a working RAG system. A student asks "what is the leave policy?" — retrieval finds the right handbook chunk, the LLM answers. Beautiful. Now a different student asks: *"who are all the teachers connected to the science department, and which classes do they handle?"* Retrieval returns... what exactly?

---

## Where Flat RAG Fails

Flat RAG retrieves the **top-K most similar chunks** to a query. That works when the answer lives in one place.

It fails when:

1. **The answer spans many entities.** "All teachers in science department" — each teacher is a separate document. None of them, individually, has high similarity to the query.

2. **The query is about relationships, not content.** "Who reports to the principal?" — this is asking about an *edge between people*, not the meaning of any single document.

3. **Multi-hop reasoning is needed.** "What classes does the principal's science teachers' favourite student attend?" — you have to traverse several connections.

> [!warning] Flat RAG can find documents that *mention* something. It cannot find documents *connected by a relationship* — because it doesn't know what relationships exist.

---

## What Data Structure Captures Relationships?

A graph. Two pieces:

- **Nodes** — entities (a teacher, a student, a class, a department)
- **Edges** — relationships between them ("teaches", "reports to", "member of")

```
[Principal] ──manages──> [Mr. Sharma] ──teaches──> [Class 10A]
                              │
                          mentor_of
                              ↓
                        [Student: Riya]
```

Now ask: "who does the principal indirectly influence?" — just walk the edges. No similarity search needed.

---

## What Is Graph RAG?

Graph RAG is a RAG system where the knowledge base is stored as a **graph of entities and relationships**, not as a flat list of chunks.

At query time, instead of (or in addition to) similarity search, the retriever **traverses edges** to gather context.

> [!info] Flat RAG asks: "what does this query *mean*?" Graph RAG asks: "what is this query *connected to*?"

---

## Does Graph RAG Replace Vector Search?

No — they complement each other. Real Graph RAG systems are **hybrid**.

Consider: *"What did Mr. Sharma's class 10A students say about the last physics exam?"*

- **Graph traversal:** find Mr. Sharma → follow `teaches` edge → get class 10A → get all student nodes
- **Vector similarity:** within those students' feedback documents, find chunks about "physics exam"

| Query Type                                      | Best Tool                             |
| ----------------------------------------------- | ------------------------------------- |
| "What is the leave policy?"                     | Vector (content-driven)               |
| "Who are class 10A's teachers?"                 | Graph traversal (relationship-driven) |
| "What did 10A's teachers say about discipline?" | Graph + Vector hybrid                 |

---

## How Does Hybrid Retrieval Actually Work Step by Step?

Take the query: *"What did 10A's teachers say about discipline?"*

**Step 1 — Graph traversal (find who is relevant)**

```cypher
MATCH (t:Teacher)-[:TEACHES]->(c:Class {name: "10A"})
RETURN t.id, t.name
```

Returns: `[sharma_id, kapoor_id, patel_id]`

No embeddings. Just edge traversal. You now know *exactly* which teachers are relevant.

**Step 2 — Filtered vector search (find what they said)**

```python
vector_db.search(
    query_vector=embed("discipline"),
    filter={"teacher_id": ["sharma_id", "kapoor_id", "patel_id"]},
    top_k=5
)
```

The vector DB runs similarity search, but only against chunks belonging to those 3 teachers. Everything else is ignored.

**Step 3 — Feed to LLM**

The returned chunks go into the prompt alongside the original question. The LLM answers from those chunks only.

```
Cypher → [sharma_id, kapoor_id, patel_id]
              ↓
  Vector search filtered to those 3 IDs
              ↓
       Top-K relevant chunks
              ↓
         LLM → Answer
```

> [!info] The graph narrows down *who* is relevant. The vector search finds *what* they said. Neither alone can answer the question — graph alone has no text, vector alone has no structure.

---

## Why Graph Traversal Wins for Relationship Questions

Two students may have *very similar* embeddings — same age, same class, same subjects. But are they actually connected? Vector similarity can't tell you.

The graph can. *"Riya is in class 10A, taught by Mr. Sharma, mentored by Ms. Kapoor"* — these are facts, encoded as edges. No fuzzy matching, no top-K guessing.

> [!important] Embeddings flatten meaning into proximity in vector space. Graphs preserve the actual structural relationships. When relationships matter, you want the structure, not the proximity.

---

## Mental Model To Remember

> [!info] Flat RAG is a librarian who finds books *about* what you asked. Graph RAG is a librarian who *also* knows which books cite each other, which authors teach the same class, and which chapters reference the same idea — and uses that web of connections to answer.
