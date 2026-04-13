
> [!info] The core idea
> Redis can also be used for distributed locks — simpler and faster than ZooKeeper. But because Redis uses async replication, there is a failure window where two processes can simultaneously believe they hold the lock.

---

## Redis as a distributed lock

Redis has a command called `SETNX` — **SET if Not eXists**. Same race as ZooKeeper's ephemeral node — first one to set the key wins the lock.

```
App Server A → SETNX /leader "A" with TTL 30s
→ succeeds → A is the leader

App Server B → SETNX /leader "B"
→ fails → /leader already exists → B waits
```

TTL handles the "what if A dies" case — lock automatically expires after 30 seconds, someone else can acquire it. No watches, no push notifications — servers poll Redis periodically to check if the lock is free.

Simple, fast, works well in most cases.

---

## The edge case where Redis fails

Redis replication is **asynchronous**. When you write to the Redis leader, it stores the value in memory and tells you "success" — before the follower has received the data.

```
A → SETNX /leader → Redis Leader → "success, you have the lock"
Redis Leader hasn't replicated to follower yet
Redis Leader crashes right here ✗
```

Follower gets promoted to new leader. But the follower never received the lock entry — it arrived after the crash. From the new leader's perspective, `/leader` doesn't exist at all.

```
Redis Leader crashes → follower promoted
Follower memory: /leader = (empty) ← never arrived

App Server B → SETNX /leader → new Redis leader → "success, you have the lock"
```

Now both A and B believe they hold the lock. Split-brain. Two writers. Data corrupted.

> [!danger] This is not a theoretical edge case
> This happens in production during Redis failovers. The window is small but real — any async replication gap is a correctness risk under the right failure timing.

---

## Why Redis can't just check the WAL

A natural instinct here: "couldn't the new Redis leader check its WAL for uncommitted writes and recover A's lock?"

Redis doesn't work this way. Redis is an **in-memory store**. It does have an AOF (Append Only File) log on disk — but that's for crash recovery of the **same node**, not for replication.

Redis replication sends a stream of commands to followers asynchronously. If the leader crashes before the stream reaches the follower, the follower simply never received the command. There is no uncommitted entry sitting anywhere. No record at all.

```
Leader memory:   /leader = A  ← only lives here
Follower memory: (empty)      ← stream never arrived

Leader crashes → follower promoted → /leader doesn't exist → lock gone
```

This is fundamentally different from Raft, where a write is only confirmed after majority nodes have it in their WAL. In Raft there is always a durable record on majority nodes before the client gets "success." In Redis there is no such guarantee.

---

## Redlock — Redis's attempt to fix this

Redis's creator (Salvatore Sanfilippo) designed an algorithm called **Redlock** to address this. The idea: instead of writing to one Redis instance, acquire the lock on a **majority of independent Redis nodes** simultaneously.

```
5 independent Redis nodes (no replication between them)

A tries to acquire lock on all 5:
→ Node 1: success
→ Node 2: success
→ Node 3: success   ← majority (3/5) acquired
→ Node 4: timeout
→ Node 5: timeout

A holds the lock — majority confirmed
```

Even if one node crashes, majority still has the lock. No single point of failure.

> [!danger] Redlock is controversial
> Martin Kleppmann (author of Designing Data-Intensive Applications) wrote a famous critique arguing Redlock still has edge cases — specifically around process pauses and clock drift across nodes. His conclusion: if you need correctness guarantees, use ZooKeeper. Use Redlock only if you can tolerate occasional lock conflicts.

---

## Redis vs ZooKeeper — when to use which

| | Redis | ZooKeeper |
|---|---|---|
| Speed | Very fast (in-memory) | Slower |
| Replication | Async — gap possible | Consensus — majority ack before success |
| Push notifications | No — callers poll | Yes — watches push to callers |
| Built for coordination | No — cache first | Yes — purpose-built |
| Failure safety | Weaker | Stronger |
| Operational simplicity | Simple | More complex to operate |

**Use Redis when:** you need speed and can tolerate very rare lock conflicts. Most applications with short lock durations and low failure rates are fine here.

**Use ZooKeeper / etcd when:** correctness is non-negotiable. Financial transactions, primary DB election, anything where two simultaneous lock holders would cause serious damage.

> [!tip] Interview framing
> "For distributed locks, Redis SETNX works well for most cases but has an async replication gap during failover. If correctness is critical, ZooKeeper or etcd are safer because they use consensus — a write is only confirmed after majority nodes have it, so there's no gap during leader failover."
