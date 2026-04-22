
> [!info] Sequence numbers solve the physical time problem — but per-user sequence numbers don't solve the interleaving problem
> A sequence number is a logical counter. It has nothing to do with clocks. But the scope of the counter matters enormously.

---

## Why sequence numbers are better than timestamps

A sequence number is assigned by a single atomic counter. There is no clock involved, no network latency measurement, no NTP drift. The counter just increments:

```
Message 1 → seq=1
Message 2 → seq=2
Message 3 → seq=3
```

The ordering is unambiguous. `seq=2` always comes after `seq=1`. No two messages can have the same sequence number. The time machine problem disappears — not because we measured time more accurately, but because we stopped measuring time at all.

---

## The per-user counter approach

The natural first implementation: give each user their own counter. Alice has a counter. Bob has a counter. Each increments independently.

```
Alice's counter: 1, 2, 3, 4...
Bob's counter:   1, 2, 3, 4...
```

Alice sends "hey" → seq_alice=1
Alice sends "you there" → seq_alice=2
Bob sends "hi" → seq_bob=1
Alice sends "hello??" → seq_alice=3

Within Alice's messages, ordering is perfect. Within Bob's messages, ordering is perfect. But when you try to interleave them into a single conversation timeline:

```
seq_alice=1  "hey"
seq_alice=2  "you there"
seq_bob=1    "hi"           ← where does this go? seq_bob=1 and seq_alice=1 are incomparable
seq_alice=3  "hello??"
```

You have two independent counters with no relationship to each other. `seq_bob=1` and `seq_alice=1` are both "1" — but which one happened first in real time? You're back to needing a timestamp to break the tie between Alice's messages and Bob's messages.

---

## The problem in plain terms

Per-user sequence numbers solve ordering within a single sender's messages. They tell you nothing about the ordering between different senders' messages. To build a conversation timeline, you need to interleave messages from multiple senders — and for that, the counter needs to span all senders, not just one.

The fix is to change the scope of the counter from per-user to per-conversation.
