
> [!info] The core idea
> When DB-1's ACCEPT gets rejected, it retries with a higher proposal number. What happens next depends entirely on how far the competing proposer got before the rejection. Two very different outcomes.

---

## Setup

DB-1 sent `ACCEPT(1, x=100)` — rejected because acceptors already promised N=2 to DB-2.

DB-1 now picks N=3 and goes back to Phase 1:

```
DB-1 → PREPARE(3) → all acceptors
```

What happens next splits into two cases.

---

## Case 1 — DB-2 was still in Phase 1 (never sent ACCEPT)

DB-2 collected promises for N=2 but hadn't sent `ACCEPT(2, x=999)` yet. The acceptors promised N=2 but never wrote any value.

Acceptors check: "Is 3 higher than 2?" Yes. They abandon their promise to DB-2 and switch to DB-1. Since no value was ever accepted, they report nothing:

```
DB-2 → PROMISE(3) + "nothing accepted yet"
DB-3 → PROMISE(3) + "nothing accepted yet"
```

DB-1 sees empty hands — no accepted values to inherit. It is free to propose its own value:

```
DB-1 → ACCEPT(3, x=100) → majority acks → x=100 committed ✓
```

DB-2 eventually tries `ACCEPT(2, x=999)` — acceptors already promised N=3. Rejected. DB-2 has to retry with N=4 or higher. But by then x=100 is committed, so the value inheritance rule forces DB-2 to use x=100 anyway.

> [!important] This only resolves cleanly if DB-1's ACCEPT goes through before DB-2 retries
> If DB-2 retries with N=4 before DB-1's ACCEPT(3) completes, DB-1 gets rejected again and picks N=5. That back-and-forth is exactly livelock — covered in [[04-Paxos-Livelock]].

---

## Case 2 — DB-2 already completed Phase 2 (x=999 committed on majority)

DB-2 sent `ACCEPT(2, x=999)` and got majority acks. x=999 is committed.

DB-1 sends `PREPARE(3)`. Acceptors promise N=3 — but this time they report what they already accepted:

```
DB-2 → PROMISE(3) + "I accepted (N=2, x=999)"
DB-3 → PROMISE(3) + "I accepted (N=2, x=999)"
```

DB-1 has majority promises. But it sees accepted values in the responses. The value inheritance rule kicks in.

> [!danger] Sneaky trap — DB-1 cannot propose x=100 now and "come back to x=999 later"
> A natural instinct: "DB-1 got majority promises, so it could first commit x=999 as a courtesy, then retry with x=100." This is completely wrong. The value inheritance rule is not a suggestion — it is a hard constraint. DB-1 must use x=999 **for this entire round**. It never gets another shot at x=100 in this retry. The client that sent x=100 gets no response and must start over as a brand new request from scratch.

DB-1 sends:

```
DB-1 → ACCEPT(3, x=999) → majority acks → x=999 re-confirmed ✓
```

DB-1 becomes the messenger that commits x=999 — even though it originally wanted x=100. DB-1 has no way of knowing whether x=999 was already committed on some nodes. Overwriting it with x=100 would destroy a value majority already agreed on. So the safe choice is always to preserve the highest accepted value.

---

→ See [[04-Paxos-Livelock]] for what happens when neither proposer wins and they keep racing forever
