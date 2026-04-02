# Cold Start Problem

> [!question] Auto-scaling triggered. A new server is booting. Traffic is already spiking. The server won't be ready for 7 minutes. What do you do?
> Three solutions — each attacking the problem at a different point.

---

## What Cold Start Is

When a new server boots from scratch, it's not immediately useful. It has to go through a full startup sequence:

```
1. Start blank VM                           30 seconds
2. OS boot                                  20 seconds
3. Install runtime (Java, Node, Python)     60 seconds
4. Install application dependencies        90 seconds
5. Pull latest application code from Git   30 seconds
6. Run startup checks                       20 seconds
7. Start application process               30 seconds
8. JVM warmup / cache population           60 seconds
9. Pass health checks (3 consecutive)      30 seconds
──────────────────────────────────────────────────────
Total: ~6-7 minutes before serving traffic
```

During those 6-7 minutes, the new server is useless. Existing servers remain overloaded. Users experience slowness.

For a reactive spike — traffic doubles in 30 seconds — 7 minutes is an eternity.

---

## Solution 1 — Pre-baked AMIs

**What an AMI is:**
AMI (Amazon Machine Image) is a complete frozen snapshot of a server's disk — OS, runtime, dependencies, application code — all captured at a specific point in time. Booting from an AMI means starting with everything already installed.

**Normal boot vs AMI boot:**

```
Normal boot:                              AMI boot:
──────────────────────────────────────    ──────────────────────────────
1. Start blank VM            30s          1. Start VM from AMI snapshot  30s
2. Install Java              60s             (Java already installed)
3. Install dependencies      90s             (Dependencies already there)
4. Pull code from Git        30s             (Code already baked in)
5. Start application         30s          2. Start application           15s
6. JVM warmup                60s          3. JVM warmup                  30s
7. Pass health checks        30s          4. Pass health checks          15s
──────────────────────────────────────    ──────────────────────────────
Total: ~7 minutes                         Total: ~90 seconds
```

Everything that was installed and configured is frozen into the image. You skip the entire setup phase.

**How AMIs fit into a deployment pipeline:**

```
Engineer merges new code
  ↓
CI/CD pipeline runs tests
  ↓
Pipeline bakes new AMI (installs new code into the image)
  ↓
Auto-scaling group updated: "use new AMI for all future servers"
  ↓
Next time scaling triggers → new server boots from new AMI → 90 seconds to ready
```

Old servers running old code stay running until they're drained and replaced. Zero downtime deployment.

---

## Solution 2 — Warm Pools

Even 90 seconds is too slow for a sudden spike. Warm pools eliminate the remaining wait entirely.

**The concept:**
Keep a small set of servers already booted and idle — not registered with the load balancer, not serving traffic, just sitting there having already completed startup. When scaling triggers, pull from the pool instead of booting fresh.

```
Normal state:
  Active servers: 10  (serving traffic, registered with LB)
  Warm pool:       3  (booted, idle, NOT registered with LB)

Traffic spike hits — scaling triggers:
  Option A (without warm pool): boot new server → 90 seconds
  Option B (with warm pool):    pull from warm pool → register with LB → 5 seconds

After pulling from warm pool:
  Active servers: 11  (new server immediately serving traffic)
  Warm pool:       2  (one slot freed — trigger to replenish in background)

Background (off critical path):
  Boot new server → add to warm pool
  Active servers: 11
  Warm pool:       3  (replenished, ready for next spike)
```

The cold start still happens — it just happens in the background, not during a spike.

**Cost tradeoff:**

Warm pool servers are idle but not free. You pay for them doing nothing.

```
3 warm pool servers × $0.10/hour = $0.30/hour = $216/year
```

The question is: what does 90 seconds of overloaded servers cost you in lost revenue and user experience? For most production systems — $216/year is trivial compared to the damage of a slow spike response.

**Warm pool sizing:**

Too small → spike exhausts pool, back to cold booting
Too large → paying for idle capacity you rarely use

Rule of thumb: size the warm pool to cover your typical sudden spike. If traffic usually jumps 20% in a burst, keep enough warm servers to absorb that 20%.

---

## Solution 3 — Predictive Scaling

The cleanest solution: don't let cold start happen during a spike at all. Start servers before the spike arrives.

**How it works:**
Auto-scaling analyses historical traffic patterns and pre-scales based on predictions:

```
Historical data: traffic 5x every weekday at 9:00am

Predictive rule:
  8:45am → add 40 servers (cold start happens now — 7 minutes off peak)
  8:52am → all 40 servers warmed up, registered with LB, health checks passing
  9:00am → traffic arrives → 50 servers already waiting, no spike felt
  6:30pm → traffic drops → scale back in with connection draining
```

Cold start still takes 7 minutes. But it happens at 8:45am when load is low — not at 9:00am when users are hammering the system.

**Netflix — show release scaling:**

```
New season drops: Friday 3:00am

Netflix's schedule:
  Thursday 8:00pm  → predictive scaling adds servers across all regions
  Thursday 8:00pm → 11:00pm → cold starts complete, JVMs warmed up, caches populated
  Friday 3:00am   → show drops, millions start streaming simultaneously
                    Infrastructure already at full capacity — zero spike felt
```

By the time users arrive, servers aren't just booted — they're warm. JVM has been running for hours, hit-ratio on caches is high, everything optimised.

---

## The Three Solutions Compared

| Solution | Reduces boot time to | Cost | Best for |
|---|---|---|---|
| Pre-baked AMI | ~90 seconds | Low — just CI/CD pipeline change | All systems — should always do this |
| Warm pool | ~5 seconds | Medium — pay for idle servers | Systems with unpredictable sudden spikes |
| Predictive scaling | 0 seconds during spike | Low — servers run only when needed | Systems with predictable traffic patterns |

**In practice — use all three together:**

Pre-baked AMI makes every boot faster (baseline improvement). Warm pool handles sudden spikes. Predictive scaling handles known patterns like daily peaks or scheduled events. They're complementary, not alternatives.

> [!tip] In an interview — cold start is a follow-up question after auto-scaling
> *"For cold start, I'd use pre-baked AMIs to get boot time under 90 seconds, a warm pool sized for typical spike magnitude for instant response, and predictive scaling for known traffic patterns like daily peaks or planned launches."*
