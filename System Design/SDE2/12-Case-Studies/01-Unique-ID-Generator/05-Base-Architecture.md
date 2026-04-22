
## The simplest thing that works

The base architecture is as simple as it gets:

```
Client → ID Generator (in-memory counter) → Client
```

A single ID generator server maintains an in-memory counter starting at 1. Every incoming request reads the current counter value, increments it by 1, and returns it. No database, no coordination, no randomness.

This is 100% unique on a single server — no two requests can ever get the same number because the counter only moves forward.


> [!info] Base architecture is intentionally naive
> The point of the base architecture is to establish the simplest correct system, not the most scalable one. The concurrency problem, the multi-server problem, and the scale problem are all covered in the deep dives.

---

## What breaks next

Two things break as soon as you try to scale:

1. **Concurrency on a single server** — simultaneous requests collide on the counter (the lock problem above)
2. **Multiple servers** — two servers with independent counters will both generate ID `1`, `2`, `3`... and collide with each other immediately

Both of these are deep dive problems. The base architecture just establishes the mental model: a counter that only moves forward is the foundation of every ID generation scheme.
