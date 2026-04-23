
> [!info] The mutual rule — if you hide your read receipts, you lose everyone else's
> WhatsApp won't let you spy on others while hiding yourself. The trade-off is enforced at the product level.

---

## What read receipts are

By default, when Bob reads Alice's message, Alice sees a blue tick. This is a read receipt — confirmation that the other person has seen your message.

WhatsApp gives users the option to turn this off. Bob can go to Settings → Privacy → Read Receipts and disable it.

When Bob turns it off:
```
Alice sends Bob a message
Bob reads it
Alice sees: double grey tick ✓✓   (not blue)
```

Alice never knows Bob read her message.

---

## The mutual rule

This is where WhatsApp enforces a hard trade-off: **you cannot hide your own read receipts while seeing others'.**

```
Bob turns off read receipts
→ Alice cannot see blue tick on messages she sends Bob     ✓ (Bob wanted this)
→ Bob cannot see blue tick on messages he sends Alice      ✗ (Bob loses this)
```

Bob wanted privacy. He gets it — but at a cost. He no longer gets the satisfaction of seeing when Alice read his messages either.

---

## Why this rule exists

Without the mutual rule, the system would be asymmetric in a way that feels unfair to users:

```
Bob: read receipts OFF
  → Bob reads Alice's messages silently (Alice never knows)
  → Bob sees blue ticks when Alice reads his messages

Result: Bob has full information about Alice's reading habits.
        Alice has zero information about Bob's.
```

This is a surveillance asymmetry. One person can monitor the other without being monitored in return. WhatsApp's product decision is that this is not acceptable — privacy must be symmetric. If you want to hide, you also give up the ability to see.

---

## What users actually experience

Most users discover this trade-off the hard way — they turn off read receipts to avoid being pressured to reply, then realise they've also lost visibility into whether their own messages were read.

```
Bob turns off read receipts thinking:
  "Alice won't know I've seen her messages"   ✓ correct

Bob then notices:
  "Wait, I also can't see if Alice read mine"  ✗ unexpected cost
```

WhatsApp shows a warning in the settings screen: "If you turn off read receipts, you won't be able to see read receipts from other people."

> [!important] The mutual rule is a product decision, not a technical constraint
> There is nothing technically stopping WhatsApp from letting Bob hide his receipts while still showing him Alice's. The mutual rule is a deliberate product choice to enforce fairness.
