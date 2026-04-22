## The Real World Analogy

> [!info] Named after ship design — ships have bulkheads (walls) separating compartments. If one compartment floods, the walls contain the water. The ship keeps floating.

Same principle in software — **isolate failures so one component can't sink everything else.**

---

## The Problem Without Bulkheads

```
Your app has 100 threads — shared across all services

Normal operation:
  Payment       → 20 threads in use
  Recommendations → 15 threads in use
  Notifications  → 10 threads in use
  Available      → 55 threads free

Payment goes slow (30s per request):
  10 users hit Payment  → 10 threads stuck waiting
  20 users hit Payment  → 20 threads stuck
  50 users hit Payment  → 50 threads stuck
  100 users hit Payment → ALL 100 threads stuck

User requests Recommendations → no threads available → fails
User requests Notifications   → no threads available → fails

Payment brought down the entire system
```

> [!danger] Cascading Failure
> One slow service starved all thread resources. Recommendations and Notifications never had a problem — they were killed by association.

---

## The Fix — Bulkhead

Assign each service its own isolated resource pool:

```
Payment        → 20 dedicated threads
Recommendations → 20 dedicated threads
Notifications  → 20 dedicated threads
General pool   → 40 threads

Payment goes slow:
  Its 20 threads fill up
  New Payment requests → fail fast (no thread available)
  
Recommendations → 20 threads untouched → fully operational
Notifications   → 20 threads untouched → fully operational
```

> [!success] Failure contained
> One compartment floods. The ship keeps sailing.

---

## Bulkhead Beyond Thread Pools

The same pattern applies to any shared resource:

| Resource | Without Bulkhead | With Bulkhead |
|---|---|---|
| Thread pools | One service starves all threads | Each service has dedicated threads |
| Connection pools | One service exhausts DB connections | Each service has connection limit |
| Memory | One service causes OOM, kills process | Memory limits per service/container |
| CPU | One service pegs CPU, starves others | CPU limits per container (Docker/K8s) |

> [!tip] In Kubernetes
> Resource limits (`requests` and `limits` in pod spec) are bulkheads at the infrastructure level — each pod gets guaranteed CPU and memory, preventing one pod from starving others.

---

## Bulkhead + Graceful Degradation Together

```
Payment thread pool exhausted (bulkhead triggered)
  ↓
New Payment requests fail fast
  ↓
Graceful degradation kicks in
  ↓
Show "Payment temporarily unavailable, try again in a moment"
  ↓
Recommendations and Notifications: completely unaffected
```

Bulkhead **contains** the failure. Graceful degradation **handles** it for the user.

> [!tip] Interview framing
> *"I'd use bulkheads to isolate thread pools per downstream service — if Payment goes slow, it exhausts its own pool and fails fast rather than starving Recommendations and Notifications. Combined with graceful degradation, users see a payment error while the rest of the app works normally."*
