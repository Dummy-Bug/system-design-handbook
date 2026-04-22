
> [!question] You launched with 4 shards. Two years later you need 5. Why is that so dangerous — and how does over-sharding fix it?

## The problem with starting with exactly the shards you need

Say you calculated you need 4 DB instances today. You spin up 4 machines, one DB instance per machine, done. Each shard owns a slice of the data.

Two years later traffic has grown and you need a 5th machine. You add Machine E. But now you have a problem — you have to **split** one of your existing shards.

```
Shard 1 has users 1–10 million all mixed together
→ split: users 1–5M stay on Shard 1, users 5M–10M move to Shard 5
→ while live writes are still landing on Shard 1
→ write for user 3M arrives mid-migration
   → does it go to Shard 1 or Shard 5?
   → routing is ambiguous during the entire migration window ✗
```

You have to go through every row, decide which rows stay and which move, copy selected rows to the new shard — all while production traffic is hitting that shard. This is dangerous custom code you have to write yourself, running on a live system.

---

## What over-sharding does

Instead of starting with 4 shards, you start with **256 shards** on day one — even though you only have 4 machines. Each machine runs 64 DB instances (as containers/pods), each container owning a slice of the data.

```
Machine A → 64 pods (shards 1–64)
Machine B → 64 pods (shards 65–128)
Machine C → 64 pods (shards 129–192)
Machine D → 64 pods (shards 193–256)
```

The app server addresses each pod directly. Kubernetes handles which physical machine each pod runs on — the app doesn't need to care.

```
App → shard-14.db.internal → Kubernetes routes to Machine A's pod
```

---

## Adding a 5th machine with over-sharding

Machine A is overwhelmed. You add Machine E. Kubernetes picks up some of Machine A's pods and reschedules them onto Machine E:

```
Before:
  Machine A → shards 1–64   (overwhelmed)

After:
  Machine A → shards 1–13   (relieved)
  Machine E → shards 14–64  (took A's excess)
```

The data for shards 14–64 copies from Machine A's disk to Machine E's disk — but as **whole shards**, not individual rows. Once the copy is complete, routing flips atomically. Shard 14 is either on Machine A or Machine E — never half-here half-there.

---

## Why moving a whole shard is safe but splitting is not

Both involve copying data. The difference is routing ambiguity.

```
Split (4 shards → 5):
  Open shard 1
  Go through every row
  Decide which rows stay, which rows move
  Copy selected rows to new shard
  While new writes are still landing
  → where does a mid-migration write go? ambiguous ✗

Move (256 shards, move shard 14):
  Copy entire shard 14 to Machine E
  Once copy is done → flip routing atomically
  → shard 14 is entirely on Machine E, done ✓
```

Think of it like moving a folder vs reorganising files across folders. Moving a folder is one atomic operation. Reorganising files while someone is actively adding new files to the folder is chaos.

Practically, databases have built-in tools for copying a whole instance — `pg_dump` for Postgres, `mysqldump` for MySQL. Copying a whole DB instance is a well-understood, safe operation. Splitting one instance's rows into two based on business logic while live traffic hits it is dangerous custom code.

---

> [!important] Over-sharding upfront is cheap. Splitting shards under live traffic is not.
> 256 pods instead of 4 sounds excessive. But each pod is small — it holds less data, uses less memory. The overhead is worth it. The alternative is writing a custom live-migration script at 3am while your production system is on fire.

> [!tip] Interview framing
> "I'd over-shard upfront — start with 256 shards mapped onto however many machines we have today. When we need to scale, we add machines and move whole shard instances to them. This replaces splitting (dangerous, ambiguous routing) with moving (safe, atomic ownership transfer)."
