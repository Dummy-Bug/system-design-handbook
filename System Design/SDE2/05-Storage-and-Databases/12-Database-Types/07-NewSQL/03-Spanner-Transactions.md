
## How transactions work on top of TrueTime

TrueTime gives Spanner a globally ordered timestamp for every transaction. But ordering alone doesn't prevent conflicts — it just establishes who came first. The transaction layer on top handles correctness.

---

## The conflict scenario

Alice has $100. She simultaneously tries to send $100 to Bob and $50 to Charlie — two separate transactions initiated at nearly the same moment from two different data centers.

Without conflict detection, both transactions could read Alice's balance as $100, both could succeed, and Alice would end up with -$50. That's unacceptable.

---

## How Spanner handles it

Spanner uses **optimistic concurrency control** for read-write transactions.

Each transaction reads data, does its work, then at commit time checks: "has anything I read changed since I started?" If yes — conflict detected, one transaction rolls back. If no — safe to commit.

TrueTime establishes the order: whichever transaction gets the earlier commit timestamp wins.

```
Alice → Bob   $100  (commits first — timestamp 10:00:00.009)
→ Alice balance was $100, now $0. Committed.

Alice → Charlie $50  (commits second — timestamp 10:00:00.010)
→ Reads Alice balance: $0
→ $0 < $50 — constraint violation → rollback
```

Alice's money is safe. The ordering from TrueTime determined which transaction won. ACID holds.

---

## Row-level locking

Spanner locks at the **row level**. Two transactions touching different rows proceed in parallel with no interference. Two transactions touching the same row — one waits for the other.

```
Alice → Bob     (locks Alice's row + Bob's row)
Charlie → Dave  (locks Charlie's row + Dave's row)
→ No shared rows → no conflict → both commit in parallel ✓

Alice → Bob     (locks Alice's row)
Alice → Charlie (locks Alice's row)
→ Same row → one waits → one commits → other checks, detects conflict → rollback
```

Locking is at the row level, not the column level. Even if two transactions touch different columns of the same row, Spanner treats it as a conflict. This is conservative — occasionally causes unnecessary waiting — but it's simple and safe at global scale.

---

## The full transaction flow

```
1. Transaction starts → Spanner records a start timestamp (TrueTime)
2. Transaction reads rows → takes read locks
3. Transaction writes → buffers writes locally (not yet applied)
4. Commit time:
   → Spanner acquires write locks on affected rows
   → Calls TrueTime.now() → gets uncertainty window
   → Waits out the uncertainty window (commit-wait)
   → Applies buffered writes with the commit timestamp
   → Releases locks
5. Other transactions that were waiting now proceed
   → If they read a row that changed, they detect the conflict and rollback
```

---

## What Spanner gives you

```
✓ Full ACID transactions — across any number of rows, any number of data centers
✓ Serializable isolation — transactions appear to execute one at a time
✓ External consistency — global real-world ordering guaranteed
✓ Horizontal scale — add nodes, Spanner reshards automatically
✓ Global distribution — data replicated across regions, reads served locally
```

---

## What Spanner costs you

```
✗ Latency — commit-wait adds 1-7ms per transaction
✗ Cost — atomic clocks and GPS hardware in every data center is expensive
✗ Complexity — you're trusting Google's infrastructure completely
✗ Not open source — Spanner is Google Cloud only
```

For most systems, Postgres is simpler and cheaper. Spanner is for when you've genuinely outgrown everything else and consistency cannot be compromised.

> [!danger] Common interview trap
> Don't mention Spanner for every globally distributed system. Eventual consistency (Cassandra, DynamoDB) is fine for social feeds, notifications, counters. Spanner is only necessary when strong consistency is non-negotiable — payments, financial ledgers, inventory that cannot oversell.
