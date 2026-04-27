
> [!info] When two clients have different clocks, replies can appear before the original message
> This is not a theoretical edge case. It happens whenever two users' phones have drifted clocks — and the result looks like a time machine.

---

## The scenario

Alice and Bob are in a conversation. Both are using client-generated timestamps. Their phone clocks are not in sync.

```
Alice's clock: correct   → 4:20 PM
Bob's clock:   10 min behind → 4:10 PM
```

Alice sends "hey" at what her phone says is 4:20:

```
m1: sender=Alice, content="hey", timestamp=4:20:00
```

Bob receives it, reads it, and replies "hi" at what his phone says is 4:10 (because his clock is behind):

```
m2: sender=Bob, content="hi", timestamp=4:10:00
```

Now Alice's client receives Bob's reply. It sorts the conversation by timestamp:

```
m2 → "hi"   — 4:10:00   ← appears FIRST
m1 → "hey"  — 4:20:00   ← appears SECOND
```

Bob's reply to Alice's "hey" appears **10 minutes before** Alice's original message. A reply before the question. Causality broken.

```
Bob: "hi"     ← 4:10 PM
Alice: "hey"  ← 4:20 PM
```

People say time machines are impossible. Client timestamps beg to differ.

---

## Why this is worse than just visual noise

In the single-sender case (network reordering of Alice's own messages), the timestamps are all from the same clock — so sorting by timestamp still produces the right relative order. Wrong absolute time, but correct relative order.

In the two-sender case, you have two independent clocks that have no obligation to agree with each other. The relative order between Alice's messages and Bob's messages can be completely inverted. No amount of sorting helps — the timestamps themselves are wrong relative to each other.

---

## The fix direction

Client timestamps cannot be used for ordering across different senders. The ordering signal must come from somewhere that has a single, authoritative view of time — not from the devices themselves.

The obvious next idea: **let the server assign the timestamp when it receives the message.** The server is in the datacenter, running NTP, with a reliable clock. Surely server-assigned timestamps fix this?

They help — but they introduce a different problem. Covered next.
