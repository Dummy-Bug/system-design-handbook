# When to Use Each Consistency Model

## The Decision Question

> [!question] Before picking a consistency model, ask: "What is the cost of showing stale data to the user?"

```
Stale data costs nothing    → Eventual consistency
Stale data is jarring       → Read-your-writes or Monotonic reads
Stale data breaks logic     → Causal consistency
Stale data costs money      → Strong consistency
Stale data has legal impact → Linearizability
```

---

## System → Model Decision Table

| System | Model | Reason |
|---|---|---|
| Amazon shopping cart | Eventual | Slight staleness fine, availability critical |
| Instagram like count | Eventual | Off by a few — nobody notices |
| Twitter/X timeline | Monotonic reads | Timeline must never jump backwards |
| Instagram — own profile | Read-your-writes | You must see your own posts immediately |
| WhatsApp messages | Causal | Replies must appear after original |
| Bank balance | Strong | Never show stale balance after transfer |
| Stock trading | Strong | Stale price = wrong trade |
| Google Spanner (financial) | Linearizable | Real-time global ordering required |

---

## Deep Dives

### Amazon Shopping Cart — Why Eventual?

Amazon's Dynamo paper (2007) made eventual consistency famous. The cart is the canonical example.

```
You add item to cart → write to primary
Your spouse also adds item simultaneously → write to another replica

Eventual consistency → both items merge into cart eventually ✓
Strong consistency   → one write blocks until all replicas confirm
                     → slower, cart errors out during network issues

Amazon's decision: availability > consistency for cart
A cart that's briefly stale = minor annoyance
A cart that errors out = lost sale
```

### WhatsApp — Why Not Linearizability?

```
WhatsApp has 2 billion users globally
Messages sent across continents

Linearizability → every message globally ordered by real time
               → every write waits for global quorum
               → high latency on every message
               → network partition → system goes down

Causal consistency → only related messages ordered (replies after originals)
                  → system stays available on poor networks
                  → 2 billion users can message even with spotty connection

Nobody notices that a message in one conversation isn't 
globally ordered with a message in another conversation.
```

### Bank Balance — Why Strong, Not Linearizable?

```
Strong consistency → every read sees latest write → sufficient for balance checks
Linearizability   → adds real-time clock ordering → needed only when
                    multiple systems need to agree on the exact moment
                    a transaction happened (audit trails, legal records)

Most banks → strong consistency is sufficient
Global financial systems (Spanner) → linearizability for cross-region ordering
```

---

## The Availability Tradeoff

> [!important] Stricter consistency = lower availability during network issues

```
Eventual      → always available, even during partition
Causal        → available, partition only affects ordering guarantees  
Strong        → may be unavailable during partition (must wait for quorum)
Linearizable  → most likely to be unavailable (strictest requirements)
```

This is the preview of CAP theorem — consistency and availability are in tension. You can't have both during a network partition.

```
WhatsApp chose: availability > strict consistency → causal
Bank chose:     consistency > availability        → strong
```

---

## Common Interview Trap

> [!warning] Don't always say "strong consistency" to sound safe

Strong consistency has real costs — higher latency, lower availability. Saying "I'd use strong consistency everywhere" shows you don't understand the tradeoffs.

The right answer is always:
*"I'd use [model] because [what staleness costs in this system] and [what availability requirement is]."*

```
Instagram feed → "Eventual — like counts being off by a few is fine,
                  we need maximum throughput at billions of operations/day"

WhatsApp       → "Causal — replies must appear after originals,
                  but full linearizability would hurt availability
                  for 2 billion users on varying network quality"

Bank transfer  → "Strong — stale balance after a transfer
                  could cause double-spending, correctness is non-negotiable"
```
