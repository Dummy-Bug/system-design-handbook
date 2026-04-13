
> [!info] The routing problem
> Once you decide to shard by short_code, you need a way to map any short code to a specific shard. The naive approach — modulo hashing — works but breaks badly when shards are added or removed. Consistent hashing solves this.

---

## The naive approach — modulo hashing

Take the hash of the short code, divide by the number of shards, use the remainder as the shard number:

```
shard = hash(short_code) % N
```

Example with 4 shards:
```
hash("x7k2p9") = 1839274  →  1839274 % 4 = 2  →  Shard 2
hash("a3f8c2") = 9274610  →  9274610 % 4 = 2  →  Shard 2
hash("q9m3r7") = 4719283  →  4719283 % 4 = 3  →  Shard 3
```

Simple. Fast. Works perfectly — until you need to add or remove a shard.

---

## Why modulo breaks when shards change

If you go from 4 shards to 5 shards, the formula changes:

```
Before: shard = hash(short_code) % 4
After:  shard = hash(short_code) % 5
```

A short code that mapped to Shard 2 before might now map to Shard 0. Every single key gets re-evaluated with the new N.

```
hash("x7k2p9") = 1839274
Before: 1839274 % 4 = 2  →  Shard 2
After:  1839274 % 5 = 4  →  Shard 4   ← moved!
```

In practice, when you add one shard to a 4-shard cluster:
```
Keys that stay in place  → ~20% (1/N of keys)
Keys that must move      → ~80% (the rest)
```

At 250TB of data, 80% moving means 200TB of data migration. During that migration, queries go to the wrong shard. The system is broken until the migration completes.

This is catastrophic at scale. You cannot afford to remap most of your data every time you add capacity.

---

## Consistent hashing — the fix

Consistent hashing places both shards and keys on a virtual ring. The ring has positions from 0 to 2^32 (about 4 billion positions).

**Setting up the ring:**

Each shard gets assigned one or more positions on the ring by hashing its identifier:

```
hash("Shard-1") = 1,073,741,824  →  position 25% around the ring
hash("Shard-2") = 2,147,483,648  →  position 50% around the ring
hash("Shard-3") = 3,221,225,472  →  position 75% around the ring
hash("Shard-4") = 4,294,967,295  →  position 100% (wraps to 0%)
```

**Routing a key:**

Hash the short code to get a ring position. Walk clockwise around the ring until you hit a shard. That shard owns this key.

```
hash("x7k2p9") = 1,500,000,000
Walk clockwise → first shard encountered is Shard-2 at position 2,147,483,648
→ this key belongs to Shard-2
```

**Adding a new shard:**

Add Shard-5 at position 1,200,000,000 (between Shard-1 and Shard-2):

```
Before: keys between position 1,073,741,824 and 2,147,483,648 → Shard-2
After:  keys between position 1,073,741,824 and 1,200,000,000 → Shard-2 (unchanged)
        keys between position 1,200,000,000 and 2,147,483,648 → Shard-5 (moved from Shard-2)
```

Only the keys that were in Shard-2's range and fall between the old boundary and the new shard's position need to move. Everything else stays put.

```
Modulo hashing:     add 1 shard → ~80% of all keys move
Consistent hashing: add 1 shard → only K/N keys move (1/N of total)
```

At 250TB with 25 shards, adding one shard moves only 1/26 of the data — about 10TB instead of 200TB.

---

## Virtual nodes — fixing uneven distribution

A problem with basic consistent hashing: shards land at fixed positions on the ring. With only 4 shards, the spacing between them may be uneven — one shard might own 40% of the ring while another owns 10%.

Virtual nodes (vnodes) fix this. Each physical shard gets assigned multiple positions on the ring — say 100-150 positions each. Each position is a virtual node.

```
Shard-1 → 150 virtual nodes scattered around the ring
Shard-2 → 150 virtual nodes scattered around the ring
Shard-3 → 150 virtual nodes scattered around the ring
```

With 150 virtual nodes per shard, the ring has 600 positions for 4 shards. The spacing between consecutive positions is small and roughly even. Each shard ends up owning approximately 25% of the keyspace — regardless of where the physical shards landed.

---

## Why power of 2 for shard count

The consistent hashing ring spans from 0 to 2^32. When you add a new shard, you split an existing shard's range in half — giving half its keys to the new shard.

If your total shard count is a power of 2 — 2, 4, 8, 16, 32, 64, 128 — every split is perfectly even:

```
1 shard  → owns 100% of ring
2 shards → each owns 50%    (split evenly)
4 shards → each owns 25%    (split evenly)
8 shards → each owns 12.5%  (split evenly)
16 shards → each owns 6.25% (split evenly)
...always clean halves
```

If shard count is not a power of 2 — say 10 shards — the splits become uneven. Some shards own more of the ring than others, causing load imbalance.

Power of 2 keeps the ring balanced at every growth step. This is why shard counts in production systems are almost always 8, 16, 32, 64, or 128 — not 10, 15, or 25.

---

> [!tip] Interview framing
> "Consistent hashing over modulo — adding a shard with modulo remaps ~80% of all keys, at 250TB that's catastrophic. Consistent hashing moves only K/N keys. Virtual nodes ensure even distribution across the ring. Power of 2 shard count keeps splits perfectly even at every growth step — that's why production shard counts are 8, 16, 32, 64, not 10 or 25."
