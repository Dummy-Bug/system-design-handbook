> [!question] Your system launched with 4 shards. Two years later you have 10x users. You need more shards. How do you do this without taking the system down?

---

## Why resharding is dangerous

Even with consistent hashing minimising remapping, moving data while a system is under live production traffic is one of the most dangerous operations in distributed systems.

Consider what happens mid-migration when a row is being moved from Shard 1 to Shard 3:

```
Row X is being migrated from Shard 1 → Shard 3

Write comes in for Row X:
  → routes to Shard 1? (old location — migration not complete)
  → routes to Shard 3? (new location — data not fully there yet)
  → either way: wrong answer → data loss or inconsistency

Meanwhile: all shards are slower as they copy data to neighbours
           query latency spikes during the migration window
```

And this isn't one row — it's potentially hundreds of millions of rows migrating simultaneously across multiple shards.

---

## Strategy 1 — Over-shard upfront (best)

The core idea: **separate virtual shards from physical servers from day one.**

On day one you only have 4 servers. But instead of creating 4 shards (one per server), you create 256 virtual shards and map groups of them onto your 4 servers. Each server thinks it owns 64 shards, not 1.

```
Day 1 (4 servers):
  Server A → virtual shards 1–64
  Server B → virtual shards 65–128
  Server C → virtual shards 129–192
  Server D → virtual shards 193–256
```

The 256 shards cost almost nothing upfront — they're just logical partitions. A virtual shard is just a range of keys with a label. No extra hardware, no extra cost, no performance hit. You're just deciding in advance how the key space is divided.

Now, two years later, your traffic has 10x'd and Server A is overwhelmed. You add Server E. Instead of a row-level migration, you simply reassign ownership of some virtual shards:

```
Server A was: shards 1–64
Move shards 1–50 to Server E → Server E now owns those shards
Server A now: shards 51–64 only (much lighter load)
```

The data for shards 1–50 physically copies from Server A to Server E once — as a whole shard, not row by row. Once copied, routing updates and Server E starts serving those keys. Server A is immediately relieved.

No row-level migration. No query routing confusion. No double-write complexity. Just move the whole shard as a unit.

Compare this to if you had only created 4 shards upfront:

```
4 shards, need to split Shard 1 into two halves:
→ which rows go left half? which go right?
→ copy half the rows to new shard while writes are landing
→ routing is ambiguous during migration
→ dangerous, complex, slow
```

With 256 virtual shards you never split a shard — you just move whole shards to new servers. The hard problem (splitting) is replaced with the easy problem (moving).

> [!important] Over-sharding upfront is cheap. Emergency resharding under load is not.
> Adding 256 virtual shards at design time costs nothing. Running a live row-level migration at 3am under production traffic is catastrophic. Always over-shard upfront — it is the single best resharding decision you can make before launch.

---

## Strategy 2 — Double writes during migration

For systems that must scale incrementally without downtime:

```
Migration window:
  Step 1 → start writing to both old shard and new shard (double write)
  Step 2 → backfill: copy existing data from old shard to new shard
  Step 3 → reads: check new shard first, fall back to old shard on miss
  Step 4 → once backfill complete and verified, stop writing to old shard
  Step 5 → remove old shard from routing
```

Reads always return correct data because they fall back to the old shard during the migration window. Writes land in both places so nothing is lost even if the migration is paused.

The risk is the complexity of running this migration logic in production — bugs in the double-write path can cause inconsistencies.

---

## Strategy 3 — Maintenance window (simplest, has downtime)

Pause all writes briefly during the cutover:

```
1. Put system in read-only mode
2. Migrate data to new sharding topology
3. Verify migration complete
4. Resume writes on new topology
```

Simple and safe but requires downtime — unacceptable for consumer products, acceptable for internal tools or systems with maintenance windows.

---

## Summary

```
Resharding pain comes from: moving rows while writes are happening
                             query routing confusion during migration

Strategy 1 — Over-shard upfront
  Start with 256 virtual shards on 4 servers
  Add servers by moving whole virtual shards, not individual rows
  Best option: plan for it before you launch

Strategy 2 — Double writes
  Write to old + new during migration
  Read from new, fallback to old
  No downtime, more complex

Strategy 3 — Maintenance window
  Pause writes, migrate, resume
  Simple, requires downtime
```

> [!tip] Interview framing
> "I'd over-shard upfront — start with 256 virtual shards mapped to however many physical servers we have today. When we need to scale, we add servers and move whole virtual shards to them. This avoids live row-level migration entirely."
