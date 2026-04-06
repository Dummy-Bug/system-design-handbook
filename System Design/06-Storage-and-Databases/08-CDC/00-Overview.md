# Change Data Capture (CDC) — Overview

> [!abstract] CDC solves one of the most dangerous problems in distributed systems — keeping multiple systems in sync with your database without ever writing to two systems at once. Every time you have a search index, a cache, or a data warehouse sitting next to your primary DB, CDC is the answer to how they stay consistent.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-What-is-CDC.md | The dual-write problem, how CDC works, Debezium and the WAL |
| 02-Outbox-Pattern.md | The Outbox Pattern — guaranteed event delivery without dual-write |
| 03-Interview-Cheatsheet.md | Exactly when to mention CDC in an interview |

---

## The one-line mental model

Your app only ever writes to one system — your database. CDC watches the database's internal log and streams every change to whoever needs it. Everything else reacts asynchronously.

```
App → DB (one write)
        ↓
      CDC reads WAL
        ↓
      Kafka
     ↙   ↓   ↘
Search Cache Warehouse
```

---

> [!important] CDC is not AI, not intelligent, not interpretation
> It is a mechanical tool that reads the database's binary write-ahead log and converts each entry into a structured JSON event. Nothing more.
