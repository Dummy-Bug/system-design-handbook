# ACID — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of ACID properties, the WAL, and why each guarantee exists. Every SDE candidate is expected to answer these confidently and concretely.

---

> [!question] What is ACID? What does each letter stand for?

> [!success]- Answer
>
> **A — Atomicity** — all or nothing. Every operation in a transaction succeeds together, or none of them happen. No partial state ever persists.
>
> **C — Consistency** — the database always moves from one valid state to another valid state. No transaction can leave the database in a state that violates its own rules (constraints, foreign keys, business rules).
>
> **I — Isolation** — two concurrent transactions must feel like they're executing independently. One transaction cannot see the partial state of another mid-execution.
>
> **D — Durability** — once a transaction is committed, that data survives permanently. Crashes, power loss, hardware failure — none of it can undo a committed transaction.
>
> > [!important] The key distinction between A and D
> > Atomicity covers crashes **during** a transaction — if something goes wrong mid-way, roll back to clean state. Durability covers crashes **after** commit — once committed, the data is permanent. Same WAL mechanism, different job.
>
> > [!tip] Interview framing
> > *"ACID is a set of four guarantees that ensure database transactions are reliable. Atomicity — all or nothing. Consistency — valid state to valid state. Isolation — concurrent transactions don't interfere. Durability — committed data survives permanently, including crashes and power loss."*

---

> [!question] Why does ACID matter? Give me a real-world example where violating even one property causes a visible problem for the user.

> [!success]- Answer
>
> The strongest single example is a bank transfer — it touches all four properties and the failure mode is immediately visible to the user.
>
> **Atomicity violated:**
> ```
> Alice sends $100 to Bob
> → debit Alice succeeds
> → server crashes before crediting Bob
> → Alice loses $100, Bob gets nothing
> → user sees money gone with no explanation
> ```
>
> Each property has a distinct failure mode:
> ```
> Atomicity broken   → partial transfer — money debited, never credited
> Consistency broken → account balance goes negative (violates DB constraint)
> Isolation broken   → two users book the last hotel room simultaneously, both get a confirmation
> Durability broken  → payment succeeds, server crashes, transaction lost on restart
> ```
>
> > [!tip] Interview framing
> > *"Take a bank transfer — debit Alice, credit Bob. Atomicity ensures both happen or neither does. Consistency ensures balances can't go negative. Isolation ensures two transfers on the same account don't interfere. Durability ensures a confirmed transfer isn't lost if the server crashes a second later."*

---

> [!question] What is the WAL and why does every ACID-compliant database need one?

> [!success]- Answer
>
> WAL stands for **Write-Ahead Log**. It is an append-only file on disk where every change is recorded **before** it is applied to the actual data files. "Write-ahead" means the log always precedes the action — you write to the log first, then apply the change.
>
> ```
> Transaction starts
>   → WAL entry: "about to deduct $100 from Alice (current: $500)"
>   → deduct $100 from Alice in data file
>   → WAL entry: "about to add $100 to Bob (current: $300)"
>   CRASH ← before credit applied
>
> On restart:
>   → DB reads WAL
>   → finds incomplete transaction (no COMMIT marker)
>   → uses WAL entry to reverse: Alice restored to $500
>   → clean state ✓
> ```
>
> The WAL is what makes both atomicity and durability possible:
> - **Atomicity** — uses WAL to undo incomplete transactions on crash (rollback)
> - **Durability** — uses WAL to redo committed transactions on crash (recovery)
>
> Without the WAL, a crash mid-transaction would leave the database in corrupt partial state with no way to recover.
>
> > [!tip] Interview framing
> > *"The WAL is an append-only log where every change is written before it's applied to actual data. It's needed because if the server crashes mid-transaction, in-memory changes are lost — the WAL survives on disk. On restart, the DB replays the WAL: committed transactions are redone, incomplete ones are rolled back."*

---

> [!question] What is the difference between atomicity and durability? They both seem to deal with crashes — convince me they're separate guarantees.

> [!success]- Answer
>
> They use the same mechanism (the WAL) but protect against completely different failure scenarios:
>
> ```
> Atomicity  → crash DURING transaction  → rollback, clean state, as if it never happened
> Durability → crash AFTER commit        → data survives, committed state is permanent
> ```
>
> **Atomicity** is about incomplete work — if a transaction is only halfway done when the server dies, atomicity ensures the partial changes are reversed. The WAL records what was done so it can be undone.
>
> **Durability** is about completed work — if a transaction fully committed and then the server dies, durability ensures that committed data is still there on restart. The WAL records the commit so it can be replayed.
>
> Same WAL, opposite direction:
> ```
> Incomplete transaction → WAL used to UNDO  (atomicity)
> Committed transaction  → WAL used to REDO  (durability)
> ```
>
> > [!tip] Interview framing
> > *"Atomicity deals with crashes during a transaction — roll back to clean state. Durability deals with crashes after commit — the committed state is permanent. Same WAL mechanism, different job: atomicity uses it to undo incomplete work, durability uses it to redo committed work."*

---

> [!question] What is fsync and why does turning it off break the D in ACID?

> [!success]- Answer
>
> When the database tells the OS to write to disk, the OS doesn't do it immediately. It puts the data in a **RAM buffer** and says "done ✓" — because batching writes is faster. The database thinks the write succeeded, but the data is still in RAM.
>
> ```
> Without fsync:
> DB → "write WAL to disk" → OS → RAM buffer → "done ✓"  ← OS is lying
>                                       ↓ maybe later → actual disk
> ```
>
> `fsync()` forces the OS to flush the RAM buffer to physical disk before returning success. The database blocks and waits until the data has physically hit the disk — this forced round-trip is what makes writes feel slow.
>
> ```
> With fsync:
> DB → "write WAL to disk" → OS → RAM buffer → fsync() → physical disk → "done ✓"
> ```
>
> With `fsync=off`, a power cut wipes RAM entirely — the OS buffer is gone, the WAL entry is gone, and a transaction the user was told succeeded is permanently lost.
>
> > [!important] Process crash vs power cut
> > A process crash leaves the OS still running — the OS buffer survives and will eventually flush to disk. A power cut wipes all RAM instantly — OS buffer, MemTable, everything gone simultaneously. `fsync=off` often survives process crashes in practice, but has zero protection against power loss.
>
> ```
> Process crash + fsync=off  → risky but often survives (OS still running, flushes eventually)
> Power cut    + fsync=off  → guaranteed data loss (RAM wiped, nothing left to flush)
> Power cut    + fsync=on   → safe (data was on disk before commit returned)
> ```
>
> > [!danger] Never turn off fsync for financial or transactional data
> > `fsync=off` is fine for a throwaway test environment. In production it completely breaks the D in ACID — a power cut will silently lose committed transactions.
>
> > [!tip] Interview framing
> > *"The OS buffers disk writes in RAM for performance — it lies to the database saying 'done' before the data hits disk. fsync forces the OS to flush to physical disk before returning. With fsync=off, a power cut wipes the OS buffer and any committed-but-not-flushed WAL entries are lost permanently — the D in ACID is gone."*
