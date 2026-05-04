#rag #graph-rag #indexing #entity-extraction #llm

---

# Where Do the Nodes and Edges Actually Come From?

You decided to use Graph RAG. Now you need a graph. But your raw data is unstructured text — a school handbook, teacher profiles, class notes. None of it says "node" or "edge." How do you turn paragraphs into a graph?

---

## What Information Do You Need to Extract?

To build a graph, every chunk of text must be reduced to two things:

1. **Entities** — the things mentioned (people, classes, subjects, departments)
2. **Relationships** — how those entities are connected

Take this paragraph:

> "Ms. Kapoor heads the science department and mentors Riya, a student in class 10A taught by Mr. Sharma."

What entities are in there?

- Ms. Kapoor (Teacher)
- Science Department (Department)
- Riya (Student)
- Class 10A (Class)
- Mr. Sharma (Teacher)

What relationships?

- Ms. Kapoor — `heads` → Science Department
- Ms. Kapoor — `mentors` → Riya
- Riya — `member of` → Class 10A
- Mr. Sharma — `teaches` → Class 10A

That is your graph fragment.

---

## Who Does the Extraction?

You can't write regex to do this — language is too varied. *"Ms. Kapoor heads the science department"* and *"the science department is led by Ms. Kapoor"* mean the same thing. Pattern matching fails.

Only one tool reliably reads unstructured text and outputs structured relationships — an **LLM**.

> [!info] At index time, every chunk gets passed to an LLM with a prompt like: *"Extract all entities and the relationships between them. Return as JSON."* The LLM output becomes graph data.

---

## What Does Index Time Look Like Now?

Compare:

| Step | Flat RAG | Graph RAG |
|---|---|---|
| Chunk documents | ✅ | ✅ |
| Embed each chunk | ✅ | ✅ |
| **LLM extracts entities + relationships** | ❌ | ✅ |
| **Merge into a graph store** | ❌ | ✅ |
| Store in vector DB | ✅ | ✅ (vectors live on nodes) |

The new step — extraction — is what makes Graph RAG expensive.

---

## What Is the Cost?

**One LLM call per chunk, at index time.**

- 10,000 documents × 20 chunks each = 200,000 chunks
- 200,000 LLM calls before answering a single user query
- Each call has latency + token cost

> [!warning] Graph RAG shifts cost from query time to index time. The setup is slow and expensive. Once built, queries can be very fast — but the upfront investment is real.

---

## Entity Resolution — The Hidden Hard Part

The LLM extracts "Ms. Kapoor" from chunk A and "Anjali Kapoor" from chunk B. Same person? The LLM doesn't automatically know.

If you don't merge them, you get two disconnected nodes for the same teacher — and traversal misses half the relationships.

Solutions, roughly in order of sophistication:

1. **Exact name match** — naive, breaks on nicknames and typos
2. **Fuzzy match + manual review** — works for small graphs
3. **Embedding-based merging** — embed each entity name + context, merge if similarity > threshold
4. **Schema-driven IDs** — if the source already has IDs (employee ID, student roll number), use those as the canonical key

> [!danger] Bad entity resolution silently fragments your graph. You'll think traversal is "missing data" — really, the data exists but is split across duplicate nodes.

---

## Where Is the Graph Stored?

Two common shapes:

1. **Dedicated graph DB** — Neo4j, ArangoDB. Optimized for traversal queries (`MATCH (a)-[:teaches]->(b)`).
2. **Hybrid in Postgres** — `pgvector` for embeddings + relational tables for edges. Less specialised, simpler ops.

Each node typically holds:
- A unique ID
- The entity type (Teacher, Class, Department)
- An embedding of its descriptive text
- Metadata

Each edge holds:
- Source node ID
- Target node ID
- Relationship type
- Optional properties (timestamp, weight)

---

## Mental Model To Remember

> [!info] Flat RAG indexes meaning. Graph RAG indexes meaning *and structure*. The LLM is the structure extractor — it reads paragraphs and outputs (entity, relationship, entity) triples that become the spine of your knowledge graph.
