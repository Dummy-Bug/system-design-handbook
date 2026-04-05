# Transaction Isolation — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of isolation problems, isolation levels, and the cost of each. Every SDE candidate is expected to answer these confidently.

---

## Q1 — What Is a Dirty Read?

> [!question] What is a dirty read? Give me a concrete example with a bank transfer.

> [!success]- Answer
>
> **Dirty read:**
> Reading data that another transaction has written but not yet committed. If that transaction rolls back, you read data that never officially existed.
>
> **Bank transfer example:**
> ```
> Account A: $1000, Account B: $500
>
> Transaction 1 — transferring $200 from A to B:
>   Step 1: Deduct $200 from A → A = $800 (uncommitted)
>   Step 2: [crash happens, transaction rolls back]
>
> Transaction 2 — reads account balance mid-transfer:
>   Reads A = $800 (dirty read — this was never committed)
>   Shows user: "Your balance is $800"
>   Transaction 1 rolls back → A is actually $1000
>   User saw phantom money disappear
> ```
>
> **Why it's dangerous:**
> The read saw a state that never existed in the final committed history. Any decision made based on that read is potentially wrong.
>
> **Which isolation level prevents it:**
> ```
> READ UNCOMMITTED → dirty reads allowed
> READ COMMITTED   → dirty reads prevented ✓ (only see committed data)
> ```
>
> PostgreSQL's default is READ COMMITTED — dirty reads are never possible in Postgres.
>
> > [!tip] Interview framing
> > *"A dirty read is reading another transaction's uncommitted write. If that transaction rolls back, you read data that never existed. Prevented by READ COMMITTED — only see data after it's committed. PostgreSQL defaults to READ COMMITTED, so dirty reads never happen."*

---

## Q2 — Non-Repeatable Read and Phantom Read

> [!question] What is the difference between a non-repeatable read and a phantom read?

> [!success]- Answer
>
> **Non-repeatable read:**
> You read the same row twice within one transaction and get different values — because another transaction modified and committed it between your reads.
>
> ```
> Transaction A reads: SELECT balance FROM accounts WHERE id = 1 → $1000
>
> Transaction B runs: UPDATE accounts SET balance = $800 WHERE id = 1 → commits
>
> Transaction A reads again: SELECT balance FROM accounts WHERE id = 1 → $800
>
> Same row, different value within same transaction
> ```
>
> **Phantom read:**
> You run the same query twice and get different *rows* — because another transaction inserted or deleted rows matching your filter.
>
> ```
> Transaction A: SELECT COUNT(*) FROM orders WHERE user_id = 1 → 5 orders
>
> Transaction B: INSERT INTO orders (user_id, ...) VALUES (1, ...) → commits
>
> Transaction A: SELECT COUNT(*) FROM orders WHERE user_id = 1 → 6 orders
>
> Same query, different row count — a "phantom" row appeared
> ```
>
> **The key difference:**
> ```
> Non-repeatable read → same existing row changed between reads
> Phantom read        → different set of rows matched the query
> ```
>
> **Prevention:**
> ```
> READ COMMITTED    → prevents dirty reads only
> REPEATABLE READ   → prevents non-repeatable reads (and phantoms in PostgreSQL's implementation)
> SERIALIZABLE      → prevents all anomalies including phantoms
> ```
>
> > [!tip] Interview framing
> > *"Non-repeatable: same row, different value — another transaction modified it. Phantom: same query, different row count — another transaction inserted or deleted rows. REPEATABLE READ prevents non-repeatable reads. PostgreSQL's REPEATABLE READ (snapshot isolation) prevents phantoms too."*

---

## Q3 — The Four Isolation Levels

> [!question] Name the four transaction isolation levels from weakest to strongest. What does each one prevent?

> [!success]- Answer
>
> **From weakest to strongest:**
>
> | Level | Prevents | Notes |
> |---|---|---|
> | READ UNCOMMITTED | Nothing | Never use — reads uncommitted data |
> | READ COMMITTED | Dirty reads | PostgreSQL default |
> | REPEATABLE READ | Dirty reads + non-repeatable reads | MySQL default; snapshot isolation in PostgreSQL also prevents phantoms |
> | SERIALIZABLE | All four anomalies | Slowest — transactions behave as if fully sequential |
>
> **The four anomalies they address:**
> ```
> Dirty Read          → read uncommitted data (phantom money)
> Non-Repeatable Read → same row changes mid-transaction
> Phantom Read        → new rows appear mid-transaction
> Lost Update         → one write silently overwrites another
> ```
>
> **Important nuance — REPEATABLE READ in PostgreSQL:**
> PostgreSQL implements REPEATABLE READ as snapshot isolation. This gives each transaction a consistent snapshot of the entire database as of when it started — preventing phantom reads too. MySQL's REPEATABLE READ doesn't have this property.
>
> > [!important] Say "snapshot isolation" when discussing REPEATABLE READ with PostgreSQL. It shows you know what databases actually implement, not just the theoretical levels.
>
> > [!tip] Interview framing
> > *"Four levels weakest to strongest: READ UNCOMMITTED (avoid), READ COMMITTED (Postgres default, prevents dirty reads), REPEATABLE READ (prevents non-repeatable reads — and phantoms in Postgres via snapshot isolation), SERIALIZABLE (prevents all anomalies, slowest)."*

---

## Q4 — Default Isolation Level

> [!question] What isolation level does PostgreSQL use by default? What does that mean in practice?

> [!success]- Answer
>
> **PostgreSQL default: READ COMMITTED**
>
> In practice this means:
> ```
> ✓ Dirty reads prevented — you only see committed data
> ✗ Non-repeatable reads possible — same row can return different values in same txn
> ✗ Phantom reads possible — query results can change within same txn
> ✗ Lost updates possible without explicit locking
> ```
>
> **What this looks like in a real scenario:**
> ```
> Transaction: generate invoice (reads multiple tables)
>
> Step 1: SELECT price FROM products WHERE id = 1  → $50
> -- another transaction updates price to $60 and commits --
> Step 2: SELECT price FROM products WHERE id = 1  → $60
>
> Invoice was calculated with a price that changed mid-generation
> ```
>
> **When READ COMMITTED is fine:**
> Most CRUD operations — single reads, simple writes — are unaffected by this.
>
> **When you need more:**
> ```
> Multi-step reads that must be consistent → REPEATABLE READ
> Financial operations with complex logic  → SERIALIZABLE or explicit SELECT FOR UPDATE
> Generating a consistent report          → REPEATABLE READ or SET TRANSACTION SNAPSHOT
> ```
>
> > [!tip] Interview framing
> > *"PostgreSQL defaults to READ COMMITTED — you only see committed data, but the same row can return different values if another transaction commits between your reads. For multi-step operations that need a consistent view, I'd explicitly use REPEATABLE READ or add SELECT FOR UPDATE where needed."*

---

## Q5 — When to Use SERIALIZABLE

> [!question] When would you choose SERIALIZABLE isolation over using explicit SELECT FOR UPDATE locks?

> [!success]- Answer
>
> **SERIALIZABLE:**
> The database automatically detects conflicting access patterns and ensures transactions behave as if they ran one at a time — no anomalies possible.
>
> **SELECT FOR UPDATE:**
> You manually identify which rows need locking and add FOR UPDATE to those queries.
>
> **They achieve the same correctness goal — but for different teams and risk profiles:**
>
> **Use SERIALIZABLE when:**
> ```
> Team is junior or mixed experience
> → every developer must remember to add FOR UPDATE on every critical path
> → one missed FOR UPDATE = race condition = money lost
>
> Correctness is non-negotiable (medical, financial, legal data)
> → DB enforces safety automatically → no developer error possible
>
> Complex transaction logic
> → it's hard to identify ALL rows that need locking
> → SERIALIZABLE catches interactions you didn't think of
> ```
>
> **Use REPEATABLE READ + SELECT FOR UPDATE when:**
> ```
> Team is senior and experienced with locking
> High scale → SERIALIZABLE retry overhead is unacceptable
> Known, simple critical paths → easy to add FOR UPDATE in the right places
> ```
>
> **The cost of SERIALIZABLE:**
> ```
> DB detects conflicts → may abort and retry transactions automatically
> Under high contention → many retries → lower throughput
> FOR UPDATE is more predictable performance
> ```
>
> **Rule:**
> ```
> SERIALIZABLE    → safety net, correct by default, pay with performance
> FOR UPDATE      → surgical, higher performance, pay with developer discipline
> ```
>
> > [!tip] Interview framing
> > *"SERIALIZABLE is a safety net — the DB enforces correctness automatically, no developer can forget a lock. FOR UPDATE is surgical — correct if every developer remembers to use it on every critical path. For senior teams at scale, FOR UPDATE. For junior teams or highly critical correctness requirements, SERIALIZABLE."*
