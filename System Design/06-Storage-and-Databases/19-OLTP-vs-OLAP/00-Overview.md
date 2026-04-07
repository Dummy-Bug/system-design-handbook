# OLTP vs OLAP — Overview

> [!info] The core idea
> OLTP and OLAP are two fundamentally different types of database workloads. OLTP serves your live users — fast, small operations. OLAP serves your analysts — slow, massive scans. They cannot share the same database at scale.

---

## Why this matters

Every production system eventually needs two things:

1. A database that serves live users — fast reads and writes, low latency, thousands of operations per second.
2. A way to answer business questions — how many users signed up this month? Which country has the highest engagement? What's the daily active user trend?

The instinct is to run both on the same database. At small scale, that works. At millions of users, it becomes catastrophic — a single analytics query scanning 500 million rows can freeze your production database and take down the live app.

The solution is to **separate these workloads entirely** — OLTP for live traffic, OLAP for analytics, with a pipeline (CDC or ETL) keeping the warehouse fed.

---

## The full architecture

```
Live users
    ↓
OLTP DB (PostgreSQL)     ← row-oriented, fast for single row ops
    ↓  CDC (real-time) or ETL (batch)
Kafka
    ↓
OLAP DB (BigQuery)       ← column-oriented, fast for full column scans
    ↑
Analysts / dashboards
```

---

## Files in this folder

| File | What it covers |
|---|---|
| `01-The-Problem.md` | Why mixing analytics with live traffic kills production |
| `02-OLTP.md` | What OLTP is, row-oriented storage, examples |
| `03-OLAP.md` | What OLAP is, column-oriented storage, why scans are fast |
| `04-ETL-vs-CDC.md` | How data moves between OLTP and OLAP |
| `05-Interview-Cheatsheet.md` | Quick reference for revision |
