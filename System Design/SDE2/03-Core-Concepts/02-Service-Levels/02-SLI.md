# SLI — Service Level Indicator

> [!question] How do you know what your system is actually doing right now?
> You measure it. That measurement is your SLI.

---

## What it is

An SLI is simply **a number your system is actively generating right now**.

Not a target. Not a promise. Just a real measurement being produced by your system at this moment.

- P99 latency = 180ms → SLI
- 0.5% of requests are returning errors → SLI
- System was available 99.7% of the last 30 days → SLI
- 95% of DB queries completed under 50ms → SLI

---

## What to measure — and what NOT to measure

You don't measure everything. You pick the measurements that directly reflect whether your **users are having a good experience**.

> [!warning] SLIs must reflect user experience — not internal infrastructure health

**Good SLIs:**
- Message delivery latency — users feel this directly
- Error rate on the API — users see these failures
- Availability — is the service up when users try to use it?

**Bad SLIs:**
- CPU usage — a server can be at 90% CPU and users are perfectly fine
- Memory usage — same problem, doesn't map to user experience
- Number of database connections — internal plumbing, users don't feel this

> [!info] A server can be at 10% CPU and every request is still failing
> Internal metrics tell you about your infrastructure. SLIs tell you about your users. These are different things.

---

## Wait — what's the difference between P99 and an SLI?

This is the most common confusion after learning percentiles.

**P99 is a calculation method. SLI is a concept — what you decided to measure.**

- The SLI is the *what* — what are we measuring?
- P99 is the *how* — how are we computing that measurement?

You decide to measure **response time** → that decision is your SLI.
You choose to express it as **P99** → that's the calculation method you picked.

The same SLI can be expressed multiple ways:

| SLI | Expressed as | Result |
|---|---|---|
| Response time | P99 | P99 latency = 180ms |
| Response time | P50 | P50 latency = 50ms |
| Response time | Average | Average latency = 60ms (but averages lie) |

And not all SLIs use percentiles at all:
- SLI = error rate → *"0.5% of requests failed"* — a ratio, no percentile involved
- SLI = availability → *"99.9% uptime this month"* — a percentage, no percentile involved

> [!info] P99 is just one tool for expressing an SLI — not the same thing as an SLI

---

## SLIs are always ratios or percentiles — never raw counts

❌ *"500 errors happened today"* — raw count, meaningless without context. 500 errors out of 100 requests is catastrophic. 500 errors out of 10 million requests is fine.

✅ *"0.5% of requests returned errors"* — a ratio, meaningful regardless of traffic volume

> [!tip] The test for a good SLI
> If traffic doubles, does the number stay meaningful?
> - Error count doubles → not meaningful anymore
> - Error rate stays the same → meaningful, it's a good SLI

---

## Common SLIs by system type

| System | SLI examples |
|---|---|
| API / Web service | Request success rate, P99 latency |
| Storage system | Read/write success rate, P99 read latency |
| Data pipeline | Freshness (how old is the latest data?), throughput |
| Batch job | Job completion rate, job duration P95 |
| Video streaming | Buffering rate, playback start latency |
