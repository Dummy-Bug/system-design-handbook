# Alerting

## Alert tiers

### Critical — page immediately

These mean the SLO is breached or data is corrupted right now.

| Alert | Condition | Why |
|---|---|---|
| Latency SLO breach | p99 > 5ms sustained for 2 minutes | Callers are being slowed down platform-wide |
| Availability breach | Success rate < 99.99% for 5 minutes | Write path is failing for callers |
| Duplicate ID detected | Duplicate ID count > 0 | Data corruption — P0 incident, no tolerance |
| All nodes unhealthy | LB has no healthy nodes | Complete outage — no IDs can be generated |

### Warning — investigate soon

These are leading indicators — the system is healthy now but trending towards a problem.

| Alert | Condition | Why |
|---|---|---|
| High clock skew frequency | >5 clock skew events/minute on any node | NTP or hardware clock is misbehaving |
| Clock skew wait > 10ms | Any single wait exceeds 10ms | Larger than expected NTP correction |
| Node latency divergence | One node's p99 > 3x other nodes | Node-specific hardware or resource problem |
| Single node down | One node fails health check | Reduced capacity, increased load on remaining nodes |
| Sequence counter saturation | Sequence hitting 4095 (max) per ms | Node receiving more than 4096 requests/ms — unexpected |

### Informational — log and monitor

| Alert | Condition |
|---|---|
| Node restart | Any ID generator node restarts |
| NTP sync event | NTP correction applied to any node |
| Deployment | New version rolled out |

---

## Sustained breach window

Don't alert on a single bad second — brief spikes happen. Alert only when the condition is sustained:

- Critical latency: 2 consecutive minutes above threshold
- Availability: 5 consecutive minutes below threshold
- Duplicate ID: immediate — zero tolerance, no window

A 2-minute window prevents false alarms from brief GC pauses or network blips while still catching real degradation quickly.
