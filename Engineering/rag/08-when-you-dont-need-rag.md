#rag #graph #structured-retrieval #cold-start #decision

---

# When Is Graph Traversal Alone Enough — No RAG Needed?

A school district is building a recommendation system. When a new school joins the network, the system should suggest which curriculum categories to enable — Lab Sciences, Mathematics, Languages, Sports, Arts. The team's first instinct is Graph RAG. But before building it, they look at their data — and realize there is no free text to search at all.

---

## What Does the Data Actually Look Like?

Every school in the network is described in fully structured fields:

| Field | Type | Example |
|---|---|---|
| Board | Enum | CBSE, ICSE, IB, State |
| Size | Bucket | small (<500), mid (500-2000), large (2000+) |
| Stage | Enum | new, established, legacy |
| Streams offered | Set of enums | Science, Commerce, Humanities |
| Categories selected | Set of enums | Lab Sciences, Mathematics, Languages |

There are no paragraphs. No teacher bios as free text. No school descriptions written by humans. Every entity is either an ID or a known value from a small set.

> [!info] When your knowledge base is fully structured, embeddings have nothing to embed. Vector search has nothing to find that an exact match query couldn't find faster.

---

## Why Vector Search Would Add Nothing Here

Vector search exists to handle two problems:
1. Sentences with the same meaning but different words
2. Documents whose content is unstructured prose

Neither exists here. "CBSE" and "ICSE" are not synonyms — they are genuinely different boards, and matching them as "similar" would be wrong. There is no prose to search inside. Every relevant attribute is already a clean, queryable value.

---

## The Cold-Start Question — Naive Version

When a new CBSE school joins, what categories should the system suggest?

First attempt:

```cypher
MATCH (s:School {board: "CBSE"})-[:SELECTED_CATEGORY]->(c:Category)
RETURN c.name, count(*) AS frequency
ORDER BY frequency DESC
```

Returns: *"Most CBSE schools select Mathematics, Languages, Lab Sciences..."*

It works, but the answer is so broad it is almost useless. A 200-student new school does not need the same category mix as a 5,000-student legacy institution — even if both are CBSE.

---

## Why One Dimension Is Not Enough

Board alone hides the variation that actually drives category choice.

| Attribute | What it predicts |
|---|---|
| Board | The official curriculum framework — but not the depth or breadth |
| Size | How many categories the school can run at all — small schools cannot staff every subject lab |
| Stage | Tier of resources within each category — new schools use basic lab kits, legacy schools use advanced ones |
| Streams offered | Which categories are even relevant — a Commerce-only school does not need Lab Sciences |

You need at least three of these together before the recommendation becomes precise.

---

## The Multi-Dimensional Match

```cypher
MATCH (s:School)
WHERE s.board = "CBSE"
  AND s.size_bucket = "mid"
  AND s.stage = "established"
MATCH (s)-[:OFFERS_STREAM]->(:Stream {name: "Science"})
      -[:SELECTED_CATEGORY]->(c:Category)
RETURN c.name, count(*) AS frequency
ORDER BY frequency DESC
```

Read in plain English: *"For mid-sized established CBSE schools that offer the Science stream, what categories do they typically select?"*

Four discrete dimensions, all structured, all native to Cypher. No embeddings, no ANN, no LLM extraction — just edge traversal with attribute filters.

---

## What This Architecture Actually Is

This is **retrieval + generation**, but the retrieval is graph traversal, not vector similarity. The LLM still uses the retrieved context to generate a tailored recommendation — it just receives structured facts instead of fuzzy chunks.

```
Cypher returns structured patterns (category frequencies, similar schools)
        ↓
LLM receives [new school profile + retrieved patterns] in prompt
        ↓
LLM generates a tailored category proposal
```

This is sometimes called **Graph-Augmented Generation** to distinguish it from Graph RAG. It is not RAG in the academic sense — there is no vector layer.

> [!important] Graph + LLM (no vectors) is a valid third path between Flat RAG and Graph RAG. When your data is fully structured, this path is cleaner, faster, and more deterministic than either.

---

## When Would This Stop Being Enough?

Add a vector layer the day you introduce:

| New data | Why vectors help |
|---|---|
| Free-text teacher feedback per term | Cannot match feedback semantics with enums |
| School mission statements | "Holistic education" and "well-rounded development" mean the same thing — exact match fails |
| Custom curriculum notes | Unstructured prose that needs semantic search |
| Cross-board role matching | "Head of Department" vs "Senior Master" vs "Subject Lead" all mean similar things |

Until those exist, vector search is overhead.

---

## Mental Model To Remember

> [!info] Flat RAG indexes meaning. Graph RAG indexes meaning *and* structure. Pure graph indexes structure alone — and when your world is structured all the way down, that is exactly enough. Embeddings only earn their place when there is unstructured text that exact matching cannot reach.
