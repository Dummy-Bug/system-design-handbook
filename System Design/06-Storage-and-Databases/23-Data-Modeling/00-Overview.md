# Data Modeling — Overview

> [!info] Why this matters
> Data modeling is where interviewers judge whether you actually understand the system. Anyone can say "use Cassandra" — but can you design the schema, pick the right indexes, and explain why? The data model section of a case study is where strong candidates separate themselves.

---

## The core principle

**Schema serves the queries — not the other way around.**

Don't design tables and then figure out how to query them. Figure out what queries you need first, then design the schema to serve those queries efficiently.

---

## The 4-step process

```
Step 1 → nouns from requirements    → entities (what things exist?)
Step 2 → verbs from requirements    → relationships (how do they connect?)
Step 3 → access patterns            → what queries must the schema serve?
Step 4 → schema                     → tables, indexes, denormalization decisions
```

Never skip to step 4. Interviewers watch for candidates who jump straight to schema without establishing entities, relationships, and access patterns first.

---

## Files in this folder

| File | What it covers |
|---|---|
| `01-The-Process.md` | The 4-step framework in detail |
| `02-Entities-And-Relationships.md` | Extracting entities, mapping relationships, junction tables |
| `03-Access-Patterns.md` | Why access patterns drive everything — indexes, embedding, partition keys |
| `04-Instagram-Schema.md` | Full schema walkthrough — users, posts, follows, likes, comments, feed |
| `05-Red-Flags.md` | Common mistakes interviewers watch for |
