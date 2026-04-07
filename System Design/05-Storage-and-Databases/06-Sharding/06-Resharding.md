# Resharding

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

Start with far more shards than you need on day one — say 256 shards — even if you only have 4 physical servers. Map multiple virtual shards to each physical server:

```
Day 1 (4 servers):
  Server A → virtual shards 1–64
  Server B → virtual shards 65–128
  Server C → virtual shards 129–192
  Server D → virtual shards 193–256

When you add Server E:
  Move virtual shards 1–50 from Server A to Server E
  → entire virtual shard moves as a unit
  → no row-level migration, just reassigning ownership
  → Server A now handles shards 51–64, Server E handles 1–50
```

No row-level migration. You're moving ownership of whole shards, not individual rows. The data physically copies once per virtual shard, not once per row. Far safer and faster.

> [!important] Over-sharding upfront is cheap. Emergency resharding under load is not.
> Adding virtual shard capacity costs almost nothing at design time. Running an emergency live migration at 3am under production load is catastrophic. Always over-shard upfront.

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
