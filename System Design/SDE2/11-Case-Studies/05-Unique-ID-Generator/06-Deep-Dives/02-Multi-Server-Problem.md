# The Multi-Server Problem

## Why a single server isn't enough

A single server with an atomic counter can handle ~10M IDs/second — exactly our peak requirement. But it's a single point of failure. If it goes down, every write to every service in the platform fails instantly.

So we need multiple servers. And that's where the problem begins.

---

## Independent counters collide immediately

Two servers, both starting their counter at 1:

```
Server A: request arrives → counter = 1 → returns ID 1
Server B: request arrives → counter = 1 → returns ID 1
```

Both servers return `1`. Collision. The moment you add a second server with its own independent counter, uniqueness breaks.

---

## Why randomization doesn't fix it

The intuitive fix is to add randomness — each server picks a random number instead of incrementing a counter. But randomness doesn't guarantee uniqueness. It just makes collisions *unlikely*.

At 10M IDs/second across multiple servers, "unlikely" becomes "inevitable." A correctness requirement cannot be satisfied by probability. You need a structural guarantee.

---

## The key insight — machine ID

If each server has a **unique machine ID** baked into every ID it generates, two servers can never produce the same ID — even if their counters and timestamps are identical.

Think of it like this: Server A is only allowed to produce IDs that "belong" to Server A. Server B produces IDs that "belong" to Server B. They operate in completely separate spaces, no coordination needed.

```
Server A (machine_id=1): 1-500-1699999999
Server B (machine_id=2): 2-500-1699999999
```

Same counter value (500), same timestamp — but different machine IDs make them different IDs.

This is the foundation of every multi-server ID generation solution — each server owns a unique space of IDs that no other server can produce.
