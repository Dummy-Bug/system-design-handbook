
> [!info] Message ordering is not guaranteed by the network
> Sending three messages in order does not mean they arrive in order. The network doesn't care about your sequence — it routes each packet independently.

---

## What happens when Alice sends three messages rapidly

Alice hits send three times in quick succession:

```
Alice sends:
  m1 → "hey"        T=100ms
  m2 → "you there"  T=101ms
  m3 → "hello??"    T=102ms
```

Each message travels as an independent request over the network. The network routes each one separately — different paths, different hops, different congestion points. There is no guarantee that a packet sent first arrives first.

Bob receives:

```
Bob receives:
  m3 → "hello??"    (arrived first)
  m1 → "hey"        (arrived second)
  m2 → "you there"  (arrived third)
```

If Bob's client displays messages in arrival order, the conversation looks broken:

```
"hello??"
"hey"
"you there"
```

A reply before the original message. Confusing and wrong.

---

## Why this happens

The internet is a packet-switched network. Every message takes its own route. A message sent 1ms later might find a faster path and overtake the earlier message. A message sent first might hit a congested router and arrive last.

This is not a bug. It is the fundamental nature of how the internet works. The job of the application layer is to detect and correct this reordering before showing it to the user.

---

## The naive fix — sort at the receiver

The first instinct is: sort the messages before displaying them. If each message carries some kind of timestamp or sequence indicator, the receiving client can reorder them into the correct sequence regardless of arrival order.

```
Bob receives in order: m3, m1, m2
Bob sorts by timestamp: m1, m2, m3
Bob displays: "hey" → "you there" → "hello??"
```

This works. The question is: **what do you sort by?** The answer is not obvious — and getting it wrong introduces a completely different class of bugs.
