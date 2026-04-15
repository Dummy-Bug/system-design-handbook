
> [!info] One counter per conversation — not per user
> The fix is simple once you see it: every message in a conversation, regardless of who sent it, pulls from the same counter.

---

## The deli counter analogy

Imagine a deli counter. There's one ticket machine. It doesn't matter if Alice takes a ticket or Bob takes a ticket — the machine gives out the next number to whoever pulls:

```
Alice pulls a ticket → gets 1
Bob pulls a ticket   → gets 2
Alice pulls a ticket → gets 3
Bob pulls a ticket   → gets 4
```

The order of tickets is the order of arrivals. Not Alice's order. Not Bob's order. The global order for everyone at that counter.

This is exactly what a per-conversation sequence number does. The "deli counter" is a single atomic counter keyed to `conversation_id`. Every message — from Alice or Bob — pulls the next number from that counter.

---

## How it solves the interleaving problem

```
conv_abc123 counter starts at 0

Alice sends "hey"        → INCR → gets seq=1
Bob sends "hi"           → INCR → gets seq=2
Alice sends "how are you"→ INCR → gets seq=3
Bob sends "good!"        → INCR → gets seq=4
```

Now the conversation timeline is unambiguous:

```
seq=1  Alice: "hey"
seq=2  Bob:   "hi"
seq=3  Alice: "how are you"
seq=4  Bob:   "good!"
```

Both Alice's client and Bob's client sort by `seq`. They see the identical timeline. No timestamps. No clock drift. No time machine. Just a counter that increments.

---

## What "per conversation" means

The counter is scoped to a `conversation_id`. A conversation is the unique pair (Alice, Bob) — the same pair they've always had, regardless of whether they've deleted history or logged out. `conversation_id` is permanent and unique to the pair.

This means:
- Alice and Bob's conversation has its own counter, completely independent of any other conversation
- If Alice is in 50 conversations, each one has its own counter
- The counter for conv_abc123 tells you nothing about the order of messages in conv_def456 — nor should it

> [!tip] Interview framing
> "I'd use a per-conversation sequence number — a single atomic counter per conversation_id. Every message from any sender in that conversation pulls the next number. Clients sort by seq. This eliminates all clock skew and drift from the ordering problem entirely."
