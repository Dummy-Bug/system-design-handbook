# Instagram Feed Generation — Fan-Out on Write

In the previous section we saw why fan-out on read collapses — assembling a feed at read time requires 500 queries per user, and at 1M feed loads per second that means 500M DB queries every second. Ten thousand database instances just to serve the feed. Not a real answer.

Caching feels like the obvious fix. But caching doesn't eliminate the work — before you can cache a feed, you still have to assemble it first. Those 500 queries still happen, just once instead of every time.

Which is actually the right idea. It just points you toward a completely different question: does the feed have to be assembled at read time at all?

---

## The asymmetry hiding in the numbers

Look at the estimation numbers side by side:

```
Write QPS  →  ~1,000 posts/sec
Read QPS   →  ~1,000,000 feed loads/sec
```

Reads happen 1,000x more often than writes. Every time a user opens the app, you pay the assembly cost. But posts are rare — only 1,000 per second across 500M users.

If reads are expensive, why not shift the work to writes instead? Writes happen 1,000x less often — they're a far cheaper place to do heavy computation.

---

## Building the feed before anyone asks for it

The moment someone posts a photo, immediately push that post into every follower's pre-built feed list. By the time a follower opens Instagram, their feed is already sitting there — no DB queries, no merging, no sorting. Just fetch and return.

This is **fan-out on write** — you fan out the work at write time, so read time is instant.

```
User posts a photo
        ↓
Fan-out worker runs
        ↓
Pushes post into every follower's feed list
        ↓
Follower opens app → feed is already built → instant response
```

The read path collapses to a single cache lookup. Instead of 500 DB queries per feed load, you do one fetch from a pre-built list. The N+1 problem disappears entirely on the read side.

The write side gets heavier — one post now triggers N feed updates where N is the follower count. But at 1,000 posts/sec with an average of 500 followers each, that's 500,000 feed updates per second — well within what a distributed worker pool can handle.
