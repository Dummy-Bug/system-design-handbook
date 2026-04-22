# Error Budget

## What the budget is

At 99.99% availability SLO:

```
Allowed downtime per year  = 0.01% × 365 × 24 × 60 = 52.6 minutes/year
Allowed downtime per month = 0.01% × 30 × 24 × 60  = 4.3 minutes/month
```

Every minute the service is unavailable or breaching its latency SLO consumes from this budget.

---

## What consumes the budget

| Event | Budget consumed | Notes |
|---|---|---|
| Node crash + failover | ~30 seconds | LB detects failure, stops routing, callers retry |
| Full cluster restart (rolling deploy) | ~1–2 minutes | Nodes restart one at a time, brief reduced capacity |
| NTP correction causing wait spikes | Seconds | Brief latency SLO breach, not full unavailability |
| Hardware failure on one node | Until replacement | Reduced capacity, remaining nodes absorb load |

---

## Duplicate IDs consume infinite budget

A duplicate ID is not an error budget problem — it is a correctness failure. Error budgets measure availability and latency. Data corruption is outside the budget model entirely.

If a duplicate ID is ever detected, the incident response is not "how much budget did we consume?" — it is "which records are corrupted, how do we fix the data, and what code change caused this?"

> [!danger] Duplicate IDs are not an SLO issue — they are a correctness incident
> SLOs measure degradation. A duplicate ID is a bug that corrupted production data. Treat it as a P0 incident with a full post-mortem, not as budget consumption.

---

## Budget policy

**Healthy budget (>50% remaining):** Deploy freely. Experiment with node configurations. Normal operations.

**Degraded budget (10–50% remaining):** Freeze non-critical changes. Investigate what consumed the budget. No risky deployments.

**Budget exhausted (<10% remaining):** Feature freeze. Only critical fixes. Post-mortem required before any changes. Focus entirely on reliability improvements.

---

## Rolling deploy strategy

When deploying a new version, restart nodes one at a time:

```
Node 1 restarts → Nodes 2 and 3 absorb all traffic
Node 1 healthy → Node 2 restarts → Nodes 1 and 3 serve traffic
Node 2 healthy → Node 3 restarts → Nodes 1 and 2 serve traffic
```

Each restart causes a brief capacity reduction — not an outage. Budget consumed per deploy is typically under 30 seconds — well within the 4.3-minute monthly allowance.
