
> [!info] The core idea
> Raft only tells the client "success" after a majority of nodes have the write. This single rule is what makes committed data safe across every failure scenario.

---

## How a write works in Raft

Every write goes through exactly these steps before the client gets a response:

```
Step 1 → Leader writes entry to its own WAL (uncommitted)
Step 2 → Leader sends entry to followers via AppendEntries RPC
          Followers write entry to their WAL (uncommitted)
Step 3 → Leader receives majority acks → marks entry committed in its WAL
Step 4 → Leader applies entry to state machine
Step 5 → Leader replies "success" to client
Step 6 → Leader sends commit notification to followers → they commit + apply too
```

The client only hears "success" at Step 5 — after majority has the entry and the leader has committed. This is the guarantee everything else is built on.

---

## Case 1 — Leader crashes before replicating (between Step 1 and Step 2)

Leader wrote to its own WAL but crashed before sending to any follower. No follower has any trace of this entry.

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Leader (A)
    participant B as Follower B
    participant C2 as Follower C

    C->>A: Write request
    A->>A: Write to WAL (uncommitted)
    Note over A: Crashes here ✗
    Note over B,C2: No entry at all
    B->>B: Timeout → start election (Term 2)
    B-->>C2: Request vote
    C2-->>B: Vote granted
    Note over B: New leader (Term 2)
    A->>A: Comes back → sees Term 2 → steps down as follower
    B->>A: Sync → A's uncommitted entry discarded
```

**Result:** Entry discarded. Client got no response, so it retries. Idempotency handles the duplicate.

---

## Case 2 — Leader crashes after replicating but before committing (between Step 2 and Step 3)

Leader sent the entry to followers. Followers wrote it to their WAL as uncommitted. Leader crashes before getting majority acks.

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Leader (A)
    participant B as Follower B
    participant C2 as Follower C

    C->>A: Write request
    A->>A: Write to WAL (uncommitted)
    A->>B: AppendEntries (uncommitted)
    A->>C2: AppendEntries (uncommitted)
    B->>B: Write to WAL (uncommitted)
    C2->>C2: Write to WAL (uncommitted)
    Note over A: Crashes before getting acks ✗
    B->>B: Timeout → start election (Term 2)
    B-->>C2: Request vote
    C2-->>B: Vote granted
    Note over B: New leader (Term 2)
    Note over B: Sees uncommitted entry in WAL
    Note over B: Majority has it → safe to auto-commit
    B->>B: Commits entry
    B->>C2: Commit notification → C2 commits
    A->>A: Comes back → B syncs A → A commits too
```

**Result:** Entry is saved. New leader sees the uncommitted entry on majority nodes and auto-commits it. Client retries (got no response) — idempotency handles the duplicate.

> [!important] Why can the new leader auto-commit?
> Because it was elected by majority — meaning majority already has this entry in their WAL. It's safe to commit because the data won't disappear even if another node fails.

---

## Case 3 — Leader crashes after committing but before notifying followers (between Step 5 and Step 6)

Leader committed the entry and replied "success" to the client. Was about to send the commit notification to followers — crashes right here. Followers still have the entry as uncommitted.

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Leader (A)
    participant B as Follower B
    participant C2 as Follower C

    C->>A: Write request
    A->>A: Write to WAL (uncommitted)
    A->>B: AppendEntries
    A->>C2: AppendEntries
    B->>B: Write to WAL (uncommitted)
    C2->>C2: Write to WAL (uncommitted)
    B-->>A: ACK
    C2-->>A: ACK
    A->>A: Majority acks → commits entry
    A-->>C: "success"
    Note over A: Crashes before sending commit notification ✗
    B->>B: Timeout → start election (Term 2)
    Note over B: New leader (Term 2)
    Note over B: Sees uncommitted entry on majority → auto-commits
    B->>C2: Commit notification → C2 commits
    A->>A: Comes back → B syncs A → A commits too
```

**Result:** Identical outcome to Case 2. New leader auto-commits the pending entry. Client already got "success" and does not retry.

---

## The pattern across all three cases

| When leader crashes | Followers have | Outcome |
|---|---|---|
| Before replicating (Step 1→2) | Nothing | Entry discarded. Client retries. |
| After replicating, before commit (Step 2→3) | Uncommitted entry on majority | New leader auto-commits. Client retries harmlessly. |
| After committing, before notifying (Step 5→6) | Uncommitted entry on majority | New leader auto-commits. Client already got success. |

> [!important] Committed data is never lost
> "Committed" in Raft means majority acknowledged the entry. The new leader is always elected from majority — so committed data always survives, even permanent leader failure. The only exception is losing more than ⌊N/2⌋ nodes permanently at the same time.

---

## What if a follower missed some entries?

Say Follower C was down during several writes and just came back. Its log is behind.

```
Leader:     [1, 2, 3, 4, 5, 6]
Follower C: [1, 2, 3, 4]

Follower C rejects index 6 → "I only have up to index 4"
Leader → sends index 5 → C applies → sends index 6 → C applies
Follower C: [1, 2, 3, 4, 5, 6] ✓
```

Followers never skip entries. They always catch up sequentially. No gaps allowed — ever.
