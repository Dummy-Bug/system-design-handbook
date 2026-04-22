# Lambda vs Kappa — Comparison

> [!info] Lambda runs batch + stream in parallel and merges results — accurate but operationally expensive (two codebases). Kappa runs stream only and replays history when needed — simpler but requires your stream processor to handle replay at scale. The choice comes down to whether batch-level accuracy is a hard requirement, or whether operational simplicity is worth more.

## Side by Side

| | Lambda | Kappa |
|---|---|---|
| Pipelines | Two (batch + stream) | One (stream only) |
| Codebases | Two | One |
| Consistency | Batch and stream can drift | Single pipeline, always consistent |
| Accuracy | Batch is exact, stream is approximate | One logic, consistent accuracy |
| Latency | Low (speed layer) + delayed correction (batch) | Low (stream handles both) |
| Historical reprocessing | Spark reruns on S3 | Replay Kafka/S3 through stream processor |
| Operational complexity | High — maintain two pipelines | Low — one pipeline |
| Storage requirement | S3 + Kafka | S3 (source of truth) + Kafka |
| Use when | Batch accuracy non-negotiable | Simplicity matters, stream can handle replay |

---

## Decision Rule

**Use Lambda when:**
- Regulatory or financial accuracy is required (billing, compliance, tax)
- Batch and stream results need to be independently verifiable
- Your stream processor cannot replay years of history at scale

**Use Kappa when:**
- You want one codebase and one pipeline to maintain
- S3 is your source of truth and you can replay through Kafka
- Your stream processor (Flink, Kafka Streams) is capable enough for both live and replay

---

## Interview Answer Template

> "For the real-time dashboard I'd use a stream processor — Flink consuming from Kafka, results updated every second. For the monthly billing report I need exact numbers, so I'd run a nightly Spark batch job against the raw event log in S3. This is Lambda architecture — speed layer for low latency, batch layer for accuracy, serving layer merges both. If operational simplicity is a priority and we're okay with Kappa, we could drop the batch pipeline and replay historical events from S3 through the same stream processor using a new consumer group from offset 0."

---

## Where These Appear in Interviews

| System | Architecture |
|--------|-------------|
| Ad Click Aggregation | Lambda — real-time approximate counts + nightly exact reconciliation |
| Billing / Payments | Lambda — batch for exact invoicing, stream for live alerts |
| News Feed Analytics | Kappa — stream handles both live feed and historical replay |
| Fraud Detection | Kappa — single stream processor, replay to retrain on historical patterns |
| Log Analytics | Either — depends on accuracy requirements |
