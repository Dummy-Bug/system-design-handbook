
> [!info] Stream processing handles events as they arrive in real-time. Batch processing handles data at rest — 
> Huge historical datasets that can't fit in memory and need to be processed across many machines in parallel. When someone says "rebuild the recommendation index from scratch" or "generate this month's billing report", they're describing a batch job, not a stream.

## Stream Processing Isn't Always Enough

Stream processing handles live events as they arrive. But some problems require processing **historical data at rest** — data that already exists, sitting in files or object storage.

Examples:
- "Give me total revenue per user for the last 3 years"
- "Rebuild the recommendation index from scratch after a bug"
- "Generate the monthly billing report for all customers"

You can't stream 3 years of S3 data through Kafka every time someone runs a report. It's slow, expensive, and Kafka isn't designed for random historical access.

---

## The Core Problem

Historical data is **huge and spread across many machines**.

```
S3 / HDFS:
  file-001.log  (1GB)  →  Machine 1
  file-002.log  (1GB)  →  Machine 2
  file-003.log  (1GB)  →  Machine 3
  ...
  file-1000.log (1GB)  →  Machine 1000
```

A single machine can't load 1TB into memory. You need to **bring computation to the data**, not data to the computation.

---

## Batch Processing: The Idea

Instead of moving data to one machine, run computation on each machine **locally** against its own chunk, then aggregate results.

```
Each machine → processes its local file → emits partial result
Framework    → collects all partial results → aggregates → final answer
```

This is the foundation of **MapReduce** — Google's solution to this problem (2004).

---

## When Batch Processing Appears in Interviews

| Scenario | Why Batch |
|----------|-----------|
| **Reconciliation** | Nightly job compares your DB against external source (payments, ad clicks) |
| **Analytics** | Aggregate raw events into hourly/daily rollup tables for dashboards |
| **Reprocessing** | Bug in aggregation logic — replay raw event log to rebuild correct output |
| **Billing reports** | Exact counts required — stream gives approximate, batch gives exact |
| **ML training** | Train models on historical data in bulk |

> [!tip] **Interview framing:** "For the real-time dashboard I'd use stream processing. For the monthly billing report I'd use a batch job — reprocess the raw event log from S3 for exact counts. The stream gives approximate real-time; the batch gives exact numbers for invoicing."
