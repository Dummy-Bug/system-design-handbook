
> [!info] Lambda architecture runs two separate pipelines in parallel — a batch layer for accuracy and a speed layer for real-time — then merges their results in a serving layer. 
> The insight is that you can't get both low latency and guaranteed accuracy from a single system, so you run both and combine them. The cost is maintaining two codebases that compute the same thing.

## The Problem It Solves

Some systems have two conflicting requirements for the same data:
1. **Real-time** — show results updated every second (live dashboard)
2. **Accurate** — produce exact numbers for billing/compliance (monthly report)

A stream processor gives you speed but approximate results. A batch job gives you exact results but is slow. You need both.

Lambda Architecture runs **two separate pipelines** in parallel.

---

## The Three Layers

```
                    Raw Events
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
   Speed Layer                  Batch Layer
   (Stream Processor)           (Spark / MapReduce)
   processes live events        reprocesses all history
   low latency                  high accuracy
   approximate                  exact
          │                           │
          └─────────────┬─────────────┘
                        ▼
                  Serving Layer
                  merges both results
                  answers queries
```

**Batch layer** — periodically reprocesses all historical data (S3) using Spark or MapReduce. Slow but 100% accurate. Runs every hour or every day.

**Speed layer** — stream processor handles live events as they arrive. Fast but covers only recent data since last batch run.

**Serving layer** — merges batch results (accurate, delayed) + speed layer results (recent, approximate) to answer queries.

---

## Example: Revenue Dashboard

```
Batch layer:  Spark job runs every hour
              reprocesses all events from S3
              produces exact revenue up to 1 hour ago

Speed layer:  Flink processes live events
              produces approximate revenue for last hour

Serving layer: query answer =
              batch result (up to 1 hour ago) +
              speed layer result (last hour)
```

---

## The Core Problem: Logic Drift

Both layers compute the same thing — revenue. But they're separate codebases.

Say a bug is found: discounts are being applied incorrectly.

```
Fix in batch pipeline  ✅
Fix in speed pipeline  ← easy to forget, or applied differently
```

Now:
```
Speed layer:  revenue = $98,000   (old buggy logic)
Batch layer:  revenue = $95,000   (correct logic)
```

Every bug must be fixed twice. Every feature added twice. Every test written twice. Over time the two pipelines **drift apart** — producing different results for the same data.

This is the fundamental pain of Lambda.

---

## When To Use Lambda

- Batch accuracy is **non-negotiable** (billing, compliance, financial reporting)
- You can afford to maintain two separate pipelines
- Your stream processor cannot handle full historical replay at scale
- Results older than N hours can tolerate eventual correction via batch
