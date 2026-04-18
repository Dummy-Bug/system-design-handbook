# Snowflake ID — The 64-Bit Solution

## Why 64 bits?

We need to pack three things into one ID: a timestamp, a machine ID, and a sequence counter. The question is what container to use.

**Why not 12 bytes (96 bits)?**
There is no native 96-bit integer type in any major database. You'd have to store it as a string or binary blob — slower comparisons, larger indexes, no native sorting. Every database has `BIGINT` (64-bit signed integer) built in. Fast to compare, fast to index, 8 bytes of storage.

**Why not characters?**
IDs are machine-readable only. Characters are for humans. A char-based ID like `"A3-500-1699999"` takes far more than 8 bytes and is slower to compare. We want pure binary — a number.

**64 bits = 8 bytes = `BIGINT` = the right choice.** It's the minimum size that can fit timestamp + machine ID + sequence for hundreds of years.

---

## Deriving the bit layout

You have 64 bits. Three things to fit in. Let's derive how many bits each needs.

### Sign bit — 1 bit

The most significant bit of a signed 64-bit integer indicates positive or negative. We always want positive IDs, so this bit is always `0`. It's reserved — not used for any data.

Remaining: **63 bits**.

### Sequence counter — 12 bits

The sequence counter handles multiple IDs generated within the same millisecond on the same server.

At peak: 10M IDs/second across the system. With ~1000 machines (see machine ID section below), each machine handles:
```
10M / 1000 = 10,000 IDs/second per machine
10,000 / 1000 ms = 10 IDs/millisecond per machine
```

But we size for burst, not average. Twitter's Snowflake uses **12 bits = 2^12 = 4096 IDs per millisecond per machine**. That gives enormous headroom for spikes.

If the sequence counter hits 4096 within one millisecond, the server simply waits until the next millisecond before generating more IDs.

### Machine ID — 10 bits

One server can handle ~10M IDs/second. Our peak is 10M total. So technically one server suffices for throughput — but that's a SPOF.

For high availability across data centers and regions, you want hundreds of machines. **10 bits = 2^10 = 1024 unique machine IDs**. Start with 3, scale to hundreds — you have room.

In Twitter's implementation, the 10 machine ID bits are split further:
- 5 bits for datacenter ID (32 datacenters)
- 5 bits for worker ID within a datacenter (32 workers per datacenter)

### Timestamp — 41 bits

Remaining: 64 - 1 - 10 - 12 = **41 bits**.

This stores milliseconds elapsed since a custom epoch (a fixed start date chosen by the company — Twitter used November 4, 2010).

How long does 41 bits last?
```
2^41 = ~2.2 × 10^12 milliseconds

1 year = 365 × 24 × 3600 × 1000 = ~3.15 × 10^10 milliseconds

2.2 × 10^12 / 3.15 × 10^10 ≈ 69 years
```

From Twitter's epoch (2010), this covers until ~2079. More than enough.

> [!info] Custom epoch vs Unix epoch
> Unix epoch starts at January 1, 1970. Using it wastes the first 40 years worth of milliseconds on IDs that will never be generated. A custom epoch starting closer to your launch date maximises the usable range of your 41-bit timestamp.

---

## Final bit layout

```
| 1 bit  | 41 bits       | 10 bits      | 12 bits         |
| sign=0 | timestamp ms  | machine ID   | sequence counter|
```

Visualised as a 64-bit number:

```
0 | 00000000000000000000000000000000000000000 | 0000000000 | 000000000000
  |←————————————— 41 bits ————————————————→| ←— 10 —→  | ←— 12 ——→
```

---

## Why this guarantees uniqueness

Two servers can never produce the same ID because their machine IDs are different — they occupy different bit positions in the final number. Two requests on the same server in the same millisecond get different sequence counter values. Two requests in different milliseconds get different timestamps.

The three fields together cover every possible collision scenario — no coordination between servers needed at all.

---

## Why IDs are time-sortable

The timestamp occupies the **most significant bits** (after the sign bit). When you compare two IDs as integers, the timestamp dominates the comparison. A newer ID has a larger timestamp, therefore a larger integer value. Sorting by ID = sorting by creation time. Free of charge.

> [!important] The timestamp must be in the most significant bits
> If you put machine ID or sequence in the high bits, sorting by ID would group by machine, not by time. The layout order matters — timestamp first, then machine ID, then sequence.

---

## What each component guarantees

| Component | Bits | Max value | Purpose |
|---|---|---|---|
| Sign | 1 | Always 0 | Ensures positive integers |
| Timestamp | 41 | ~69 years from epoch | Time-sortability |
| Machine ID | 10 | 1024 machines | Cross-server uniqueness |
| Sequence | 12 | 4096 IDs/ms per machine | Within-millisecond uniqueness |
