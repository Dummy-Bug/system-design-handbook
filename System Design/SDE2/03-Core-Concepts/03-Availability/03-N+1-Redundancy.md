# N+1 Redundancy

> [!question] You know you need redundancy. But how many backups is enough?
> N+1 gives you a formula instead of a gut feeling.

---

## What it is

**N = the number of components you need to handle your current load.**
**+1 = one extra, always.**

If you need 3 servers to handle your traffic — you run 4. If one dies, you still have exactly 3. Load doesn't spike. Users don't notice anything.

---

## Why "just run two" isn't a rule

"Run two servers" is vague. What if you need 10 servers to handle peak traffic? Running 2 is nowhere near enough — if one dies you're at 1, and the system collapses under load.

N+1 gives you a formula:

- Need 1 server? Run 2. (1+1)
- Need 5 servers? Run 6. (5+1)
- Need 10 servers? Run 11. (10+1)

The "+1" is always exactly one spare — not two, not three. Just enough to absorb one failure without degrading service.

---

## It applies everywhere, not just servers

| Component | N (what you need) | N+1 (what you run) |
|---|---|---|
| App servers | 3 to handle load | 4 |
| Database replicas | 2 | 3 |
| Power supplies in a server | 1 | 2 |
| Datacenters | 1 | 2 |
| Network links between DCs | 1 | 2 |

Same logic at every layer. One failure → still fully operational.

---

## The moment N+1 breaks down

N+1 protects you against **one** failure at a time.

The danger is the gap between failure and replacement:

1. You're running N+1 — 4 servers, need 3
2. One server dies → you're now at N — 3 servers, need 3 — still fine
3. **Before you provision a replacement, a second server dies** → you're at N-1 — 2 servers, need 3 → service degrades or drops

This is why N+1 requires fast replacement, not just fast detection. The "+1" is a buffer, not a permanent safety net.

> [!warning] The moment your +1 becomes your N, you're exposed
> Provision a replacement immediately — don't wait until the next maintenance window.

---

## N+2 — when one spare isn't enough

Setup for all three scenarios below: **you need 3 servers, so you run N+1 = 4**.

### Planned maintenance

You take a server offline to apply a security patch.

```
Before maintenance:  4 servers running  (N+1 — buffer intact)
During maintenance:  3 servers running  (exactly N — zero buffer)
```

If one more server dies during that window, you're at 2 but need 3. Service degrades.

With **N+2 = 5 servers**:
```
Before maintenance:  5 servers running
During maintenance:  4 servers running  (still N+1 — buffer intact)
```

Now a failure during maintenance still leaves you at exactly N. Still safe.

---

### Slow provisioning

A server dies. You're now at exactly N — no buffer. You start spinning up a replacement but it takes **20 minutes** to boot, configure, and join the cluster.

For those 20 minutes you have zero buffer. A second failure in that window puts you under capacity.

With **N+2 = 5 servers**:
```
Server 1 dies  →  4 servers left  (still N+1 — buffer intact)
Provisioning takes 20 minutes...
Server 2 dies in that window  →  3 servers left  (exactly N — still safe)
```

The second spare covers the provisioning gap.

---

### Mission-critical systems

Payment processors, hospital systems. The question isn't "can two servers die at once?" — it's "what's the cost if they do?"

- Startup — two simultaneous failures → some users annoyed → N+1 is fine
- Payment processor — two simultaneous failures during peak → transactions failing → millions in losses + regulatory consequences → N+2 is worth the cost

---

## The mental model

| Configuration | What it survives |
|---|---|
| N+1 | One failure |
| N+2 | One failure while something else risky is already happening |
| N+K | K simultaneous problems |

The cost scales linearly — one more instance per +1. The decision is: *what's the cost of a second failure in my system?*

> [!tip] In an interview
> *"I'd run N+1 for the app servers — one spare to absorb any single failure. For the database tier, given slow replica provisioning, I'd consider N+2 to cover the replacement window."*
