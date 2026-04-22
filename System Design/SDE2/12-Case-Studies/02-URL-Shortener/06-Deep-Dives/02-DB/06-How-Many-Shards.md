
> [!info] The question
> You know you need to shard. You know the sharding key. Now — how many shards do you actually need, and how many should you provision from day one?

---

## Step 1 — how many shards does the storage require?

From the estimation:
```
Storage over 10 years = 250TB
```

A practical upper limit per shard — accounting for OS overhead, index space, write-ahead logs, and leaving headroom so the disk is not at 100% capacity:
```
Practical storage per shard = ~10TB
```

Shards needed just for storage:
```
250TB / 10TB per shard = 25 shards
```

25 shards covers the 10-year storage requirement at current growth rate.

---

## Step 2 — add a growth buffer

Traffic and data rarely grow linearly. A URL shortener could 2x in scale over a 3-5 year window as more users and more integrations come online.

If traffic doubles, you need twice the shards. Planning for 2x-3x growth is a defensible engineering buffer:

```
25 shards × 2x growth = 50 shards
25 shards × 3x growth = 75 shards
```

Round to the nearest power of 2 (for consistent hashing ring balance):
```
50 shards → round up to 64
75 shards → round up to 128
```

A reasonable starting target: **64 shards** — covers 2x growth with clean ring splits.

---

## Step 3 — do you provision all 64 from day one?

No. Provisioning 64 shards on day one when you have almost no data has two real costs:

**Operational complexity:**
Each shard is a machine you need to provision, monitor, patch, back up, and recover when it fails. 64 machines on day one — when each holds only a few hundred GB — is massive overhead for no benefit.

**Connection overhead:**
App servers maintain connection pools to DB shards. 64 shards means 64 connection pools per app server. At low traffic, this wastes memory and connections.

**The right approach — start small, grow with consistent hashing:**

```
Day 1     → start with 8 shards (~3TB each, well within capacity)
Year 2-3  → add shards as data grows → consistent hashing moves only K/N keys
Year 5+   → grow toward 32, 64 shards as needed
```

Consistent hashing makes this cheap. Adding one shard moves only 1/N of the data. You never need a full reshard.

The goal is not to pre-provision for 10 years. The goal is to choose a sharding scheme that lets you grow to 64+ shards without pain.

---

## Summary

```
Storage requirement      → 25 shards (250TB / 10TB per shard)
With 2x growth buffer    → 50 shards → round to 64 (power of 2)
Day 1 provisioning       → 8 shards (start small, grow with consistent hashing)
Max target               → 64 shards (covers long-term growth)
```

---

> [!tip] Interview framing
> "Storage math: 250TB / 10TB per shard = 25 shards. With a 2x growth buffer, that's 50 — round to 64 for clean consistent hashing splits. But don't provision 64 from day one — 64 machines with almost no data is operational waste. Start with 8 shards, grow with consistent hashing. Adding shards moves only K/N keys — no catastrophic reshuffling."
