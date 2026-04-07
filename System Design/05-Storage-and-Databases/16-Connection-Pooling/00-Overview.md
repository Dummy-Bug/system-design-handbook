# Connection Pooling — Overview

> [!info] Opening a database connection is expensive — TCP handshake, TLS negotiation, authentication, memory allocation. At high concurrency, paying that cost on every request kills your DB. A connection pool pays that cost once at startup and reuses connections across thousands of requests.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Cost-Of-A-Connection.md | What actually happens when you open a DB connection — TCP, TLS, auth, memory |
| 02-Connection-Pool.md | How pooling works, pool sizing, too small vs too large |
| 03-Interview-Cheatsheet.md | Quick reference for revision |

---

## The one-line model

```
Without pooling:  every request → open connection → query → close connection  (~6-10ms overhead)
With pooling:     startup → open N connections → every request borrows one → returns it → reused
```

---

## When to mention in interviews

Any time the DB becomes a bottleneck under high concurrency. If an interviewer asks "how do you handle 10,000 concurrent users hitting the DB?" — connection pooling is part of the answer alongside read replicas and caching.
