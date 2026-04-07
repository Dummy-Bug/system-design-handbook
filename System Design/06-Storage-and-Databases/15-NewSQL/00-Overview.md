# NewSQL — Overview

> [!info] NewSQL is the answer to a specific problem: you need the full guarantees of SQL (ACID, strong consistency, complex transactions) but your system has outgrown what a single database node can handle. NewSQL gives you both — SQL semantics with horizontal scale.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-The-Problem.md | Why Postgres hits a wall globally, and why sharding doesn't fully solve it |
| 02-Spanner-TrueTime.md | How Google solved global time ordering with atomic clocks and GPS |
| 03-Spanner-Transactions.md | How transactions work on top of TrueTime — ordering, conflicts, row locking |
| 04-When-To-Use.md | Decision map — Postgres vs NewSQL vs Cassandra |
| 05-Interview-Cheatsheet.md | Quick reference for revision |

---

## The one-line model

```
Postgres    → full ACID, single node, ~10k-50k TPS ceiling
Cassandra   → massive scale, write-heavy, eventual consistency
NewSQL      → full ACID + horizontal scale + global distribution
```

---

## When to mention in interviews

Global systems where you cannot compromise on consistency — payments, banking, stock trading, booking systems at Google/Amazon scale. Don't reach for it by default. Mention it when the problem is explicitly global + high TPS + strong consistency.

> [!tip] Key names to drop
> - **Google Spanner** — Google interviews, uses TrueTime (atomic clocks + GPS)
> - **Amazon Aurora** — AWS interviews, distributed SQL with storage-compute separation
> - **Azure Cosmos DB** — Microsoft interviews, multi-model with tunable consistency
