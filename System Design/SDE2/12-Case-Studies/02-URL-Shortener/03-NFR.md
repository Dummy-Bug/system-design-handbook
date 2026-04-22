
> [!info] What NFRs actually are
> Functional requirements say what the system does. Non-functional requirements say how well it does it. NFRs drive every architectural decision that follows — consistency model, replication strategy, caching, fault isolation.

---

## Availability over Consistency

A URL shortener is a user-facing system. When someone clicks a link, they expect it to work — not get an error because two replicas disagree. **Availability wins.**

This means the system runs with async replication and eventual consistency. Replicas may be slightly stale, but the system stays up even if some nodes are down.

```
Availability SLA → 99.9%   (contractual guarantee to users)
Availability SLO → 99.99%  (internal target, stricter than SLA)
```

---

## Consistency Model — Eventual + Read-Your-Own-Writes

Full strong consistency is overkill here. You don't need every user to instantly see every other user's newly created URL. But there is one specific case that matters:

**The creator clicking their own link immediately after creating it.**

If you just shortened a URL and immediately click it to test it — and get a 404 because your replica hasn't synced yet — that's a terrible experience. Read-your-own-writes solves exactly this narrow case.

```
Everyone else  → reads from any replica (eventual consistency)
The creator    → routed to fresh data for a short window after their write
```

By the time the creator shares the URL and others start clicking it, the replicas have already synced. The window is seconds. Eventual consistency handles everything else.

The tension with availability is real but manageable — RYOW is a targeted routing rule for one user for a short window, not a system-wide consistency requirement. Availability is barely impacted.

---

## Latency SLAs

Redirects must be fast. This is a user-facing operation — the user clicks a link expecting to land on the destination instantly. Any perceptible delay feels broken and jittery. Unlike a background job or a batch process, a redirect happens in the critical path of a human waiting. Studies show users abandon pages that take more than a few hundred milliseconds to respond. A URL shortener that adds visible latency to every link click defeats its own purpose.

```
Redirect (read)
  SLA → 100ms   (maximum acceptable latency)
  SLO → 10ms    (internal target)

URL creation (write)
  SLA → 500ms
  SLO → 50ms
```

Writes are heavier than reads — they involve ID generation, a DB write, and cache population. Reads should be near-instant, ideally served from cache.

---

## Fault Isolation

The redirect flow and the creation flow should be **independent services**. If URL creation goes down — the write path is broken — redirects must still work. Users clicking existing links should be completely unaffected.

```
Creation service down → users cannot shorten new URLs
                      → existing redirects work perfectly ✓

Redirect service down → users cannot follow links
                      → creation still works ✓
```

This is a deliberate architectural choice that must be stated upfront — it influences how you split services in your base architecture.

---

## Durability

Once a URL is created, it must never be lost. This is separate from availability. The system can go down temporarily (unavailability) — but when it comes back, every URL that was ever created must still be there.

This means the database must be replicated and backed up. Losing a short URL mapping is unacceptable — users have already distributed that link everywhere.

---

## Reliability

Two different long URLs must never be assigned the same short code. If `bit.ly/x7k2p` points to Amazon today, it cannot point to Google tomorrow for a different user. This is a correctness/reliability guarantee — a collision here causes real user harm. The system must be reliable enough that every redirect always lands the user on the right destination.

> [!tip] Interview framing
> For a URL shortener: availability over consistency, eventual consistency system-wide with read-your-own-writes for the creator, sub-100ms redirect latency, fault isolation between creation and redirect, durability (URLs once created are never lost), and uniqueness (no two long URLs share a short code). These seven NFRs drive every architectural decision that follows.
