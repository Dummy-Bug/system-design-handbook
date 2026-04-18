# SLI / SLO Connection

## Why observability matters here

The ID generator is on the critical write path of every system that depends on it. A 10ms latency spike here means every tweet, order, and message in the platform is 10ms slower. A complete outage means writes stop everywhere — no new records can be created in any dependent service.

The blast radius of a failure is the entire platform. That makes observability non-negotiable.

---

## SLOs and their SLIs

| SLO | SLI | Measurement |
|---|---|---|
| p99 latency < 5ms | Request latency histogram | Time from request received to ID returned |
| Availability > 99.99% | Success rate | Successful responses / total requests |
| Zero duplicate IDs | Duplicate ID rate | Count of duplicate IDs detected (should always be 0) |
| Clock skew wait < 10ms | Clock skew wait duration | Time spent waiting for clock to catch up |

---

## Latency SLO — 5ms at p99

The ID generator must not slow down callers. Single-digit milliseconds is the target. We track p50, p95, and p99 — p99 is the SLO boundary because that's what affects the tail of callers.

---

## Availability SLO — 99.99%

99.99% = 52 minutes of allowed downtime per year. Given that this service blocks all writes in every dependent system, even 52 minutes of annual downtime is painful. This is a hard floor.

A 5xx response counts as a failure. A timeout counts as a failure. A queued request waiting for clock skew does **not** count as a failure — it's a delayed success.

---

## Duplicate ID rate — must always be zero

This is a correctness SLI, not a performance one. Any duplicate ID generated means data corruption in a caller's database. This counter should always be 0.

> [!danger] If this metric ever goes above zero, it is an immediate incident
> A single duplicate ID is not a "warning" — it is a P0 incident. Data is already corrupted in the caller's database. There is no recovery path.

How is this measured? Callers can report duplicate primary key constraint violations back to the ID generator via an internal feedback API. The generator also logs every ID it issues — periodic sampling can detect duplicates.

---

## Clock skew wait duration

Every time NTP corrects the clock backwards, the node waits. This wait is normally 1–10ms and invisible to callers. But if it happens frequently or for longer durations, it's a signal that NTP is misbehaving or the hardware clock is unreliable.

Track: how often does clock skew happen per node, and for how long?
