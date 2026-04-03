# Fault Tolerance

## What it is

> [!info] Fault Tolerance = the system continues functioning when parts of it fail. Not perfectly. Not fully. But enough that users can still do something useful.

**The Instagram example:**

```
Scenario A — Not fault tolerant:
  Stories service fails → entire app crashes → white screen

Scenario B — Fault tolerant:
  Stories service fails → feed still loads → Stories bar missing
```

Both have a failure. Only one keeps the user productive.

---

## The Three Failure Modes

Not all failures look the same. Each requires a different detection and handling strategy.

### 1. Crash Failure

The service dies or becomes completely unreachable.

```
Server restarts mid-request
Network partition — node unreachable
Process killed by OOM killer
```

> [!success] Easiest to detect
> Health checks and heartbeats catch this immediately. Load balancer removes the server from rotation automatically.

---

### 2. Slow Failure

The service is alive but too slow to be useful. Often **worse** than a crash.

```
Server overwhelmed → request queue fills up → responses take 30 seconds
Database connection pool exhausted → requests hang waiting for a connection
Memory pressure → GC pauses → sporadic 2-4 second freezes
```

> [!warning] Harder to detect than crash
> Heartbeat says the server is alive. But alive ≠ useful. A server taking 30 seconds per request is functionally dead. Without timeouts, threads pile up waiting → cascading failure.

---

### 3. Byzantine Failure

The service runs fine and returns responses — but the responses are **wrong**.

```
A bug causes Zomato to show ₹0 price for every item
Payment service charges the wrong amount due to a race condition
Recommendation engine returns items from the wrong user's profile
```

> [!danger] Hardest to detect
> Heartbeat passes. Health check passes. No errors thrown. No timeouts. Just silently wrong data flowing through the system. By the time you detect it, damage is already done.
>
> Detection requires **data validation**, **checksums**, **anomaly detection** — not just health checks.

---

## Fault Tolerance vs Reliability

> [!important] These are related but different problems
>
> | | Question it answers | Example failure |
> |---|---|---|
> | **Fault Tolerance** | Is the system operational? | Server crashes → failover kicks in |
> | **Reliability** | Is the system correct? | Bug returns wrong price |
>
> Byzantine failures sit at the intersection — the system is operational but not correct.
>
> Sometimes you deliberately trade one for the other — graceful degradation trades reliability (returning generic data) for availability (staying operational). That's a conscious design decision, not a mistake.

---

## The Tools

```
Failure detected → what do you do?

Crash failure    → Redundancy + Failover
Slow failure     → Timeout → Retry → Circuit Breaker
Byzantine        → Validation + Checksums + Monitoring
Any failure      → Graceful Degradation + Bulkhead
```
