# During a Partition — Serve or Refuse?

## The Decision Every Node Must Make

A partition has happened. Node B is isolated. A user request arrives.

Node B has two options:

```
Option 1 — Serve the request
  Return whatever data Node B currently has
  Data might be stale (Node A may have newer writes)
  User gets a response ✓
  Response might be wrong ✗

Option 2 — Refuse the request
  Return an error: "system unavailable"
  Data integrity guaranteed ✓
  User gets no response ✗
```

Neither option is perfect. The right choice depends entirely on the system.

---

## When to Serve (Choose Availability)

> [!success] Serve stale data when the cost of being wrong is low

**News feed:**
```
User reads article list during partition
Node B returns articles from 2 minutes ago
User sees slightly old feed → nobody notices
```

**Recommendation system:**
```
Netflix shows recommendations from cached data
Slightly stale recommendations → user still finds something to watch
Being down entirely → user leaves the platform
```

**Social features:**
```
Like counts, follower counts, view counters
Slightly stale numbers → acceptable
Service being down → not acceptable
```

**The reasoning:** Stale data is annoying. Errors are worse. For non-critical reads, availability wins.

---

## When to Refuse (Choose Consistency)

> [!danger] Refuse requests when the cost of wrong data is high

**Payment system:**
```
User checks balance during partition
Node B has stale balance (Mumbai had a withdrawal that didn't replicate)
Node B serves stale balance → user sees $1000
User sends $800 → goes through
Actual balance was $200 → now -$600
```

**Inventory system:**
```
Last item in stock
Both nodes accept order during partition
Two users both get "order confirmed"
One of them will be disappointed
```

**Seat booking / hotel reservation:**
```
Same room booked by two users during partition
Both get confirmation
Someone shows up to a taken room
```

**The reasoning:** Wrong data causes financial loss, legal issues, or broken trust. Better to be temporarily unavailable than permanently wrong.

---

## The System-Specific Decision

| System | During Partition | Reason |
|---|---|---|
| Social feed | Serve stale | Slight staleness harmless |
| Recommendations | Serve stale | Better than being down |
| Shopping cart | Serve stale | Amazon's famous choice |
| Bank balance | Refuse | Wrong balance = financial loss |
| Payment processing | Refuse | Double charge = unacceptable |
| Inventory | Refuse | Overselling = broken trust |
| Hotel booking | Refuse | Double booking = serious problem |

---

## This Is CAP in Action

> [!important] This serve-or-refuse decision IS the CAP theorem

```
Choosing to SERVE  → choosing Availability over Consistency
Choosing to REFUSE → choosing Consistency over Availability

You cannot choose both during a partition
→ that's the CAP theorem
```

During normal operation — no partition — you can have both. It's only when a partition happens that you're forced to pick one.

The next topic (CAP Theorem) formalizes this exactly.
