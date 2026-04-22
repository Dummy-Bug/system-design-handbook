# Race Conditions

## What it is

> [!info] A race condition happens when two operations read and write the same data simultaneously, interfering with each other and producing a wrong result.

---

## The Classic Example — Last Pizza

```
Stock: 1 pizza remaining

User A reads:  stock = 1  ✓
User B reads:  stock = 1  ✓ (reads before A writes)
User A writes: stock = 0  (order placed)
User B writes: stock = 0  (order placed)

Result: 2 orders placed, 1 pizza exists → stock should be -1
```

Both users saw stock = 1. Both proceeded. Neither was wrong at the time of reading. But the result is wrong.

---

## Why It Happens

The problem is that **read and write are two separate operations** — not atomic. Another thread can sneak in between:

```
Thread A: READ  → [gap] → WRITE
Thread B:          READ  → WRITE

Both reads happen before either write → both see old value → both write
```

The fix — **make read + write atomic**. No thread can sneak in between.

---

## The Real World Impact

| System | Race Condition | Impact |
|---|---|---|
| E-commerce | Two users buy last item | Overselling — negative stock |
| Hotel booking | Two users book last room | Double booking |
| Bank transfer | Two withdrawals simultaneously | Balance goes negative |
| Ticket booking | Two users book last seat | Duplicate tickets issued |

> [!danger] Race conditions don't always reproduce in testing
> They depend on exact timing — milliseconds apart. They appear at scale under load and disappear when you add logging (which slows things down enough to prevent the race). This makes them one of the hardest bugs to debug.

---

## The Solution — Atomicity

Read and write must happen as one indivisible unit. Two approaches:

```
Pessimistic → lock the row before reading
              nobody else can read or write until you're done

Optimistic  → no lock, but verify version hasn't changed before writing
              if changed → someone else got there first → retry
```

Which approach to use depends on **contention** — how often two users fight over the same data simultaneously.

> [!tip] The contention question
> Before choosing a locking strategy always ask: *"How often will two users try to modify the same piece of data at the same time?"*
> - High contention → Pessimistic
> - Low contention → Optimistic
