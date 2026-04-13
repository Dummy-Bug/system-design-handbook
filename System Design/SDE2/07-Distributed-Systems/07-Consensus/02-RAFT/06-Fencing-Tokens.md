
> [!info] The core idea
> Term numbers protect you inside the Raft cluster. Fencing tokens protect you outside it — when a stale process tries to write to an external system that has no idea what a term number is.

---

## The problem term numbers can't solve

Inside Raft, when an old leader comes back after a partition, it sees a higher term number and steps down. Problem solved.

But now consider a different setup. You have a **single shared database** — just a regular MySQL. Multiple app servers want to write to it. To avoid conflicts, they use a **distributed lock** — only one app server holds the lock at a time, and only the lock holder is allowed to write.

```
App Server A ── holds lock ──▶ MySQL (writes allowed)
App Server B ── waiting   ──▶ MySQL (blocked)
App Server C ── waiting   ──▶ MySQL (blocked)
```

This works fine — until App Server A freezes. GC pause, slow disk flush, whatever. It goes unresponsive for 30 seconds.

The lock has a timeout. After 10 seconds of no activity, the lock service assumes A is dead and hands the lock to App Server B. B starts writing to MySQL.

Then A unfreezes. It has no idea the lock expired. It still believes it's the lock holder. It resumes its write to MySQL.

```
App Server A → writes to MySQL  ← thinks it still holds the lock
App Server B → writes to MySQL  ← actually holds the lock
```

MySQL sees two concurrent writers. It doesn't know anything about locks or Raft terms. It accepts both writes. Data corrupted.

> [!danger] Term numbers don't help here
> MySQL doesn't speak Raft. It has no concept of terms or epochs. The protection that works inside the Raft cluster simply doesn't exist at the external storage layer.

---

## The fix — fencing tokens

When the lock service grants a lock, it hands the app server a **fencing token** — a monotonically increasing integer. Every new lock grant gets a higher number than the previous one. It never goes backwards.

```
App Server A gets lock → token = 5
A freezes → lock expires
App Server B gets lock → token = 6
```

Now the rule: **every write to MySQL must include the token**. And MySQL has one simple job — remember the highest token it has seen, and reject any write carrying a lower token.

```
App Server B → writes to MySQL with token = 6
MySQL remembers: highest token seen = 6 ✓

App Server A unfreezes → writes to MySQL with token = 5
MySQL: "I already saw token 6 — token 5 is stale"
MySQL → rejects the write ✗
```

App Server A gets rejected at the storage layer itself. No coordination needed between A and B. MySQL doesn't need to know anything about locks or Raft — just one integer comparison.

> [!important] The storage system enforces the fencing, not the lock holder
> You can't rely on the stale process to behave correctly — it genuinely doesn't know it's stale. The check must happen at the resource being written to. That's the whole point of fencing.

---

## Why this is the same idea as optimistic locking

If you've seen optimistic locking in databases — this is the exact same pattern.

In optimistic locking: you read a row, get its version number, write back with that version, and the database rejects the write if the version changed underneath you. Someone else updated the row between your read and your write — your version is stale, rejected.

Fencing tokens work identically — just at the **lock level** instead of the **row level**.

| | Optimistic Locking | Fencing Token |
|---|---|---|
| Number attached to | A specific row | A lock grant |
| Protects | One record | Whatever the lock guards |
| Rejection condition | Version changed | Token is lower than highest seen |
| Core mechanism | Same | Same |

Both say the same thing: include a number that proves you saw the latest state. If you're behind, you get rejected.

---

## Where fencing tokens appear in practice

The pattern shows up under different names across distributed systems:

- Raft calls the epoch counter a **term number** (inside the cluster)
- ZooKeeper calls its epoch counter a **zxid**
- Distributed lock services issue **fencing tokens** to lock holders
- The general concept — monotonically increasing number, stale writer gets rejected — is called a **fencing token** or sometimes a **generation number**

Whenever you see a monotonically increasing number being passed around and checked before a write, you're looking at this pattern.

---

→ Next: [[01-ZooKeeper-Election]] — how ZooKeeper uses this same idea to manage leader election across services
