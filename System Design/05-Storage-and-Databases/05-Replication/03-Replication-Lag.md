# Replication Lag

> [!question] You updated your Instagram profile picture. You refresh the page immediately and see the old one. The write succeeded — so what went wrong?

---

## What replication lag is

With async replication, replicas are always slightly behind the primary. The primary writes and returns success immediately. The replica applies that write milliseconds — sometimes seconds — later. During that window, the replica has stale data.

Normally this gap is imperceptible. Users don't notice a feed post appearing 50ms later than it was written. But one scenario makes it very visible.

---

## Read-your-own-writes violation

You're on Instagram. You update your profile picture. You immediately refresh your profile page.

```
Write → goes to primary ✓ — primary now has new photo
Read  → load balancer routes to a replica
      → replica is 200ms behind
      → replica still has old photo
      → you see your old profile picture ✗
```

You were told the write succeeded. But you can't see your own change. This is a **read-your-own-writes violation** — one of the most common and user-visible symptoms of replication lag.

Other examples:

```
Post a tweet → refresh feed → tweet not there yet
Send a message → open conversation → message missing
Update settings → page reloads → old settings shown
```

In each case, the write went to the primary, the read hit a lagging replica, and the user sees their own action as if it never happened.

---

## The fix — sticky routing after a write

For a short window after a user writes something, route that specific user's reads to the primary instead of the replica.

```
User updates profile pic:
→ write goes to primary
→ flag: "user 123 just wrote, route their reads to primary for 1 second"
→ user's next read → primary → sees new photo ✓
→ after 1 second (replica has caught up) → reads route to replica again
```

The window only needs to be long enough for the replica to catch up — typically under a second for a healthy replica.

This is often implemented at the application layer or the database proxy layer (e.g. ProxySQL, RDS Proxy).

---

## Other forms of lag-related anomalies

**Monotonic read violation** — you read a value, then read it again and see an older value. Happens when two consecutive reads hit different replicas at different lag points.

```
Read 1 → Replica A (lag: 50ms)  → sees post from 10 seconds ago ✓
Read 2 → Replica B (lag: 500ms) → sees post from 1 minute ago   ✗ (went backwards)
```

Fix: pin a user's session to the same replica for the duration of their session. They see consistent progress — monotonically forward in time.

---

## When lag becomes a serious problem

Most of the time, replica lag is milliseconds and invisible. But in certain conditions it grows:

```
Replica is overloaded     → falling behind, lag grows to seconds or minutes
Network between primary   → slow link, writes queue up, lag spikes
and replica is congested

Long-running write        → replica must apply it sequentially,
on primary (bulk update)  → blocking other updates behind it → lag spike
```

Monitoring replica lag is a critical operational metric — lag above a few seconds in a healthy system is a warning sign. Lag above 30 seconds is an incident.

> [!tip] Interview framing
> "I'd use async replication for read scalability. The trade-off is replication lag, which can cause read-your-own-writes violations. I'd fix that by routing a user's reads to the primary for a short window after they write — typically one second — then returning to replica reads once the replica has caught up."
